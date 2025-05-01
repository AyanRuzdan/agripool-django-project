from django.contrib import messages
from django.shortcuts import redirect, render, get_object_or_404
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from .forms import UserRegisterForm, ProduceForm
from .models import UserProfile, Produce, Transport
from django.http import HttpResponseForbidden
import requests


def logout_view(request):
    logout(request)
    return redirect('home')


def home(request):
    profile = request.user.userprofile if request.user.is_authenticated else None
    return render(request, 'core/home.html', {'profile': profile})


def register(request):
    if request.method == 'POST':
        form = UserRegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.set_password(form.cleaned_data['password'])
            user.save()
            UserProfile.objects.create(
                user=user, role=form.cleaned_data['role'])
            login(request, user)
            return redirect('dashboard')
    else:
        form = UserRegisterForm()
    return render(request, 'core/register.html', {'form': form})


@login_required
def dashboard(request):
    profile = request.user.userprofile

    # For farmers, get only their own produce
    produce = Produce.objects.filter(
        owner=request.user) if profile.role == 'farmer' else None

    # For drivers, get only the transports where they are the driver
    # This will show all transport routes to both farmers and drivers
    transport = Transport.objects.all()

    return render(request, 'core/dashboard.html', {
        'profile': profile,
        'produce': produce,
        'transport': transport
    })


@login_required
def create_produce(request):
    if request.method == 'POST':
        lat = request.POST.get('pickup_lat')
        lng = request.POST.get('pickup_lng')
        form = ProduceForm(request.POST)

        if not lat or not lng:
            messages.error(
                request, "Please select a pickup location on the map.")
            return render(request, 'core/create_produce.html', {'form': form})

        if form.is_valid():
            try:
                response = requests.get(
                    f'https://nominatim.openstreetmap.org/reverse?lat={lat}&lon={lng}&format=json',
                    headers={'User-Agent': 'AgriPoolApp'}
                )
                address = response.json().get('display_name', f"{lat}, {lng}")
            except Exception as e:
                address = f"{lat}, {lng}"
                messages.warning(
                    request, "Could not fetch location name. Coordinates will be saved instead.")

            produce = form.save(commit=False)
            produce.owner = request.user
            produce.pickup_location = address
            produce.save()
            messages.success(request, "Produce added successfully.")
            return redirect('dashboard')
    else:
        form = ProduceForm()

    return render(request, 'core/create_produce.html', {'form': form})


@login_required
def create_transport(request):
    if request.method == 'POST':
        route_start_lat = request.POST['route_start_lat']
        route_start_lng = request.POST['route_start_lng']
        route_end_lat = request.POST['route_end_lat']
        route_end_lng = request.POST['route_end_lng']
        capacity_total = request.POST['capacity_total']
        capacity_used = request.POST['capacity_used']
        scheduled_date = request.POST['scheduled_date']
        if capacity_used > capacity_total:
            return render(request, 'core/create_transport.html', {'error': 'Filled capacity cannot exceed total capacity.'})
        Transport.objects.create(
            driver=request.user,
            route_start_lat=route_start_lat,
            route_start_lng=route_start_lng,
            route_end_lat=route_end_lat,
            route_end_lng=route_end_lng,
            capacity_total=capacity_total,
            capacity_used=0,
            scheduled_date=scheduled_date
        )
        return redirect('dashboard')

    return render(request, 'core/create_transport.html')


@login_required
def delete_transport(request, transport_id):
    transport = get_object_or_404(Transport, id=transport_id)

    # Only the driver who created the transport can delete it
    if transport.driver != request.user:
        return HttpResponseForbidden("You are not allowed to delete this transport.")

    if request.method == 'POST':
        transport.delete()
        # Replace 'dashboard' with your dashboard view name
        return redirect('dashboard')

    return HttpResponseForbidden("Invalid request method.")


@login_required
def delete_produce(request, id):
    produce = get_object_or_404(Produce, id=id, owner=request.user)
    if request.method == 'POST':
        produce.delete()
        return redirect('dashboard')
    return HttpResponseForbidden()

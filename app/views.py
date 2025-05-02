import datetime

from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages

from .models import Event, User, Venue
from .forms import EventForm  
from .models import Event, User


def register(request):
    if request.method == "POST":
        email = request.POST.get("email")
        username = request.POST.get("username")
        is_organizer = request.POST.get("is-organizer") is not None
        password = request.POST.get("password")
        password_confirm = request.POST.get("password-confirm")

        errors = User.validate_new_user(email, username, password, password_confirm)

        if len(errors) > 0:
            return render(
                request,
                "accounts/register.html",
                {
                    "errors": errors,
                    "data": request.POST,
                },
            )
        else:
            user = User.objects.create_user(
                email=email, username=username, password=password, is_organizer=is_organizer
            )
            login(request, user)
            return redirect("home")

    return render(request, "accounts/register.html", {})


def login_view(request):
    if request.method == "POST":
        username = request.POST.get("username")
        password = request.POST.get("password")

        user = authenticate(request, username=username, password=password)

        if user is None:
            return render(
                request, "accounts/login.html", {"error": "Usuario o contraseña incorrectos"}
            )

        login(request, user)
        return redirect("home")

    return render(request, "accounts/login.html")


def home(request):
    user = request.user

    user_is_organizer = False
    if user.is_authenticated:
        user_is_organizer = user.is_organizer

    context = {
        "user_is_organizer": user_is_organizer,
    }
    return render(request, "home.html", context)



@login_required
def events(request):
    queryset = Event.objects.all().order_by("scheduled_at")
    if not request.user.is_organizer:
        queryset = queryset.filter(scheduled_at__gte=timezone.now())
    return render(request, "app/events.html", {"events": queryset})

@login_required
def event_detail(request, pk):
    event = get_object_or_404(Event.objects.select_related('venue'), pk=pk)
    return render(request, "app/event_detail.html", {"event": event})



@login_required
def event_delete(request, pk):
    if not request.user.is_organizer:
        messages.error(request, "No tienes permisos")
        return redirect("events")

    event = get_object_or_404(Event, pk=pk)
    if request.method == "POST":
        event.delete()
        messages.success(request, "Evento eliminado")
        return redirect("events")

    return render(request, "app/event_confirm_delete.html", {"event": event})


@login_required
def event_form(request, pk=None):
    event = get_object_or_404(Event, pk=pk) if pk else None
    if request.method == 'POST':
        form = EventForm(request.POST, instance=event, user=request.user)
        if form.is_valid():
            event = form.save(commit=False)
            event.organizer = request.user
            event.save()
            return redirect('event_detail', pk=event.pk)
    else:
        form = EventForm(instance=event, user=request.user)
    
    return render(request, 'app/event_form.html', {'form': form})



@login_required
def venue_list(request):
    if not request.user.is_organizer:
        return redirect('events')
    venues = Venue.objects.filter(created_by=request.user)
    return render(request, 'app/venue_list.html', {
        'venues': venues,
        'user_is_organizer': request.user.is_organizer
        })

def venue_form(request, id=None):
    if not request.user.is_organizer:
        return redirect('events')

    if request.method == 'POST':
        name = request.POST.get('name')
        address = request.POST.get('address')
        city = request.POST.get('city')
        capacity = request.POST.get('capacity')
        contact_info = request.POST.get('contact_info')

        if id:
            venue = get_object_or_404(Venue, pk=id)
            venue.update(
                name=name,
                address=address,
                city=city,
                capacity=capacity,
                contact_info=contact_info
            )
        else:
            success, errors = Venue.new(
                name=name,
                address=address,
                city=city,
                capacity=capacity,
                contact_info=contact_info,
                created_by=request.user
            )

            if not success:
                return render(request, 'app/venue_form.html', {
                    'errors': errors,
                    'venue_data': request.POST
                })

        return redirect('venue_list')

    venue = {}
    if id:
        venue = get_object_or_404(Venue, pk=id)
    
    return render(request, 'app/venue_form.html', {'venue': venue})

@login_required
def venue_delete(request, id):
    if not request.user.is_organizer:
        return redirect('events')
    
    venue = get_object_or_404(Venue, pk=id)
    if request.method == 'POST':
        venue.delete()
    return redirect('venue_list')

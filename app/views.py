import datetime
from django.contrib.auth import authenticate, login
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.contrib import messages
from datetime import timedelta 

from .models import RefundRequest, Ticket, Event, User
from .forms import RefundRequestForm


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
            return redirect("events")

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
        return redirect("events")

    return render(request, "accounts/login.html")


def home(request):
    return render(request, "home.html")


@login_required
def events(request):
    events = Event.objects.all().order_by("scheduled_at")
    return render(
        request,
        "app/events.html",
        {"events": events, "user_is_organizer": request.user.is_organizer},
    )


@login_required
def event_detail(request, id):
    event = get_object_or_404(Event, pk=id)
    return render(request, "app/event_detail.html", {"event": event})


@login_required
def event_delete(request, id):
    user = request.user
    if not user.is_organizer:
        return redirect("events")

    if request.method == "POST":
        event = get_object_or_404(Event, pk=id)
        event.delete()
        return redirect("events")

    return redirect("events")


@login_required
def event_form(request, id=None):
    user = request.user

    if not user.is_organizer:
        return redirect("events")

    if request.method == "POST":
        title = request.POST.get("title")
        description = request.POST.get("description")
        date = request.POST.get("date")
        time = request.POST.get("time")

        [year, month, day] = date.split("-")
        [hour, minutes] = time.split(":")

        scheduled_at = timezone.make_aware(
            datetime.datetime(int(year), int(month), int(day), int(hour), int(minutes))
        )

        if id is None:
            Event.new(title, description, scheduled_at, request.user)
        else:
            event = get_object_or_404(Event, pk=id)
            event.update(title, description, scheduled_at, request.user)

        return redirect("events")

    event = {}
    if id is not None:
        event = get_object_or_404(Event, pk=id)

    return render(
        request,
        "app/event_form.html",
        {"event": event, "user_is_organizer": request.user.is_organizer},
    )


@login_required
def update_refund_status(request, refund_id, action):
    """Unifica aprobación y rechazo en una sola vista"""
    refund = get_object_or_404(RefundRequest, id=refund_id)
    
    # Verificación de doble seguridad
    is_organizer = request.user.is_organizer
    is_own_event = refund.ticket.event.organizer == request.user
    
    if is_organizer and is_own_event:
        if action == 'approve':
            refund.status = 'approved'
            msg_type = messages.success
            msg_text = f"Reembolso #{refund_id} aprobado ✅"
        elif action == 'reject':
            refund.status = 'rejected'
            msg_type = messages.error
            msg_text = f"Reembolso #{refund_id} rechazado ❌"
        else:
            return redirect('manage_refunds')
        
        refund.save()
        msg_type(request, msg_text)
    
    return redirect('manage_refunds')

# Versión mejorada de manage_refunds
@login_required
def manage_refunds(request):
    if not request.user.is_organizer:
        return redirect('home')
    
    # Consulta BASE (todas las solicitudes del organizador)
    base_refunds = RefundRequest.objects.filter(
        ticket__event__organizer=request.user
    ).select_related('ticket__event', 'user')
    
    # Calcular conteos ANTES de filtrar por estado
    status_counts = {
        'pending': base_refunds.filter(status='pending').count(),
        'approved': base_refunds.filter(status='approved').count(),
        'rejected': base_refunds.filter(status='rejected').count(),
    }
    
    # Aplicar filtro de estado (si existe)
    status_filter = request.GET.get('status')
    if status_filter in ['approved', 'rejected', 'pending']:
        refunds = base_refunds.filter(status=status_filter)
    else:
        refunds = base_refunds
    
    return render(request, 'refunds/manage.html', {
        'refunds': refunds,
        'status_counts': status_counts,
    })

# Versión segura de refund_detail
@login_required
def refund_detail(request, refund_id):
    """Incluye validación de permisos"""
    refund = get_object_or_404(RefundRequest, id=refund_id)
    
    # Verifica si el usuario es dueño u organizador
    if not (request.user == refund.user or request.user.is_organizer):
        return redirect('home')
    
    return render(request, 'refunds/detail.html', {
        'refund': refund,
        'can_edit': request.user.is_organizer
    })

@login_required
def request_refund(request, ticket_id):
    """
    Vista para que usuarios regulares soliciten reembolsos
    """
    ticket = get_object_or_404(Ticket, id=ticket_id, user=request.user)
    
    # Validación de tiempo restante
    tiempo_restante = ticket.event.scheduled_at - timezone.now()
    if tiempo_restante < timedelta(hours=48):
        messages.error(request, "⚠️ No se permiten reembolsos a menos de 48 horas del evento")
        return redirect('event_detail', id=ticket.event.id)

    if request.method == 'POST':
        form = RefundRequestForm(request.POST)
        if form.is_valid():
            # Crear reembolso
            refund = form.save(commit=False)
            refund.ticket = ticket
            refund.user = request.user
            
            # Calcular monto automáticamente
            refund.calcular_monto()  # Usando el método del modelo
            refund.save()
            
            messages.success(request, "✅ Solicitud creada exitosamente")
            return redirect('refund_detail', refund_id=refund.id)
    else:
        form = RefundRequestForm()

    return render(request, 'refunds/request.html', {
    'form': form,
    'ticket': ticket,
    'policy_message': "Puedes solicitar reembolsos hasta 48 horas antes del evento."
})
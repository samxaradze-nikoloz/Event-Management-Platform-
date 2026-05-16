from django.shortcuts import render, get_object_or_404, redirect
from django.db.models import Count, Q
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.views.decorators.http import require_http_methods
from .models import Event, Category, Registration, Review, EventMedia, Tag

def event_list(request):
    events = Event.objects.filter(status='published').select_related('organizer', 'category').prefetch_related('registrations', 'tags')
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    event_type = request.GET.get('event_type', '')
    category = request.GET.get('category', '')

    if search:
        events = events.filter(Q(title__icontains=search) | Q(description__icontains=search))
    if status:
        events = events.filter(status=status)
    if event_type:
        events = events.filter(event_type=event_type)
    if category:
        events = events.filter(category_id=category)

    return render(request, 'events/list.html', {
        'events': events,
        'categories': Category.objects.all(),
    })

def event_detail(request, pk):
    event = get_object_or_404(Event, pk=pk)
    reviews = event.reviews.select_related('user').all()
    user_registration = None
    user_has_reviewed = False

    if request.user.is_authenticated:
        user_registration = Registration.objects.filter(
            user=request.user, event=event
        ).first()
        user_has_reviewed = Review.objects.filter(
            user=request.user, event=event
        ).exists()

    return render(request, 'events/detail.html', {
        'event': event,
        'reviews': reviews,
        'user_registration': user_registration,
        'user_has_reviewed': user_has_reviewed,
    })

@login_required(login_url='/accounts/login/')
def create_event(request):
    if request.method == 'POST':
        try:
            # Get form data
            title = request.POST.get('title')
            description = request.POST.get('description')
            category_id = request.POST.get('category')
            status = request.POST.get('status', 'draft')
            event_type = request.POST.get('event_type', 'online')
            start_date = request.POST.get('start_date')
            end_date = request.POST.get('end_date')
            location = request.POST.get('location')
            max_attendees = request.POST.get('max_attendees')
            tags_ids = request.POST.getlist('tags')
            media_file = request.FILES.get('media')
            
            
            if not all([title, description, start_date, end_date, max_attendees]):
                messages.error(request, 'Please fill in all required fields.')
                return redirect('create-event')
            
            
            if request.user.role != 'organizer':
                messages.error(request, 'Only organizers can create events.')
                return redirect('web-event-list')
            
            
            event = Event.objects.create(
                title=title,
                description=description,
                organizer=request.user,
                category_id=category_id if category_id else None,
                status=status,
                event_type=event_type,
                start_date=start_date,
                end_date=end_date,
                location=location if location else None,
                max_attendees=int(max_attendees),
            )
            
            
            if tags_ids:
                event.tags.set(tags_ids)
            
           
            if media_file:
                EventMedia.objects.create(
                    event=event,
                    file=media_file
                )
            
            messages.success(request, f'Event "{event.title}" created successfully!')
            
            
            if status == 'published':
                return redirect('web-event-detail', pk=event.id)
            else:
                return render(request, 'events/success.html', {'event': event})
        
        except Exception as e:
            messages.error(request, f'Error creating event: {str(e)}')
            return redirect('create-event')
    
  
    return render(request, 'events/create.html', {
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    })

@login_required(login_url='/accounts/login/')
@require_http_methods(["POST"])
def register_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    

    existing_registration = Registration.objects.filter(
        user=request.user, event=event
    ).first()
    
    if existing_registration:
        messages.warning(request, 'You are already registered for this event.')
        return redirect('web-event-detail', pk=event.id)
    

    if event.is_full:
        messages.error(request, 'This event is full.')
        return redirect('web-event-detail', pk=event.id)

    registration = Registration.objects.create(
        user=request.user,
        event=event,
        status='confirmed'
    )
    
    messages.success(request, f'Successfully registered for "{event.title}"!')
    return render(request, 'events/registration_success.html', {
        'event': event,
        'registration': registration,
    })

@login_required(login_url='/accounts/login/')
@require_http_methods(["POST"])
def cancel_registration(request, pk, reg_id):
    event = get_object_or_404(Event, pk=pk)
    registration = get_object_or_404(Registration, pk=reg_id, user=request.user, event=event)
    
    event_title = event.title
    registration.delete()
    
    messages.success(request, f'Cancelled registration for "{event_title}".')
    return redirect('web-event-detail', pk=event.id)

@login_required(login_url='/accounts/login/')
def my_registrations(request):
    registrations = Registration.objects.filter(
        user=request.user
    ).select_related('event').order_by('-registered_at')
    
    return render(request, 'events/my_registrations.html', {
        'registrations': registrations,
        'total_events': registrations.count(),
    })

@login_required(login_url='/accounts/login/')
def my_events(request):
    if request.user.role != 'organizer':
        messages.error(request, 'Only organizers can view this page.')
        return redirect('web-event-list')
    
    events = Event.objects.filter(organizer=request.user).order_by('-created_at')
    draft_count = events.filter(status='draft').count()
    published_count = events.filter(status='published').count()
    
    return render(request, 'events/my_events.html', {
        'events': events,
        'draft_count': draft_count,
        'published_count': published_count,
    })

@login_required(login_url='/accounts/login/')
def edit_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.user != event.organizer:
        messages.error(request, 'You can only edit your own events.')
        return redirect('web-event-detail', pk=event.id)
    
    if request.method == 'POST':
        try:
            event.title = request.POST.get('title', event.title)
            event.description = request.POST.get('description', event.description)
            event.category_id = request.POST.get('category') or None
            event.status = request.POST.get('status', event.status)
            event.event_type = request.POST.get('event_type', event.event_type)
            event.start_date = request.POST.get('start_date', event.start_date)
            event.end_date = request.POST.get('end_date', event.end_date)
            event.location = request.POST.get('location') or None
            event.max_attendees = int(request.POST.get('max_attendees', event.max_attendees))
            
            event.save()
            
            tags_ids = request.POST.getlist('tags')
            if tags_ids:
                event.tags.set(tags_ids)
            
            if request.FILES.get('media'):
                EventMedia.objects.filter(event=event).delete()
                EventMedia.objects.create(
                    event=event,
                    file=request.FILES.get('media')
                )
            
            messages.success(request, 'Event updated successfully!')
            return redirect('web-event-detail', pk=event.id)
        except Exception as e:
            messages.error(request, f'Error updating event: {str(e)}')
    
    return render(request, 'events/edit_event.html', {
        'event': event,
        'categories': Category.objects.all(),
        'tags': Tag.objects.all(),
    })

@login_required(login_url='/accounts/login/')
@require_http_methods(["POST"])
def delete_event(request, pk):
    event = get_object_or_404(Event, pk=pk)
    
    if request.user != event.organizer:
        messages.error(request, 'You can only delete your own events.')
        return redirect('web-event-detail', pk=event.id)
    
    event_title = event.title
    event.delete()
    
    messages.success(request, f'Event "{event_title}" deleted successfully.')
    return redirect('web-event-list')
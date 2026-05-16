from django.shortcuts import render, get_object_or_404
from .models import Event, Category, Registration, Review

def event_list(request):
    events = Event.objects.filter(status='published').select_related('organizer', 'category')
    search = request.GET.get('search', '')
    status = request.GET.get('status', '')
    event_type = request.GET.get('event_type', '')
    category = request.GET.get('category', '')

    if search:
        events = events.filter(title__icontains=search) | \
                 events.filter(description__icontains=search)
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


from django.shortcuts import render

def create_event(request):
    return render(request, 'events/create.html')
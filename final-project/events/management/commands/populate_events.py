from django.core.management.base import BaseCommand
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from events.models import Event, Category, Tag

User = get_user_model()

class Command(BaseCommand):
    help = 'Populate database with test events'

    def handle(self, *args, **options):
        # Create or get categories
        tech, _ = Category.objects.get_or_create(
            slug='technology',
            defaults={'name': 'Technology'}
        )
        business, _ = Category.objects.get_or_create(
            slug='business',
            defaults={'name': 'Business'}
        )
        
        # Create or get tags
        python, _ = Tag.objects.get_or_create(name='Python')
        django, _ = Tag.objects.get_or_create(name='Django')
        web, _ = Tag.objects.get_or_create(name='Web Development')
        
        # Get or create test organizer
        organizer, _ = User.objects.get_or_create(
            username='organizer',
            defaults={
                'email': 'organizer@example.com',
                'role': 'organizer',
                'first_name': 'Test',
                'last_name': 'Organizer'
            }
        )
        
        # Set password if it's a new user
        if not organizer.has_usable_password():
            organizer.set_password('testpass123')
            organizer.save()
        
        # Create test events
        now = timezone.now()
        
        events_data = [
            {
                'title': 'Python Conference 2025',
                'description': 'Join us for the annual Python Conference featuring talks from industry experts, workshops, and networking sessions.',
                'category': tech,
                'event_type': 'online',
                'start_date': now + timedelta(days=30),
                'end_date': now + timedelta(days=30, hours=8),
                'location': 'Online via Zoom',
                'max_attendees': 500,
                'status': 'published',
                'tags': [python, django],
            },
            {
                'title': 'Django Workshop - Beginner',
                'description': 'Learn Django framework from scratch. This hands-on workshop is perfect for beginners who want to build web applications.',
                'category': tech,
                'event_type': 'offline',
                'start_date': now + timedelta(days=15),
                'end_date': now + timedelta(days=15, hours=4),
                'location': 'Tbilisi Innovation Hub, Georgia',
                'max_attendees': 50,
                'status': 'published',
                'tags': [django, web],
            },
            {
                'title': 'Tech Startup Meetup',
                'description': 'Monthly meetup for tech entrepreneurs and startup founders. Network, share ideas, and find your co-founders.',
                'category': business,
                'event_type': 'offline',
                'start_date': now + timedelta(days=7),
                'end_date': now + timedelta(days=7, hours=2),
                'location': 'Co-working Space, Tbilisi',
                'max_attendees': 100,
                'status': 'published',
                'tags': [web],
            },
            {
                'title': 'Web Development Bootcamp',
                'description': 'Intensive 4-week bootcamp covering HTML, CSS, JavaScript, and React. Build real-world projects and land your first job.',
                'category': tech,
                'event_type': 'offline',
                'start_date': now + timedelta(days=45),
                'end_date': now + timedelta(days=73),
                'location': 'Tech Academy, Tbilisi',
                'max_attendees': 30,
                'status': 'published',
                'tags': [web],
            },
        ]
        
        for event_data in events_data:
            tags = event_data.pop('tags')
            event, created = Event.objects.get_or_create(
                title=event_data['title'],
                organizer=organizer,
                defaults=event_data
            )
            event.tags.set(tags)
            
            status = 'Created' if created else 'Already exists'
            self.stdout.write(f'{status}: {event.title}')
        
        self.stdout.write(self.style.SUCCESS('Successfully populated database with test events'))

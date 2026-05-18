from django.core.management.base import BaseCommand
from events.models import Category, Tag

class Command(BaseCommand):
    help = 'Seed categories and tags'

    def handle(self, *args, **kwargs):
        categories = [
            ('Technology', 'technology'),
            ('Design', 'design'),
            ('Business', 'business'),
            ('Science', 'science'),
            ('Art & Culture', 'art-culture'),
            ('Music', 'music'),
            ('Sports', 'sports'),
            ('Education', 'education'),
            ('Health & Wellness', 'health-wellness'),
            ('Gaming', 'gaming'),
        ]

        for name, slug in categories:
            cat, created = Category.objects.get_or_create(slug=slug, defaults={'name': name})
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Category [{status}]: {name}')

        tags = [
            'Python', 'Django', 'JavaScript', 'React', 'AI', 'Machine Learning',
            'Startup', 'Networking', 'Workshop', 'Conference', 'Hackathon',
            'Online', 'Free', 'Beginner', 'Advanced', 'Georgian', 'International',
        ]

        for tag_name in tags:
            tag, created = Tag.objects.get_or_create(name=tag_name)
            status = 'created' if created else 'exists'
            self.stdout.write(f'  Tag [{status}]: {tag_name}')

        self.stdout.write(self.style.SUCCESS('\nDone! All categories and tags seeded.'))
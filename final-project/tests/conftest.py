import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

User = get_user_model()


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def organizer(db):
    return User.objects.create_user(
        username='organizer1', email='org@test.com',
        password='pass1234', role='organizer'
    )


@pytest.fixture
def attendee(db):
    return User.objects.create_user(
        username='attendee1', email='att@test.com',
        password='pass1234', role='attendee'
    )


@pytest.fixture
def organizer_client(api_client, organizer):
    api_client.force_authenticate(user=organizer)
    return api_client


@pytest.fixture
def attendee_client(api_client, attendee):
    api_client.force_authenticate(user=attendee)
    return api_client


@pytest.fixture
def event(db, organizer):
    from events.models import Event
    return Event.objects.create(
        title='Test Event',
        description='Test description',
        organizer=organizer,
        status='published',
        event_type='online',
        max_attendees=10,
        start_date='2025-12-01 10:00:00+00:00',
        end_date='2025-12-01 18:00:00+00:00',
    )


@pytest.fixture
def full_event(db, organizer):
    from events.models import Event
    return Event.objects.create(
        title='Full Event',
        description='No spots left',
        organizer=organizer,
        status='published',
        event_type='online',
        max_attendees=0,
        start_date='2025-12-01 10:00:00+00:00',
        end_date='2025-12-01 18:00:00+00:00',
    )


@pytest.fixture
def confirmed_registration(db, attendee, event):
    from events.models import Registration
    return Registration.objects.create(user=attendee, event=event, status='confirmed')
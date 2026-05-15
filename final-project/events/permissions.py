from rest_framework.permissions import BasePermission, SAFE_METHODS
from events.models import Registration


class IsOrganizer(BasePermission):
    def has_permission(self, request, view):
        return bool(request.user and request.user.is_authenticated and request.user.role == 'organizer')


class IsOwnerOrReadOnly(BasePermission):
    def has_object_permission(self, request, view, obj):
        if request.method in SAFE_METHODS:
            return True
        return getattr(obj, 'organizer', None) == request.user


class IsConfirmedAttendee(BasePermission):
    def has_permission(self, request, view):
        if not request.user or not request.user.is_authenticated:
            return False
        event_id = view.kwargs.get('event_pk')
        return Registration.objects.filter(
            user=request.user,
            event_id=event_id,
            status='confirmed'
        ).exists()

from rest_framework.throttling import UserRateThrottle


class RegistrationBurstThrottle(UserRateThrottle):
    scope = 'registration_burst'
import pytz
from django.conf import settings
from django.utils import timezone


class TimezoneMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        if request.user.is_authenticated and hasattr(
            request.user.useraccount, "timezone"
        ):
            user_tz = request.user.useraccount.timezone
        elif settings.TIME_ZONE:
            user_tz = pytz.timezone(settings.TIME_ZONE)
        else:
            user_tz = None

        if user_tz:
            timezone.activate(user_tz)
        else:
            timezone.deactivate()

        return self.get_response(request)

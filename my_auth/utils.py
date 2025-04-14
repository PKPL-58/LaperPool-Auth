from functools import wraps

from django.conf import settings
from django.utils.module_loading import import_string

from django_ratelimit import ALL, UNSAFE
from django_ratelimit.exceptions import Ratelimited
from django_ratelimit.core import is_ratelimited
from django.contrib import messages
from django.shortcuts import redirect
import logging

__all__ = ['ratelimit']
logger = logging.getLogger(__name__)

def login_ratelimit(group=None, key=None, rate=None, method=ALL, block=True):
    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kw):
            old_limited = getattr(request, 'limited', False)
            ratelimited = is_ratelimited(request=request, group=group, fn=fn,
                                         key=key, rate=rate, method=method,
                                         increment=True)
            request.limited = ratelimited or old_limited

            # Log semua headers 
            logger.debug("Headers dari request:")
            for header, value in request.META.items():
                logger.debug(f"{header}: {value}")

            if ratelimited and block:
                logger.warning(f"Rate limit tercapai untuk pengguna: {request.POST.get('username')} "
                               f"dengan key: {key}.")
                messages.error(request, "Anda telah melampaui batas percobaan login. Silakan coba lagi nanti.")
                return redirect('auth:login')
            return fn(request, *args, **kw)
        return _wrapped
    return decorator
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

def login_ratelimit(group=None, rate=None, method=ALL, block=True):
    """
    Rate limiting berdasarkan IP dan username.
    """
    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kw):
            old_limited = getattr(request, 'limited', False)

            # Ambil username dari POST
            username = request.POST.get('username', '').strip()

            # Rate limit berdasarkan IP dari header HTTP_X_ORIGINAL_FORWARDED_FOR
            if request.META.get('HTTP_X_ORIGINAL_FORWARDED_FOR'):
                ip_key = 'header:x-original-forwarded-for'
                ip_limited = is_ratelimited(
                    request=request,
                    group=group,
                    fn=fn,
                    key=ip_key,
                    rate=rate,
                    method=method,
                    increment=True
                )
            else:
                ip_limited = False

            # Rate limit berdasarkan username
            username_key = f'post:username'
            username_limited = is_ratelimited(
                request=request,
                group=group,
                fn=fn,
                key=username_key,
                rate=rate,
                method=method,
                increment=True
            )

            # Gabungkan hasil rate limiting
            ratelimited = ip_limited or username_limited
            request.limited = ratelimited or old_limited

            logger.debug(f"Username: {username}, IP Limited: {ip_limited}, Username Limited: {username_limited}")

            if ratelimited and block:
                logger.warning(f"Rate limit tercapai untuk pengguna: {username}, dengan IP: {request.META.get('HTTP_X_ORIGINAL_FORWARDED_FOR')}")
                messages.error(request, "Anda telah melampaui batas percobaan login. Silakan coba lagi nanti.")
                return redirect('auth:login')

            return fn(request, *args, **kw)
        return _wrapped
    return decorator
from functools import wraps

from django.conf import settings
from django.utils.module_loading import import_string

from django_ratelimit import ALL, UNSAFE
from django_ratelimit.exceptions import Ratelimited
from django_ratelimit.core import is_ratelimited
from django.contrib import messages
from django.shortcuts import redirect

__all__ = ['ratelimit']


def login_ratelimit(group=None, key=None, rate=None, method=ALL, block=True):
    def decorator(fn):
        @wraps(fn)
        def _wrapped(request, *args, **kw):
            old_limited = getattr(request, 'limited', False)
            ratelimited = is_ratelimited(request=request, group=group, fn=fn,
                                         key=key, rate=rate, method=method,
                                         increment=True)
            request.limited = ratelimited or old_limited
            if ratelimited and block:
                messages.error(request, "Anda telah melampaui batas percobaan login. Silakan coba lagi nanti.")
                return redirect('auth:login')
            return fn(request, *args, **kw)
        return _wrapped
    return decorator
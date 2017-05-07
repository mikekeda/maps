from django.core.cache import cache
from django.conf import settings


def simple_cache_page(cache_timeout, per_user=False):
    """
    Decorator for views that tries getting the page from the cache and
    populates the cache if the page isn't in the cache yet.

    The cache is keyed by view name and arguments.
    """
    def _dec(func):
        def _new_func(*args, **kwargs):
            key = ''
            if per_user:
                request, = args
                key += str(request.user.id) if request.user.id else '0'
                key += ':'
            key += func.__name__
            if kwargs:
                key += ':' + ':'.join([kwargs[key] for key in kwargs])

            response = cache.get(key)
            if not response or settings.DEBUG:
                response = func(*args, **kwargs)
                cache.set(key, response, cache_timeout)
            return response
        return _new_func
    return _dec

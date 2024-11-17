import hashlib
from urllib.parse import urlencode

from django import template
from django.utils.safestring import mark_safe
from django.conf import settings

register = template.Library()


@register.filter
def gravatar_url(user):
    email = user.email.lower().encode('utf-8')
    default = 'mm'
    size = 40
    url = 'https://www.gravatar.com/avatar/{sha256}?{params}'.format(
        sha256=hashlib.sha256(email).hexdigest(),
        params=urlencode({'d': default, 's': str(size)})
    )
    return url

@register.filter
def gravatar(user):
    url = gravatar_url(user)
    return mark_safe(f'')
from django.shortcuts import redirect
from django.conf import settings

from .utilities import get_MSAL_user

ms_identity_web = settings.MS_IDENTITY_WEB


@ms_identity_web.login_required
def check_user(request):
    user = get_MSAL_user(request, ms_identity_web)
    if user.is_superuser:
        return redirect('event:admin-dash')
    else:
        return redirect('event:user-dash')

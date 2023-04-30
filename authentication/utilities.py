import requests
import json
# from django.shortcuts import redirect
# from .models import User


def acquireUserDetails(identity):
    identity.acquire_token_silently()
    graph = 'https://graph.microsoft.com/v1.0/me'
    authZ = f'Bearer {identity.id_data._access_token}'
    results = requests.get(graph, headers={'Authorization': authZ}).text
    return json.loads(results)


# def get_user_from_request(request):
#     uid = request.identity_context_data._id_token_claims['oid']
#     return User.objects.get(ms_id=uid)

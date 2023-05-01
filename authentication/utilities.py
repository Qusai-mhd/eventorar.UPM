import requests
import json
from .models import CustomUser


def acquireUserDetails(identity):
    identity.acquire_token_silently()
    graph = 'https://graph.microsoft.com/v1.0/me'
    authZ = f'Bearer {identity.id_data._access_token}'
    results = requests.get(graph, headers={'Authorization': authZ}).text
    return json.loads(results)


def get_user_from_db(request, identity):

    try:  # Try look for the user in the DB
        uid = request.identity_context_data._id_token_claims['oid']
        return CustomUser.objects.get(ms_id=uid)

    except CustomUser.DoesNotExist:  # If not found, create a new user and return it
        userProfile = acquireUserDetails(identity)
        user = CustomUser(email=userProfile['mail'], job_title=userProfile['jobTitle'],
                          first_name=userProfile['givenName'], last_name=userProfile['surname'],
                          ms_id=userProfile['id'], gender='M')  # TODO: Change the Gender
        user.save()
        return user

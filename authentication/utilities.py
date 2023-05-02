import requests
import json
from .models import CustomUser
from django.contrib.auth.models import Group


def acquireUserDetails(identity):
    identity.acquire_token_silently()
    graph = 'https://graph.microsoft.com/v1.0/me'
    authZ = f'Bearer {identity.id_data._access_token}'
    results = requests.get(graph, headers={'Authorization': authZ}).text
    return json.loads(results)


def get_MSAL_user(request, identity):

    try:  # Try look for the user in the DB
        uid = request.identity_context_data._id_token_claims['oid']
        return CustomUser.objects.get(ms_id=uid)

    except CustomUser.DoesNotExist:  # If not found, create a new user and return it
        userProfile = acquireUserDetails(identity)
        user = CustomUser(email=userProfile['mail'], job_title=userProfile['jobTitle'],
                          first_name=userProfile['givenName'], last_name=userProfile['surname'],
                          ms_id=userProfile['id'])
        user.save()
        add_user_to_college_group(user.job_title,user.ms_id)
        return user


def add_user_to_college_group(job_title,user_id):
    user=CustomUser.objects.get(ms_id=user_id)
    group_all=Group.objects.get(name='All Colleges')
    if job_title == 'BSFC' or 'BSCSE' or 'BSCAI':
        group=Group.objects.get(name='College Of Computer and Cyber Sciences')
        user.groups.add(group)
    elif job_title == 'BSELE' or 'BSARC' or 'BSCVL' or 'BSIND':
        group=Group.objects.get(name='College Of Engineering')
        user.groups.add(group)
    elif job_title == 'BAMGT' or 'BAACC' or 'BSHOS' or 'PENG' or 'PBUS' or 'BAMKT':
        group=Group.objects.get(name='College Of Business Administration')
        user.groups.add(group)
    elif job_title == 'PCS':
        group=Group.objects.get(name='Prep Year')
        user.groups.add(group)
    user.groups.add(group_all)

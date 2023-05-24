import requests
from .models import CustomUser
from django.contrib.auth.models import Group


def call_MS_graph(identity, endpoint):
    identity.acquire_token_silently()
    authZ = f'Bearer {identity.id_data._access_token}'
    results = requests.get(endpoint, headers={'Authorization': authZ}).json()
    return results


def get_MSAL_user_old(request, identity):
    try:  # Try look for the user in the DB
        uid = request.identity_context_data._id_token_claims['oid']
        return CustomUser.objects.get(ms_id=uid)

    except CustomUser.DoesNotExist:  # If not found, create a new user and return it

        me_endpoint = 'https://graph.microsoft.com/v1.0/me'
        userProfile = call_MS_graph(identity, endpoint=me_endpoint)
        user = CustomUser(email=userProfile['mail'], job_title=userProfile['jobTitle'],
                          first_name=userProfile['givenName'], last_name=userProfile['surname'],
                          ms_id=userProfile['id'])
        user.save()
        add_user_to_college_group(user)
        return user


def get_MSAL_user(request, identity):
    uid = request.identity_context_data._id_token_claims['oid']

    try:  # Try look for the user in the DB
        return CustomUser.objects.get(ms_id=uid)

    except CustomUser.DoesNotExist:  # If not found, create a new user and return it

        me_beta_endpoint = 'https://graph.microsoft.com/beta/me/profile'
        userProfile = call_MS_graph(identity, me_beta_endpoint)

        email = userProfile['emails'][0]['address']
        job_title = userProfile['positions'][0]['detail']['jobTitle']
        first_name = userProfile['names'][0]['first']
        last_name = userProfile['names'][0]['last']

        try:
            gender = userProfile['positions'][0]['detail']['company']['address']['postalCode'].upper()
        except KeyError:
            gender = None
        gender = gender if (gender in ('M', 'F')) else None

        user = CustomUser(email=email, job_title=job_title,
                          first_name=first_name, last_name=last_name,
                          gender=gender, ms_id=uid)
        user.save()
        add_user_to_college_group(user)
        return user


def add_user_to_college_group(user):
    group_all=Group.objects.get(name='All Colleges')
    job_title = user.job_title
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

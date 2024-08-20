import os, requests, json
from django.http import HttpResponse, JsonResponse
from django.shortcuts import render, redirect
from django.views.decorators.csrf import csrf_exempt
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests
from .models import NewUser
from urllib.parse import urlencode
from midfield import settings
from django.views import View
from user_apps.models import user_app
from user_apps.utils import get_apps_details

@csrf_exempt
def sign_in(request):
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        "redirect_uri": request.build_absolute_uri('/auth-receiver'),
        "response_type": "code",
        "scope": "openid email profile",
        "access_type": "offline",
        "prompt": "select_account"
    }
    return redirect(f"{google_auth_url}?{urlencode(params)}")


@csrf_exempt
def auth_receiver(request):
    """
    Google calls this URL after the user has signed in with their Google account.
    """
    code = request.GET.get('code')
    if not code:
        return HttpResponse("Authorization code is missing", status=400)

    token_url = "https://oauth2.googleapis.com/token"
    data = {
        "code": code,
        "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
        "redirect_uri": request.build_absolute_uri('/auth-receiver'),
        "grant_type": "authorization_code",
    }

    # Use requests to make the POST request to Google's token endpoint
    token_response = requests.post(token_url, data=data)
    if token_response.status_code != 200:
        return HttpResponse("Failed to retrieve tokens", status=400)

    token_response_data = token_response.json()
    id_token_str = token_response_data.get('id_token')

    if not id_token_str:
        return HttpResponse("ID token is missing", status=400)

    try:
        user_data = id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        )
    except ValueError:
        return HttpResponse("Invalid token", status=403)

    # Print and save user data
    print(f"User's Name: {user_data['name']}")
    print(f"User's Email: {user_data['email']}")
    print(f"User's Google ID: {user_data['sub']}")
    print(f"User's Picture URL: {user_data.get('picture', 'No picture URL')}")

    new_user, created = NewUser.objects.get_or_create(
        google_id=user_data['sub'],
        defaults={
            'email': user_data['email'],
            'name': user_data['name'],
            'picture_url': user_data.get('picture', ''),
            "authkey" : user_data['aud']
        }
    )

    request.session['user_data'] = user_data
    return redirect('sign_in')


def sign_out(request):
    del request.session['user_data']
    return redirect('sign_in')



class dashboard(View):
    
    def get(self, request):
        req_data= json.loads(request.body)
        if not ("google_id" or "email" ) in req_data.keys() :
            return JsonResponse({'error': "there is not google id or email"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'])
        if not user :
            user =  NewUser.objects.filter(email = req_data['email']) 
            if not user:
                return JsonResponse({'error': "No user found"}, status=400)
        
        user= user.first()
        
        data = {
            "google_id" : user.google_id,
            "email" : user.email,
            "name" : user.name,
            "profile_url" : user.picture_url,
            "app_details" : get_apps_details(user)
        }
        return JsonResponse({'success': "successfully get the data","data" : data,'error': ''}, status=201)

class getauthkey(View):
    
    def get(self, request):
        req_data= json.loads(request.body)
        if not ("google_id" or "email" ) in req_data.keys() :
            return JsonResponse({'error': "there is not google id or email"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'])
        if not user :
            user =  NewUser.objects.filter(email = req_data['email']) 
            if not user:
                return JsonResponse({'error': "No user found"}, status=400)
        
        user= user.first()
        
        return JsonResponse({'success': "successfully get the data","authkey" : user.authkey,'error': ''}, status=201)
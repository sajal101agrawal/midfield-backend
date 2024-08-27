import os, requests, json, secrets
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
from django.utils.crypto import get_random_string



# @csrf_exempt
# def sign_in(request,auth_code):
#     google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
#     params = {
#         "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
#         "redirect_uri": request.build_absolute_uri('/auth-receiver/'),
#         "response_type": "code",
#         "scope": "openid email profile",
#         "access_type": "offline",
#         "prompt": "select_account"
#     }
#     return redirect(f"{google_auth_url}?{urlencode(params)}")


@csrf_exempt
def sign_in(request):
    google_auth_url = "https://accounts.google.com/o/oauth2/v2/auth"
    params = {
        "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
        "redirect_uri": request.build_absolute_uri('/auth-receiver/'),
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
        "redirect_uri": request.build_absolute_uri('/auth-receiver/'),
        "grant_type": "authorization_code",
    }

    # Get tokens from Google
    token_response = requests.post(token_url, data=data)
    if token_response.status_code != 200:
        return HttpResponse("Failed to retrieve tokens", status=400)

    token_response_data = token_response.json()
    id_token_str = token_response_data.get('id_token')
    refresh_token = token_response_data.get('refresh_token')  # Google-issued refresh token

    if not id_token_str:
        return HttpResponse("ID token is missing", status=400)

    # Verify the ID token
    try:
        user_data = id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        )
    except ValueError:  # Token is invalid or expired
        if not refresh_token:
            return HttpResponse("Refresh token is missing", status=400)

        # Try to refresh the token using the refresh token
        refresh_data = {
            "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        refresh_response = requests.post(token_url, data=refresh_data)
        if refresh_response.status_code != 200:
            return HttpResponse("Failed to refresh tokens", status=400)

        refreshed_tokens = refresh_response.json()
        id_token_str = refreshed_tokens.get('id_token')

        if not id_token_str:
            return HttpResponse("Failed to refresh ID token", status=400)

        # Re-verify the ID token after refreshing
        user_data = id_token.verify_oauth2_token(
            id_token_str, google_requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        )

    # Store user data and tokens in the session
    request.session['user_data'] = user_data
    request.session['auth_key'] = id_token_str
    request.session['refresh_token'] = refresh_token  # Store refresh token for future use

    # Optionally store tokens in the database
    new_user = NewUser.objects.get(
        email = user_data['email'],
        google_id =  user_data['sub'],
    )
    
    if not new_user :
        
        new_user = NewUser.objects.create(
            google_id=user_data['sub'],
            email = user_data['email'],
            name = user_data['name'],
            picture_url = user_data.get('picture', ''),
            authkey = id_token_str,
            refresh_token = refresh_token
        )
    else :
        new_user.authkey = id_token_str
        new_user.refresh_token = refresh_token
        new_user.save()
        
    main_data = {
        "auth-token" : id_token_str,
        "refresh-token" : refresh_token,
        "user-data" : user_data
    }
    
    return JsonResponse({"data": main_data}, status=200)
    
def refresh_auth_token(request):
    """
    Validates the given auth token and refreshes it if it's expired.
    """
    token_url = "https://oauth2.googleapis.com/token"
    
    auth_token = request.GET.get('auth-token')
    if not auth_token:
        return HttpResponse("Auth token is missing", status=400)
    
    refresh_token = request.GET.get('refresh-token')
    if not refresh_token:
        return HttpResponse("Refresh token is missing", status=400)
    
    try:
        user_data = id_token.verify_oauth2_token(
            auth_token, google_requests.Request(), settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY
        )
    except ValueError: 
        if not refresh_token:
            return HttpResponse("Refresh token is missing", status=400)

        # Try to refresh the token using the refresh token
        refresh_data = {
            "client_id": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_KEY,
            "client_secret": settings.SOCIAL_AUTH_GOOGLE_OAUTH2_SECRET,
            "refresh_token": refresh_token,
            "grant_type": "refresh_token"
        }
        refresh_response = requests.post(token_url, data=refresh_data)
        if refresh_response.status_code != 200:
            return HttpResponse("Failed to refresh tokens", status=400)

        refreshed_tokens = refresh_response.json()
        new_auth_token = refreshed_tokens.get('id_token')
        new_refresh_token = refreshed_tokens.get('refresh_token', refresh_token)  # Use the new refresh token if provided

        if not new_auth_token:
            return HttpResponse("Failed to refresh ID token", status=400)

        # Store user data and tokens in the session
        request.session['user_data'] = user_data
        request.session['auth_key'] = new_auth_token
        request.session['refresh_token'] = refresh_token  # Store refresh token for future use

        # Optionally store tokens in the database
        new_user = NewUser.objects.get(
            email = user_data['email'],
            google_id =  user_data['sub'],
        )
        
        if not new_user :
            
            new_user = NewUser.objects.create(
                google_id=user_data['sub'],
                email = user_data['email'],
                name = user_data['name'],
                picture_url = user_data.get('picture', ''),
                authkey = new_auth_token,
                refresh_token = refresh_token
            )
        else :
            new_user.authkey = new_auth_token
            new_user.refresh_token = refresh_token
            new_user.save()
        
        # Return the new tokens and user data
        return JsonResponse({
            "auth-token": new_auth_token,
            "refresh-token": new_refresh_token,
            "user-data": user_data
        }, status=200)

    return JsonResponse({
        "auth-token": auth_token,
        "refresh-token": refresh_token,
        "user-data": user_data
    }, status=200)
    
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
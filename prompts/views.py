import json, inspect
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from .models import prompts
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from google_auth.models import NewUser
from user_apps.models import user_app
from prompts.models import prompts
# Create your views here.

@method_decorator(csrf_exempt, name='dispatch')
class GetAllPrompts(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "google_id" in req_keys or not "email" in req_keys or not "app_name" in req_keys  :
            return JsonResponse({'error': "there is not google id or email or name of the app"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'])
        if not user :
            user =  NewUser.objects.filter(email = req_data['email']) 
            if not user:
                return JsonResponse({'error': "No user found"}, status=400)
            
        user = user.first()
        apps_objects = user_app.objects.filter(user = user,app_name = req_data['app_name'] ) 
        if not apps_objects:
            return JsonResponse({'error': f"user doesnt have apps created named : {req_data['app_name']}"}, status=400)
        apps_object = apps_objects.first()
        data = [ { "prompt" : i.prompt, "validate" : i.validate, "created_at" : i.created_at} for i in prompts.objects.filter(app = apps_object, user = user)]
        
        return JsonResponse({'success': f"Got the all prompt from app name : {apps_object.app_name}", "data" : data}, status=200)
        
        
        

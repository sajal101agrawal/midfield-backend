import json
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from google_auth.models import NewUser
from .models import user_app
from django.core import serializers

@method_decorator(csrf_exempt, name='dispatch')
class create(View):
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        if not ("google_id" and "email" and "app_name") in req_data.keys() :
            return JsonResponse({'error': "there is not google id or email or app's name"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'],email = req_data['email'])
        if not user :
            return JsonResponse({'error': "No user found"}, status=400)
        
        
        user = user.first()
        
        if user_app.objects.filter(app_name = req_data['app_name'],user = user) :
            return JsonResponse({'error': "This app is already exists"}, status=400)
            
        
        user_app.objects.create(app_name = req_data['app_name'],user = user)
            
        return JsonResponse({'success': "The app is created successfully"}, status=201)
    


@method_decorator(csrf_exempt, name='dispatch')
class app_list(View):
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        user_app_list = []
        req_data= json.loads(request.body)
        if not ("google_id" or "email" ) in req_data.keys() :
            return JsonResponse({'error': "there is not google id or email"}, status=400)
        
        user = NewUser.objects.filter(google_id = req_data['google_id'])
        if not user :
            user =  NewUser.objects.filter(email = req_data['email']) 
            if not user:
                return JsonResponse({'error': "No user found"}, status=400)
        
        user = user.first()
        apps_objects = user_app.objects.filter(user = user) 
        if not apps_objects:
            return JsonResponse({'error': "user doesnt have any apps created"}, status=400)
        
        user_app_list = [ {"app_name" : i.app_name, "user_name" : i.user.name} for i in apps_objects]
        return JsonResponse({'success': "The app is created successfully","app_lists" : user_app_list,'error': ''}, status=201)
    


@method_decorator(csrf_exempt, name='dispatch')
class update_app(View):
    
    @method_decorator(csrf_exempt)
    def post(self, request):
        """to update the app of user"""
        user_app_list = []
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "google_id" in req_keys or not "email" in req_keys or not "app_name" in req_keys :
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
        
        if not "new_name" in req_data.keys() :
            return JsonResponse({'error': "there is not new name of the app"}, status=400)
        
        apps_object = apps_objects.first()
        apps_object.app_name = req_data['new_name']
        apps_object.save()
        
        return JsonResponse({'success': "The app is updated successfully",'error': ''}, status=201)
    
    @method_decorator(csrf_exempt)
    def delete(self, request):
        """to delete the app of user"""

        user_app_list = []
        req_data= json.loads(request.body)
        req_keys = req_data.keys()
        if not "google_id" in req_keys or not "email" in req_keys or not "app_name" in req_keys :
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
        apps_objects.delete()
        
        return JsonResponse({'success': "The app is created successfully","app_lists" : user_app_list,'error': ''}, status=201)
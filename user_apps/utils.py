from user_apps.models import user_app
from prompts.models import prompts


def get_apps_details(user):
    """recive the user object of model and return the data of user's related app in list of all apps with details in json\n
    Example : [ { data1 }, { data2 } ]"""
    
    user_app_list = []
    userapps = user_app.objects.filter(user=user)
    if userapps  :
        user_app_list = [ {"app_name" : i.app_name, "user_name" : i.user.name, "id" : i.id} for i in userapps]
        for app in user_app_list:
            prompt_tmp = {}
            prompts_list = prompts.objects.filter(id=app['id'])
            if prompts_list :
                for prompt_obj in prompts_list :
                    prompt_tmp['prompt'] = prompt_obj.prompt
                    prompt_tmp['validate'] = prompt_obj.validate
                    
            app['prompt_data'] = prompt_tmp
                
            
        
    return user_app_list
    
    
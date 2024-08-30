import json, inspect
from django.shortcuts import render
from django.views import View
from django.http import JsonResponse
from rest_framework import status
from .models import prompts
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from google_auth.models import NewUser
from user_apps.models import user_app
from prompts.models import prompts
from validators.models import validators, Associated_validators
from guardrails import Guard, OnFailAction
from guardrails.hub import (
    RegexMatch, ToxicLanguage, MentionsDrugs,
    CompetitorCheck, ValidLength, ValidURL,
    ValidJson, ValidPython, ValidSQL,
    WebSanitization, ValidAddress, UnusualPrompt,
    SqlColumnPresence, ResponsivenessCheck, ReadingTime,
    QuotesPrice, OneLine, LowerCase,
    HasUrl, ExcludeSqlPredicates, EndpointIsReachable,
    SimilarToDocument, SaliencyCheck, RelevancyEvaluator,
    ProvenanceLLM, LowerCase, LogicCheck,
    GibberishText, ExtractedSummarySentencesMatch, DetectPII,
    ArizeDatasetEmbeddings, CorrectLanguage, 
    DetectPromptInjection, ExtractiveSummary, NSFWText,
    ProvenanceEmbeddings, QARelevanceLLMEval, RestrictToTopic,
    SecretsPresent, SimilarToPreviousValues, WikiProvenance,
    CsvMatch, EndsWith, FinancialTone,
    LLMCritic, PolitenessCheck, ReadingLevel,
    RedundantSentences, ResponseEvaluator, SensitiveTopic,
    TwoWords,
    UpperCase, ValidChoices, ValidRange,
    ValidOpenApiSpec, ProfanityFree )

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
        
        
        
@method_decorator(csrf_exempt, name='dispatch')
class validate(View):
    @method_decorator(csrf_exempt)
    def post(self, request):
        req_data= json.loads(request.body)
        
        if not "apikey"  in req_data.keys():
            return JsonResponse({'error': 'API KEY is required'}, status=status.HTTP_400_BAD_REQUEST)

        if not "prompt"  in req_data.keys():
            return JsonResponse({'error': 'Prompt is required'}, status=status.HTTP_400_BAD_REQUEST)

        apikey = req_data['apikey']
        prompt = req_data['prompt']

        user_app_obj = user_app.objects.filter(api_key= apikey)
        if not user_app_obj :
            return JsonResponse({'error': "invalid api key"}, status=400)
        user_app_obj = user_app_obj.first()
        user_obj = user_app_obj.user
        
        asoociated_val_objects = Associated_validators.objects.filter(userapp=user_app_obj)
        if not asoociated_val_objects:
            return JsonResponse({'error': f"user does not have any asoociated validator created"}, status=400)

        checks = []
        
        for val in asoociated_val_objects :
            
            validator_objects = val.validator
            tmp = {}
            tmp['type'] = validator_objects.name
            if validator_objects.parameters :
                tmp['parameters'] = validator_objects.parameters
            checks.append(tmp)

        # Map of check types to validator classes
        validators = {
            'arize_dataset_embeddings': ArizeDatasetEmbeddings,
            'correct_language': CorrectLanguage,
            'detect_prompt_injection': DetectPromptInjection,
            'extractive_summary': ExtractiveSummary,
            'nsfw_text': NSFWText,
            'provenance_embeddings': ProvenanceEmbeddings,
            'qa_relevance_llm_eval': QARelevanceLLMEval,
            'restrict_to_topic': RestrictToTopic,
            'secrets_present': SecretsPresent,
            'similar_to_previous_values': SimilarToPreviousValues,
            'wiki_provenance': WikiProvenance,
            'csv_match': CsvMatch,
            'ends_with': EndsWith,
            'financial_tone': FinancialTone,
            'llm_critic': LLMCritic,
            'mentions_drugs': MentionsDrugs,
            'politeness_check': PolitenessCheck,
            'reading_level': ReadingLevel,
            'redundant_sentences': RedundantSentences,
            'response_evaluator': ResponseEvaluator,
            'sensitive_topic': SensitiveTopic,
            'two_words': TwoWords,
            'upper_case': UpperCase,
            'valid_choices': ValidChoices,
            'valid_length': ValidLength,
            'valid_python': ValidPython,
            'valid_sql': ValidSQL,
            'web_sanitization': WebSanitization,
            'valid_url': ValidURL,
            'valid_range': ValidRange,
            'valid_openapi_spec': ValidOpenApiSpec,
            'valid_json': ValidJson,
            'valid_address': ValidAddress,
            'unusual_prompt': UnusualPrompt,
            'sql_column_presence': SqlColumnPresence,
            'responsiveness_check': ResponsivenessCheck,
            'regex_match': RegexMatch,
            'reading_time': ReadingTime,
            'quotes_price': QuotesPrice,
            'one_line': OneLine,
            'lower_case': LowerCase,
            'has_url': HasUrl,
            'exclude_sql_predicates': ExcludeSqlPredicates,
            'endpoint_is_reachable': EndpointIsReachable,
            'toxic_language': ToxicLanguage,
            'similar_to_document': SimilarToDocument,
            'saliency_check': SaliencyCheck,
            'relevancy_evaluator': RelevancyEvaluator,
            'provenance_llm': ProvenanceLLM,
            'profanity_free': ProfanityFree,
            'logic_check': LogicCheck,
            'gibberish_text': GibberishText,
            'extracted_summary_sentences_match': ExtractedSummarySentencesMatch,
            'detect_pii': DetectPII,
            'competitor_check': CompetitorCheck,
        }

        validators_instances = []

        for check in checks:
            check_type = check.get('type')
            parameters = check.get('parameters', {})
            validator_class = validators.get(check_type)
            if not validator_class:
                return JsonResponse({'error': f'Unknown check type: {check_type}'}, status=status.HTTP_400_BAD_REQUEST)
            try:
                validator_instance = validator_class(**parameters, on_fail=OnFailAction.EXCEPTION)
                validators_instances.append(validator_instance)
            except TypeError as e:
                return JsonResponse({'error': f'Error initializing validator {check_type}: {str(e)}'}, status=status.HTTP_400_BAD_REQUEST)
        guard = Guard().use_many(*validators_instances)

        try:
            result = guard.validate(prompt)
            prompts.objects.create(
                app = user_app_obj,
                user = user_obj,
                validate = result,
                prompt = prompt
            )
        except Exception as e:
            return JsonResponse({'error': str(e)}, status=status.HTTP_400_BAD_REQUEST)
        return JsonResponse({'message': 'Prompt validated successfully!',"result" : result.validation_passed }, status=status.HTTP_200_OK)
        
        
# @method_decorator(csrf_exempt, name='dispatch')
# class validate(View):
#     @method_decorator(csrf_exempt)
#     def post(self, request):
        
#         req_data= json.loads(request.body)
#         req_keys = req_data.keys()
#         if not "prompt" in req_keys  :
#             return JsonResponse({'error': "prompt is not provided"}, status=400)
        
#         if not "apikey" in req_keys  :
#             return JsonResponse({'error': "api key is not provided"}, status=400)
        
        
#         user_app_obj = user_app.objects.filter(api_key= req_data['apikey'])
#         if not user_app_obj :
#             return JsonResponse({'error': "invalid api key"}, status=400)
#         user_app_obj = user_app_obj.first()
#         user_obj = user_app_obj.user
        
#         asoociated_val_objects = Associated_validators.objects.filter(userapp=user_app_obj)
#         if not asoociated_val_objects:
#             return JsonResponse({'error': f"user does not have any asoociated validator created"}, status=400)

#         data = {}
#         validate_data = {}
#         for val in asoociated_val_objects :
#             tmp = {}
#             validate_data['error'] = []

#             validator_objects = val.validator
#             function_name = validator_objects.name 
#             function_to_call = globals().get(function_name)
#             if function_to_call is None:
#                 validate_data['error'].append( f"Validator '{function_name}' not found")
                
#             args_to_pass = {}
#             missing_param = []
#             try:
#                 signature = inspect.signature(function_to_call)
#                 for param in signature.parameters.values(): 
                    
#                     if param.name == "prompt":
#                         args_to_pass[param.name] = req_data["prompt"]
                    
#                     elif param.name in req_keys :
#                         args_to_pass[param.name] = req_data[param.name]
                    
#                     elif param.name in asoociated_val_objects.first().parameters.keys():
#                         args_to_pass[param.name] = asoociated_val_objects.first().parameters[param.name]
                        
#                     elif param.default is not inspect.Parameter.empty:
#                         args_to_pass[param.name] = param.default
                        
#                     else:
#                         missing_param.append(param.name)
                        
#                     if missing_param :
#                         validate_data['error'].append(f"Missing required parameter: {missing_param}")
                    
#                 try:
#                     result = function_to_call(**args_to_pass)
#                     prompts.objects.create(
#                         app = user_app_obj,
#                         user = user_obj,
#                         validate = result,
#                         prompt = args_to_pass["prompt"]
#                     )
#                     tmp['result'] = result
#                     tmp['prompt'] = req_data["prompt"]
                    
#                 except Exception as e:
#                     validate_data['error'].append(f"Validation failed: {str(e)}")
                
#             except Exception as e:
#                 validate_data['error'].append(f"Validation failed: {str(e)}")
#             tmp['erros'] = validate_data['error']
#             data[validator_objects.name ] = tmp
            
            
#         return JsonResponse({'data': data}, status=status.HTTP_200_OK)
        
        
        
  # checks = [
        # {
        #     "type": "regex_match",
        #     "parameters": {
        #         "regex": "\\(?\\d{3}\\)?-? *\\d{3}-? *-?\\d{4}"
        #     }
        # },
        # {
        #     "type": "toxic_language",
        #     "parameters": {}
        # },
        #         {
        #     "type": "mentions_drugs",
        #     "parameters": {}
        # }
        # ]
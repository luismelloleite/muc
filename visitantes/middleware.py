import json
import logging
from django.conf import settings
from .models import LogAtividade, CustomUser # Importar CustomUser

# Configure um logger para este middleware
logger = logging.getLogger(__name__)

LOGIN_PATHS = getattr(settings, 'LOGGING_LOGIN_PATHS', ['/login/', '/admin/login/'])
LOGOUT_PATHS = getattr(settings, 'LOGGING_LOGOUT_PATHS', ['/logout/', '/admin/logout/'])

SENSITIVE_KEYS = getattr(settings, 'LOGGING_SENSITIVE_KEYS', {
    'password', 'password1', 'password2', 'new_password1', 'new_password2', 'current_password',
    'secret', 'token', 'authorization', 'secret_key', 'api_key',
    # Adicione outros campos sensíveis que você possa ter
})

KEYS_TO_REMOVE = getattr(settings, 'LOGGING_KEYS_TO_REMOVE', {'csrfmiddlewaretoken'})

class LogAtividadeMiddleware:
    def __init__(self, get_response):
        self.get_response = get_response
        try:
            self.auth_user_model_name = CustomUser._meta.object_name
        except Exception:
            self.auth_user_model_name = "User" # Fallback

    def _sanitize_payload(self, payload_dict):
        sanitized_payload = {}
        if not isinstance(payload_dict, dict):
            return "Payload não é um dicionário ou não pôde ser parseado."

        for key, value in payload_dict.items():
            if key in KEYS_TO_REMOVE:
                continue # Pula esta chave completamente
            if key.lower() in SENSITIVE_KEYS:
                sanitized_payload[key] = "[MASKED]"
            else:
                sanitized_payload[key] = value
        return sanitized_payload

    def __call__(self, request):
        user_before_request = request.user
        is_authenticated_before = user_before_request.is_authenticated if hasattr(user_before_request, 'is_authenticated') else False

        response = self.get_response(request)

        user_after_request = request.user
        is_authenticated_after = user_after_request.is_authenticated if hasattr(user_after_request, 'is_authenticated') else False

        log_data = None
        current_path = request.path_info

        payload_to_log_str = "N/A"

        if request.method in ['POST', 'PUT', 'PATCH'] and request.POST:
            try:
                post_data = request.POST.dict().copy()
                sanitized_post_data = self._sanitize_payload(post_data)
                payload_to_log_str = json.dumps(sanitized_post_data, ensure_ascii=False, indent=2)
            except Exception:
                payload_to_log_str = "Não foi possível capturar ou sanitizar o payload do POST."
        
        # 1. Tratar Tentativas de Login
        is_login_path_post = request.method == 'POST' and any(current_path.startswith(p) for p in LOGIN_PATHS)
        
        if is_login_path_post:
            # Determina o campo usado para username (pode ser 'username' ou 'email')
            username_key = CustomUser.USERNAME_FIELD # Use o USERNAME_FIELD do seu modelo
            if username_key not in request.POST and 'username' in request.POST: # Fallback para 'username' se não for o email
                username_key = 'username'
            elif username_key not in request.POST and 'email' in request.POST: # Fallback para 'email'
                username_key = 'email'

            username_attempt = request.POST.get(username_key, 'N/A')

            if not is_authenticated_before and is_authenticated_after:
                log_data = {
                    'usuario': user_after_request,
                    'acao': "LOGIN_SUCCESS",
                    'modelo': getattr(user_after_request, '_meta', {}).object_name or self.auth_user_model_name,
                    'objeto_id': getattr(user_after_request, 'pk', 0),
                    'descricao': f"Login bem-sucedido: {user_after_request.get_username()}. \nEndpoint: {current_path}."
                }
            else: # Login falhou ou outro POST para a página de login
                status_info = f" Status da resposta: {response.status_code}." if response else ""
                log_data = {
                    'usuario': None,
                    'acao': "LOGIN_FAILURE",
                    'modelo': self.auth_user_model_name,
                    'objeto_id': 0,
                    'descricao': (
                        f"Tentativa de login falhou para: {username_attempt}. "
                        f"Endpoint: {current_path}.{status_info} "
                        f"\nPayload: \n{payload_to_log_str}"
                    )
                }
        
        # 2. Tratar Logout
        is_logout_path = any(current_path.startswith(p) for p in LOGOUT_PATHS)
        if not log_data and is_logout_path and is_authenticated_before and not is_authenticated_after:
             log_data = {
                'usuario': user_before_request,
                'acao': "LOGOUT",
                'modelo': getattr(user_before_request, '_meta', {}).object_name or self.auth_user_model_name,
                'objeto_id': getattr(user_before_request, 'pk', 0),
                'descricao': f"Logout: {user_before_request.get_username()}. \nEndpoint: {current_path}."
            }

        # 3. Tratar outras ações autenticadas (POST, PUT, DELETE)
        if not log_data and is_authenticated_after and request.method in ['POST', 'PUT', 'DELETE']:
            modelo_name = "N/A"
            obj_id = 0

            if request.resolver_match:
                view_func = request.resolver_match.func
                if hasattr(view_func, 'view_class'):
                    view_class = view_func.view_class
                    model = getattr(view_class, 'model', None) or \
                            (getattr(view_class, 'queryset', None) and view_class.queryset.model)
                    if model:
                        modelo_name = model._meta.object_name
                
                if modelo_name == "N/A":
                    modelo_name = request.resolver_match.view_name or getattr(request.resolver_match, 'app_name', "N/A")

                obj_id = request.resolver_match.kwargs.get('pk', 0)
                if not obj_id and hasattr(response, 'data') and isinstance(response.data, dict):
                    obj_id = response.data.get('id', 0)

            log_data = {
                'usuario': user_after_request,
                'acao': request.method,
                'modelo': modelo_name,
                'objeto_id': obj_id,
                'descricao': (
                    f"Ação {request.method} em {modelo_name} por {user_after_request.get_username()}. "
                    f"\nEndpoint: {current_path}. \nPayload: \n{payload_to_log_str}"
                )
            }

        if log_data:
            try:
                current_obj_id = log_data.get('objeto_id')
                log_data['objeto_id'] = int(current_obj_id) if str(current_obj_id).isdigit() else 0
                
                LogAtividade.objects.create(**log_data)
            except Exception as e:
                logger.error(
                    f"Erro ao salvar LogAtividade: {e} \nDados do Log: {log_data}",
                    exc_info=True
                )

        return response

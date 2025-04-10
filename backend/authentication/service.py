from users.models import User
from django.core.exceptions import ObjectDoesNotExist
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth import get_user_model

def save_refresh_token_when_user_login(email, refresh):
    try:
        userLogin = User.objects.get(email=email)

        userLogin.refresh_token = refresh
        userLogin.save()
        
        return userLogin
    except ObjectDoesNotExist:
        return None
    
def get_user_from_refresh_token(refresh_token):
    try:
        token = RefreshToken(refresh_token)
        user_id = token.payload.get("user_id")
        # User = get_user_model()
        user = User.objects.get(id=user_id)
        return user
    except:
        return None
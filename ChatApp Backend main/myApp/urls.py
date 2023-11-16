from django.urls import path
from .views import UserLoginView, OutfitGeneratorView


urlpatterns = [
    path('login/', UserLoginView.as_view(), name='user-login'),
    path('outfit-generator/', OutfitGeneratorView.as_view(), name='outfit-generator'),
]

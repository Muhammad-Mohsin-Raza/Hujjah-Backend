from django.urls import path
from users.views import AssistantCreateView, AssistantListView, ToggleAssistantStatusView, UserRegistrationView, UserLoginView, UserWithClientsView, UserDeleteView, UserFullProfileView
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)
urlpatterns = [
    path('register/', UserRegistrationView.as_view(), name='register'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', UserWithClientsView.as_view(), name='user-with-clients'),
    # path('delete/', UserDeleteView.as_view(), name='user-delete'),
    path('complete-user/', UserFullProfileView.as_view(),
         name='user-complete-data'),
    #  Assistants paths
    path('assistants/create/', AssistantCreateView.as_view(),
         name='create-assistant'),
    path('assistants/<int:assistant_id>/toggle-status/',
         ToggleAssistantStatusView.as_view(), name='toggle-assistant'),
    path('assistants/', AssistantListView.as_view(), name='assistant-list'),

]

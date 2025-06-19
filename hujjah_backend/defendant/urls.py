from django.urls import path
from .views import DefendantListCreateView, DefendantRetrieveUpdateDestroyView

urlpatterns = [
    path('', DefendantListCreateView.as_view(), name='defendant-list-create'),
    path('<int:pk>/', DefendantRetrieveUpdateDestroyView.as_view(),
         name='defendant-detail'),
]

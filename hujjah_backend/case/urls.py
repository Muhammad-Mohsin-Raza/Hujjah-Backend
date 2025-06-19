from django.urls import path
from .views import CaseListCreateView, CaseRetrieveUpdateDestroyView

urlpatterns = [
    path('', CaseListCreateView.as_view(), name='case-list-create'),
    path('<int:pk>/', CaseRetrieveUpdateDestroyView.as_view(), name='case-detail'),
]

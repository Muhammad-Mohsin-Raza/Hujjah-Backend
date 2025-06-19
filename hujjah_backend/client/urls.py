from django.urls import path
from .view import ClientFullProfileView, ClientListCreateView, ClientDetailView

urlpatterns = [
    path('', ClientListCreateView.as_view(), name='client-list-create'),
    path('<int:pk>/', ClientDetailView.as_view(), name='client-detail'),
    path('full-profile/', ClientFullProfileView.as_view(),
         name='client-full-profile'),

]

from django.urls import path
from .views import CaseNoteListCreateView, CaseNoteDetailView

urlpatterns = [
    path('', CaseNoteListCreateView.as_view(), name='case_note-list-create'),
    path('<int:pk>/', CaseNoteDetailView.as_view(), name='case_note-detail'),
]

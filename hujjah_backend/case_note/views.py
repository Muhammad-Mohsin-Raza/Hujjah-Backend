from rest_framework import generics

from users.permissions import IsOwnerOrAssistantReadOnly
from rest_framework.permissions import IsAuthenticated

from .models import CaseNote
from .serializers import CaseNoteSerializer


class CaseNoteListCreateView(generics.ListCreateAPIView):
    queryset = CaseNote.objects.all()
    serializer_class = CaseNoteSerializer


class CaseNoteDetailView(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAssistantReadOnly]
    queryset = CaseNote.objects.all()
    serializer_class = CaseNoteSerializer

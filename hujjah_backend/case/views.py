from django.shortcuts import render
from rest_framework import generics
from .models import Case
from .serializers import CaseSerializer
from rest_framework.permissions import IsAuthenticated


class CaseListCreateView(generics.ListCreateAPIView):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save()


class CaseRetrieveUpdateDestroyView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Case.objects.all()
    serializer_class = CaseSerializer
    permission_classes = [IsAuthenticated]

    def update(self, request, *args, **kwargs):
        # <-- make all fields optional during update
        kwargs['partial'] = True
        return super().update(request, *args, **kwargs)

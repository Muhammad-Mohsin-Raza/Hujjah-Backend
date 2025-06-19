from case.models import Case
from rest_framework import generics, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from users.utils import get_effective_user
from .models import Client
from .serializers import ClientFullProfileSerializer, ClientSerializer
from django.core.exceptions import ValidationError
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework.views import APIView


class ClientListCreateView(generics.ListCreateAPIView):
    serializer_class = ClientSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Client.objects.filter(user=self.request.user)

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def post(self, request, *args, **kwargs):
        try:
            return self.create(request, *args, **kwargs)
        except ValidationError as e:
            return Response({"errors": e.detail}, status=400)
        except Exception as e:
            return Response({"error": "Something went wrong", "details": str(e)}, status=500)


class ClientDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = ClientFullProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        effective_user = get_effective_user(self.request.user)
        return Client.objects.filter(user=effective_user).prefetch_related(
            Prefetch(
                'cases',
                queryset=Case.objects.select_related('defendant').prefetch_related('notes')
            ),
            'tasks'
        )
        # serializer = ClientFullProfileSerializer(client)
        # return Response(serializer.data)

    def get_object(self):
        try:
            obj = super().get_object()
            return obj
        except Client.DoesNotExist:
            raise Response({"error": "Client not found."},
                           status=status.HTTP_404_NOT_FOUND)

    def put(self, request, *args, **kwargs):
        try:
            return self.update(request, *args, **kwargs, partial=True)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, *args, **kwargs):
        try:
            return self.destroy(request, *args, **kwargs)
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)


class ClientFullProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        clients = Client.objects.filter(user=request.user).prefetch_related(
            Prefetch(
                'cases',
                queryset=Case.objects.select_related(
                    'defendant').prefetch_related('notes')
            ),
            'tasks'
        )
        serializer = ClientFullProfileSerializer(clients, many=True)
        return Response(serializer.data)

# class ClientFullProfileView(APIView):
#     permission_classes = [IsAuthenticated]

#     def get(self, request):
#         user = request.user

#         # If assistant, fetch the parent_user’s clients instead
#         if user.role == 'assistant' and hasattr(user, 'parent_user') and user.parent_user:
#             target_user = user.parent_user
#         else:
#             target_user = user

#         clients = Client.objects.filter(user=target_user).prefetch_related(
#             Prefetch(
#                 'cases',
#                 queryset=Case.objects.select_related(
#                     'defendant').prefetch_related('notes')
#             ),
#             'tasks'
#         )
#         serializer = ClientFullProfileSerializer(clients, many=True)
#         return Response(serializer.data)

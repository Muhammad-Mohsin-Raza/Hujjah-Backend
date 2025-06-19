from django.shortcuts import render
from case.models import Case
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from users.models import User
from users.permissions import IsOwnerOrAssistantReadOnly
from users.utils import get_effective_user
from .serializers import AssistantCreateSerializer, UserCompleteSerializer, UserRegistrationSerializer, UserLoginSerializer
from rest_framework_simplejwt.tokens import RefreshToken
from client.serializers import ClientSerializer
from rest_framework.permissions import IsAuthenticated
from client.models import Client
from django.shortcuts import get_object_or_404
from django.db.models import Prefetch
from rest_framework.exceptions import PermissionDenied


def get_token(obj):
    refresh = RefreshToken.for_user(obj)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }


class UserRegistrationView(APIView):
    def post(self, request):
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            return Response({
                'msg': 'User registered successfully',
                'user': {
                    'username': user.username,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'role': user.role,
                },
                'token': get_token(user)
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    def post(self, request):
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            # Check if user is an inactive assistant
            if user.role == 'assistant' and not user.is_active:
                raise PermissionDenied(
                    detail="Assistant account is disabled. Please contact the administrator.")

            tokens = get_token(user)

            return Response({
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'role': user.role,
                },
                'tokens': tokens
            }, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserWithClientsView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = get_effective_user(request.user)
        clients = Client.objects.filter(user=user)
        client_data = ClientSerializer(clients, many=True).data

        return Response({
            "user": {
                "id": request.user.id,
                "username": request.user.username,
                "email": request.user.email,
                "phone_number": request.user.phone_number,
                "role": request.user.role,
                "clients": client_data
            },
        }, status=status.HTTP_200_OK)


class UserDeleteView(APIView):
    permission_classes = [IsAuthenticated, IsOwnerOrAssistantReadOnly]

    def delete(self, request):
        user = request.user
        username = user.username  # store info for message
        user.delete()
        return Response({
            "message": f"User '{username}' and all related data deleted successfully."
        }, status=status.HTTP_200_OK)


class UserFullProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        current_user = request.user

        # If the user is assistant, get their parent (lawyer)
        if current_user.role == 'assistant':
            parent_user = current_user.parent_user
        else:
            parent_user = current_user

        user = get_object_or_404(User, pk=parent_user.pk)

        user = User.objects.prefetch_related(
            Prefetch(
                'clients',
                queryset=Client.objects.prefetch_related(
                    Prefetch(
                        'cases',
                        queryset=Case.objects
                        .select_related('defendant')   # Optional OneToOneField
                        .prefetch_related('notes')     # Optional reverse FK
                    ),
                    'tasks'
                )
            )
        ).get(pk=parent_user.pk)

        serializer = UserCompleteSerializer(user)
        return Response(serializer.data)


class AssistantCreateView(APIView):
    """
    Allows a primary user (lawyer/admin) to create an assistant account under their ownership.
    The assistant will have limited privileges and will be linked via the parent_user field.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            if request.user.role not in ['admin', 'user']:
                return Response({"detail": "Only primary users can add assistants."}, status=403)

            serializer = AssistantCreateSerializer(
                data=request.data, context={'request': request})
            if serializer.is_valid():
                assistant = serializer.save()
                return Response({
                    'msg': 'Assistant created successfully.',
                    'assistant': {
                        'username': assistant.username,
                        'email': assistant.email,
                        'phone_number': assistant.phone_number,
                        'role': assistant.role,
                        'is_active': assistant.is_active,
                    }
                }, status=status.HTTP_201_CREATED)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            return Response({"detail": "An error occurred while creating assistant.", "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ToggleAssistantStatusView(APIView):
    """
    Toggles the 'is_active' status of an assistant.
    Only the parent user (lawyer) is authorized to perform this action.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request, assistant_id):
        try:
            assistant = User.objects.get(
                id=assistant_id, parent_user=request.user, role='assistant')
            assistant.is_active = not assistant.is_active
            assistant.save()
            return Response({
                "msg": f"Assistant {'enabled' if assistant.is_active else 'disabled'} successfully.",
                "assistant": {
                    "username": assistant.username,
                    "is_active": assistant.is_active
                }
            }, status=status.HTTP_200_OK)

        except User.DoesNotExist:
            return Response({"detail": "Assistant not found or unauthorized access."}, status=status.HTTP_404_NOT_FOUND)
        except Exception as e:
            return Response({"detail": "An error occurred while updating assistant status.", "error": str(e)},
                            status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class AssistantListView(APIView):
    """
    Returns a list of assistants linked to the currently authenticated parent user.
    Only accessible to users with role 'admin' or 'user'.
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        if user.role not in ['admin', 'user']:
            return Response({"detail": "Only primary users can view assistants."}, status=403)

        assistants = User.objects.filter(parent_user=user, role='assistant')

        data = [
            {
                "id": assistant.id,
                "username": assistant.username,
                "email": assistant.email,
                "phone_number": assistant.phone_number,
                "is_active": assistant.is_active
            }
            for assistant in assistants
        ]

        return Response({"assistants": data}, status=status.HTTP_200_OK)

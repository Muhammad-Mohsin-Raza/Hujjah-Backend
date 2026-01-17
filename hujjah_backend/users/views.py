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
from client.serializers import ClientSerializer, ClientFullProfileSerializer
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
                    'terms_accepted': user.terms_accepted,
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

            # Update last_login timestamp
            from django.utils import timezone
            user.last_login = timezone.now()
            
            # Clear deletion request if user logs in during grace period
            if user.deletion_requested_at:
                user.deletion_requested_at = None
            
            user.save()

            tokens = get_token(user)

            return Response({
                'user': {
                    'id': str(user.id),
                    'username': user.username,
                    'email': user.email,
                    'phone_number': user.phone_number,
                    'role': user.role,
                    'terms_accepted': user.terms_accepted,
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
                "terms_accepted": request.user.terms_accepted,
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
                        'id': assistant.id,
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


class AcceptTermsView(APIView):
    """
    Allows authenticated users to accept terms and conditions.
    This endpoint updates the terms_accepted field to True.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            user.terms_accepted = True
            user.save()

            return Response({
                "msg": "Terms and conditions accepted successfully.",
                "user": {
                    "id": user.id,
                    "username": user.username,
                    "terms_accepted": user.terms_accepted
                }
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "detail": "An error occurred while updating terms acceptance.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class RequestAccountDeletionView(APIView):
    """
    Allows authenticated users to request account deletion.
    Account will be deleted after 30 days if no login occurs.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            from django.utils import timezone
            user = request.user
            
            # Check if deletion is already requested
            if user.deletion_requested_at:
                return Response({
                    "detail": "Account deletion already requested.",
                    "deletion_requested_at": user.deletion_requested_at,
                    "msg": "Your account is scheduled for deletion. Log in to cancel the request."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Set deletion request timestamp
            user.deletion_requested_at = timezone.now()
            user.save()

            return Response({
                "msg": "Account deletion requested successfully. Your account will be deleted in 30 days if you don't log in.",
                "deletion_requested_at": user.deletion_requested_at
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "detail": "An error occurred while requesting account deletion.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class CancelAccountDeletionView(APIView):
    """
    Allows authenticated users to cancel a pending account deletion request.
    """
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            user = request.user
            
            # Check if deletion request exists
            if not user.deletion_requested_at:
                return Response({
                    "detail": "No pending deletion request found."
                }, status=status.HTTP_400_BAD_REQUEST)
            
            # Clear deletion request
            user.deletion_requested_at = None
            user.save()

            return Response({
                "msg": "Account deletion request cancelled successfully."
            }, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "detail": "An error occurred while cancelling account deletion.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


class ExportUserDataView(APIView):
    """
    Export all user data securely in JSON format.
    Excludes sensitive fields like password, ids (optional), and internal flags.
    Structure:
    {
        "user": { ... },
        "assistants": [ ... ],
        "clients": [
            {
                ...,
                "cases": [ ... ],
                "tasks": [ ... ]
            }
        ]
    }
    """
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            current_user = request.user
            
            # Efficiently fetch all related data
            # Use prefetch_related for reverse foreign keys
            user = User.objects.prefetch_related(
                'assistants',
                Prefetch(
                    'clients',
                    queryset=Client.objects.prefetch_related(
                        'tasks',
                        Prefetch(
                            'cases',
                            queryset=Case.objects.select_related('defendant').prefetch_related('notes')
                        )
                    )
                )
            ).get(id=current_user.id)

            # Manual serialization for privacy control
            user_data = {
                "username": user.username,
                "email": user.email,
                "phone_number": user.phone_number,
                "role": user.role,
                "terms_accepted": user.terms_accepted,
                "created_at": user.created_at,
            }

            # Assistants
            assistants_data = [
                {
                    "username": a.username,
                    "email": a.email,
                    "phone_number": a.phone_number,
                    "is_active": a.is_active,
                    "role": a.role
                }
                for a in user.assistants.all()
            ]

            # Clients (using full profile serializer which includes cases and tasks)
            # We filter out sensitive fields from the serialized data if needed
            clients_serializer = ClientFullProfileSerializer(user.clients.all(), many=True)
            clients_data = clients_serializer.data

            response_data = {
                "user_profile": user_data,
                "assistants": assistants_data,
                "clients": clients_data
            }

            return Response(response_data, status=status.HTTP_200_OK)

        except Exception as e:
            return Response({
                "detail": "An error occurred while exporting data.",
                "error": str(e)
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

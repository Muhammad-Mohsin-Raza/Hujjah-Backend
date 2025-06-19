from client.serializers import ClientFullProfileSerializer
from rest_framework import serializers
from .models import User
from django.contrib.auth.hashers import make_password
from django.contrib.auth.password_validation import validate_password
from django.contrib.auth import authenticate


class UserRegistrationSerializer(serializers.ModelSerializer):
    # Validate Password
    # password = serializers.CharField(write_only=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ['email', 'username', 'phone_number', 'password', 'role']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Hash the password manually
        validated_data['password'] = make_password(validated_data['password'])
        return super().create(validated_data)


class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(write_only=True)
    password = serializers.CharField(
        write_only=True, style={'input_type': 'password'})
    access = serializers.CharField(read_only=True)
    refresh = serializers.CharField(read_only=True)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        if username and password:
            user = authenticate(username=username, password=password)
            if not user:
                raise serializers.ValidationError(
                    "Invalid username or password")
        else:
            raise serializers.ValidationError(
                "Must include username and password")

        attrs['user'] = user
        return attrs


class UserCompleteSerializer(serializers.ModelSerializer):
    clients = ClientFullProfileSerializer(many=True, read_only=True)

    class Meta:
        model = User
        fields = fields = [
            'id',
            'username',
            'email',
            'phone_number',
            'role',
            'clients'
        ]


#  For handling lawyer assistants


class AssistantCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email', 'phone_number', 'password']
        extra_kwargs = {
            'password': {'write_only': True},
        }

    def create(self, validated_data):
        # Automatically assign 'assistant' role and parent_user
        user = self.context['request'].user
        assistant = User.objects.create_user(
            username=validated_data['username'],
            email=validated_data['email'],
            phone_number=validated_data['phone_number'],
            password=validated_data['password'],
            role='assistant',
            parent_user=user
        )
        return assistant

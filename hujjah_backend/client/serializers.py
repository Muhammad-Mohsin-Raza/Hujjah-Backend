from case_note.serializers import CaseNoteSerializer
from defendant.serializers import DefendantSerializer
from rest_framework import serializers
from task.serializers import TaskSerializer
from .models import Client
from case.serializers import CaseSerializer


class ClientSerializer(serializers.ModelSerializer):
    # cases = CaseSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        exclude = ['user', 'created_at']  # user will be set from request
        read_only_fields = ['id']


class ClientFullProfileSerializer(serializers.ModelSerializer):
    cases = CaseSerializer(many=True, read_only=True)
    tasks = TaskSerializer(many=True, read_only=True)

    class Meta:
        model = Client
        fields = '__all__'

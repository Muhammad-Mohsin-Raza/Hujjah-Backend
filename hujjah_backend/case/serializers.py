from rest_framework import serializers
from task.serializers import TaskSerializer
from .models import Case
from defendant.serializers import DefendantSerializer
from case_note.serializers import CaseNoteSerializer


class CaseSerializer(serializers.ModelSerializer):
    defendant = DefendantSerializer(read_only=True)
    notes = CaseNoteSerializer(many=True, read_only=True)

    class Meta:
        model = Case
        fields = '__all__'

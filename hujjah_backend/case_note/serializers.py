from rest_framework import serializers
from .models import CaseNote


class CaseNoteSerializer(serializers.ModelSerializer):
    class Meta:
        model = CaseNote
        fields = '__all__'

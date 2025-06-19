from rest_framework import serializers
from .models import Defendant


class DefendantSerializer(serializers.ModelSerializer):
    class Meta:
        model = Defendant
        fields = '__all__'
        read_only_fields = ['id', 'created_at', 'updated_at']

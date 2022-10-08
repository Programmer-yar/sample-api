from rest_framework import serializers
from .models import Logger

class TaskSerializer(serializers.ModelSerializer):
    class Meta:
        model = Logger
        fields = '__all__'
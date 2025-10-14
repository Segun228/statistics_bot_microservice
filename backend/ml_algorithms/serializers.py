from rest_framework import serializers
from .models import ML_Model

class ML_ModelSerializer(serializers.ModelSerializer):
    task_display = serializers.CharField(source='get_task_display', read_only=True)
    type_display = serializers.CharField(source='get_type_display', read_only=True)

    class Meta:
        model = ML_Model
        fields = [
            "id",
            "user",
            "name",
            "description",
            "task",
            "task_display",
            "type",
            "type_display",
            "features",
            "target",
            "get_url",
            "post_url",
            "length",
            "created_at",
            "updated_at",
        ]
        read_only_fields = ["id", "user", "created_at", "updated_at"]
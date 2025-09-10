from rest_framework import serializers
from .models import Distribution, Dataset


class DistributionSerializer(serializers.ModelSerializer):
    distribution_parameters = serializers.JSONField()
    class Meta:
        model = Distribution
        fields = [
            'id',
            'user',
            'name',
            'description',
            'distribution_type',
            'distribution_parameters',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']


class DatasetSerializer(serializers.ModelSerializer):
    class Meta:
        model = Dataset
        fields = [
            "id",
            'columns',
            'url',
            "name",
            'alpha',
            'beta',
            'test',
            'control',
        ]
        read_only_fields = ['id', 'user', 'created_at', 'updated_at']
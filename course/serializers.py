from rest_framework import serializers

from core.models import Course


class CourseSerializer(serializers.ModelSerializer):
    """serializer for Course"""

    class Meta:
        model = Course
        fields = ['id', 'title', 'level']
        read_only_fields = ['id']

    def create(self, validated_data):
        """Create course"""
        course = Course.objects.create(**validated_data)

        return course

    def update(self, instance, validated_data):
        """Update a course"""
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()
        return instance


class CourseDetailSerializer(CourseSerializer):
    """Serializer for recipe detail view."""

    class Meta(CourseSerializer.Meta):
        fields = CourseSerializer.Meta.fields + ['description', 'document']


class DocumentSerializer(serializers.ModelSerializer):
    """Serializer for adding DOCUMENT TO COURSE"""

    class Meta:
        model = Course
        fields = ['id', 'document']
        read_only_fields = ['id']
        extra_kwargs = {
            'document': {'required': 'true'}
        }

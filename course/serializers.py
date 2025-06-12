from rest_framework import serializers

from core.models import Course, Enrollment, User, Progress


class CourseSerializer(serializers.ModelSerializer):
    """serializer for Course"""

    class Meta:
        model = Course
        fields = ['id', 'title', 'level', 'user']
        read_only_fields = ['id', 'user']

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


class StudentSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['username', 'email']


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


class EnrollmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Enrollment
        fields = ['id', 'user']
        read_only_fields = ['id', 'user']

    def create(self, validated_data):
        """Create course"""
        enrollement = Enrollment.objects.create(**validated_data)

        return enrollement


class ProgressSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Progress
        fields = ['course', 'completed']

    def create(self, validated_data):
        progress = Progress.objects.create(**validated_data)
        return progress

    def update(self, instance, validated_data):
        print(validated_data)
        instance.completed = validated_data.get('completed', instance.completed)
        instance.save()
        return instance


class MyCoursesSerializer(serializers.ModelSerializer):
    course = CourseSerializer(read_only=True)

    class Meta:
        model = Progress
        fields = ['id', 'course']

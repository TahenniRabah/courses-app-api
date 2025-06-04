from rest_framework import status
from rest_framework import viewsets
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission
from rest_framework.response import Response

from core.models import Course
from course import serializers


class IsStaffOrTeacherForPutOrPatch(BasePermission):
    """
    Allow PUT requests only to users who are staff or have role='teacher'.
    """

    def has_permission(self, request, view):
        if not request.method == "GET":
            user = request.user
            return user.is_authenticated and (
                user.role != 2,
            )
        return True

    def has_object_permission(self, request, view, obj):
        print('obj : ', obj.user)
        print('request : ', request)
        user = request.user
        if request.method != "GET":
            if not user.is_staff:
                return obj.user == user
        return True


class CourseViewSet(viewsets.ModelViewSet):
    """View for manage course APIs."""

    serializer_class = serializers.CourseDetailSerializer
    queryset = Course.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsStaffOrTeacherForPutOrPatch]

    def get_queryset(self):
        queryset = self.queryset

        return queryset.order_by('id')

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.CourseSerializer
        if self.action == 'upload_document':
            return serializers.DocumentSerializer

        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-document')
    def upload_document(self, request, pk=None):
        """Upload a file to course."""
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

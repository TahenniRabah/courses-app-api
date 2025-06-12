from rest_framework import viewsets, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.decorators import action
from rest_framework.permissions import BasePermission, IsAuthenticated
from rest_framework.response import Response

from core.models import Course, Enrollment, Progress
from course import serializers
from course.serializers import ProgressSerializer


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
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        queryset = self.queryset

        return queryset.order_by('id')

    def get_permissions(self):
        if self.action == 'enroll' or self.action == 'students':
            permission_classes = [IsAuthenticated]
        else:
            permission_classes = [IsStaffOrTeacherForPutOrPatch]

        return [permission() for permission in permission_classes]

    def get_serializer_class(self):
        """Return the serializer class for request"""
        if self.action == 'list':
            return serializers.CourseSerializer
        if self.action == 'upload_document':
            return serializers.DocumentSerializer
        if self.action == 'enroll':
            return serializers.EnrollmentSerializer
        if self.action == 'students':
            return serializers.StudentSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-document')
    def upload_document(self, request, pk=None):
        """Upload a file to course."""
        course = self.get_object()
        serializer = self.get_serializer(course, data=request.data)

        if serializer.is_valid():
            serializer.save(course=course)
            return Response(serializer.data, status=status.HTTP_200_OK)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['POST'], detail=True, url_path='enroll')
    def enroll(self, request, pk=None):
        """Enroll a course"""
        progression = False
        enrolled = False
        course = self.get_object()
        user = request.user
        if Enrollment.objects.filter(user=user, course=course).exists():
            enrolled = True
            if Progress.objects.filter(user=user, course=course).exists():
                progression = True
                return Response({'detail': 'Already enrolled in this course.'},
                                status=status.HTTP_400_BAD_REQUEST)
        if user.role == 2:
            if not enrolled:
                enrollment = Enrollment.objects.create(user=user, course=course)
                serializer = self.get_serializer(enrollment, data=request.data)
                if serializer.is_valid():
                    serializer.save()
            if not progression:
                progress = Progress.objects.create(user=user, course=course, completed=False)
                serializer2 = ProgressSerializer(progress, data=request.data)
                if serializer2.is_valid():
                    serializer2.save()
            if not enrolled:
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            return Response(serializer2.data, status=status.HTTP_201_CREATED)
        else:
            return Response({'detail': 'Only Students can enroll a course.'},
                            status=status.HTTP_400_BAD_REQUEST)

    @action(methods=['GET'], detail=True, url_path='students')
    def students(self, request, pk=None):
        course = self.get_object()
        enrollments = Enrollment.objects.filter(course=course)
        print(enrollments)
        if request.user == course.user:
            users = [enrollment.user for enrollment in enrollments]
            serializer = self.get_serializer(users, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response({'detail': 'Only Teacher owner of the course can see the list of students.'},
                        status=status.HTTP_400_BAD_REQUEST)


class MyCoursesViewSet(viewsets.ModelViewSet):
    serializer_class = serializers.ProgressSerializer
    queryset = Progress.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]
    http_method_names = ['get', 'post', 'patch', 'delete']

    def get_queryset(self):
        if self.action == 'list':
            self.http_method_names = ['get']
            return Progress.objects.filter(user=self.request.user)

        if self.action == 'retrieve':
            self.http_method_names = ['get', 'patch', 'delete']
            id = self.request.parser_context.get('kwargs').get('pk')
            q = Progress.objects.filter(user=self.request.user, id=id)
            return q
        return self.queryset

    def get_serializer_class(self):
        if self.action == 'list':
            return serializers.MyCoursesSerializer
        if self.action == 'retrieve':
            return serializers.ProgressSerializer
        return self.serializer_class

    def destroy(self, request, *args, **kwargs):
        pk = kwargs.get('pk')
        progress = Progress.objects.get(id=pk)
        enrolled = Enrollment.objects.get(course=progress.course, user=progress.user)
        progress.delete()
        enrolled.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)



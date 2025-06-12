"""
URL mappings for the recipe app.
"""
from django.urls import (
    path,
    include,
)
from rest_framework.routers import DefaultRouter

from course import views

router = DefaultRouter()
router.register('courses', views.CourseViewSet,basename='course')
router.register('my_courses',views.MyCoursesViewSet,basename='my_courses')
app_name = 'course'

urlpatterns = [
    path('', include(router.urls)),
    #path('my_courses/',views.MyCoursesViewSet.as_view({'get':'my_courses'})),
]

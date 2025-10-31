from django.urls import include, path
from rest_framework.routers import DefaultRouter

from .views import (
    GetTokenView,
    ProjectViewSet,
    SignUpView,
    TaskViewSet,
    UserViewSet,
)

app_name = 'api'

router_v1 = DefaultRouter()

router_v1.register('users', UserViewSet)
router_v1.register('projects', ProjectViewSet, basename='projects')
router_v1.register('tasks', TaskViewSet, basename='tasks')

urlpatterns = [
    path('v1/', include(router_v1.urls)),
    path('v1/auth/signup/', SignUpView.as_view()),
    path('v1/auth/token/', GetTokenView.as_view()),
]

import uuid

from django.contrib.auth.hashers import check_password, make_password
from django.core.mail import send_mail
from django.shortcuts import get_object_or_404
from rest_framework import filters, permissions, status, viewsets, mixins
from rest_framework.decorators import action
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from projects.models import Project, Task, User

from .permissions import IsAdminOrMe, IsAuthorOrReadOnly
from .serializers import (
    AuthSerializer,
    GetTokenSerializer,
    ProjectSerializer,
    TaskSerializer,
    UserMyselfSerializer,
    UserSerializer,
)


class SignUpView(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = AuthSerializer(data=request.data)

        user_in_db = User.objects.filter(
            username=request.data.get('username'),
            email=request.data.get('email')
        ).exists()

        if serializer.is_valid() or user_in_db:
            user, created = User.objects.get_or_create(
                username=serializer.data.get('username'),
                email=serializer.data.get('email')
            )
            confirmation_code = uuid.uuid4()
            user.confirmation_code = make_password(confirmation_code)
            user.save()
            send_mail(
                'Your confirmation_code',
                f'Ваш confirmation_code: {confirmation_code}',
                from_email=None,
                recipient_list=(user.email,),
                fail_silently=False,
            )
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class GetTokenView(APIView):

    permission_classes = (permissions.AllowAny,)

    def post(self, request):
        serializer = GetTokenSerializer(data=request.data)
        if serializer.is_valid():
            user = get_object_or_404(
                User,
                username=serializer.data.get('username')
            )
            code = serializer.data.get('confirmation_code')
            if not check_password(code, user.confirmation_code):
                return Response(
                    'Код не верный!',
                    status=status.HTTP_400_BAD_REQUEST,
                )
            refresh = RefreshToken.for_user(user)
            access = {'access': str(refresh.access_token)}
            return Response(access, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = (IsAdminOrMe,)

    filter_backends = (filters.SearchFilter,)
    search_fields = ('username',)
    lookup_field = 'username'
    pagination_class = PageNumberPagination

    @action(methods=['get', 'patch'], detail=False)
    def me(self, request):
        if request.method == 'PATCH':
            partial = True
            serializer = UserMyselfSerializer(
                request.user, data=request.data, partial=partial
            )
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
        serializer = self.get_serializer(request.user, many=False)
        return Response(serializer.data)


class ProjectViewSet(mixins.ListModelMixin, mixins.CreateModelMixin, viewsets.GenericViewSet):
    queryset = Project.objects.all().order_by('name')
    serializer_class = ProjectSerializer
    permission_classes = (permissions.IsAuthenticatedOrReadOnly,)

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    @action(methods=['get', 'post'], detail=True, url_path='tasks')
    def tasks(self, request, pk=None):
        project = get_object_or_404(Project, pk=pk)
        if request.method == 'GET':
            queryset = project.tasks.all()
            page = self.paginate_queryset(queryset)
            serializer = TaskSerializer(page or queryset, many=True)
            if page is not None:
                return self.get_paginated_response(serializer.data)
            return Response(serializer.data)
        # POST
        serializer = TaskSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(author=request.user, project=project)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class TaskViewSet(mixins.UpdateModelMixin, viewsets.GenericViewSet):
    queryset = Task.objects.all()
    serializer_class = TaskSerializer
    permission_classes = (
        permissions.IsAuthenticatedOrReadOnly,
        IsAuthorOrReadOnly,
    )
    http_method_names = ['patch', 'options', 'head']

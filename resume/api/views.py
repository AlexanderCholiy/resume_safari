from rest_framework import viewsets, generics, permissions, status, mixins
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.views import APIView
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from django.shortcuts import get_object_or_404
from rest_framework.request import Request
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth.hashers import make_password

from user.models import (
    HardSkillName,
    SoftSkillName,
    Location,
    User,
    # Resume,
    Position,
)
from .serializers import (
    HardSkillNameSerializer,
    SoftSkillNameSerializer,
    LocationSerializer,
    UserSerializer,
    # ResumeSerializer,
    PositionSerializer,
    PendingUserSerializer,
    UserMeSerializer,
    PasswordChangeSerializer,
    PasswordResetSerializer,
    PasswordResetConfirmSerializer,
)
# from .permissions import IsAdminOrStaff, IsOwnerOrStaffOrAdmin
from services.models import PendingUser


class UserAuthViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        methods=['post'],
        permission_classes=[permissions.AllowAny]
    )
    def register(self: 'UserAuthViewSet', request: Request) -> Response:
        serializer = PendingUserSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        pending_user = serializer.save()
        self.send_activation_email(pending_user, request)
        return Response(
            {'detail': 'Письмо с подтверждением отправлено'},
            status.HTTP_201_CREATED
        )

    @action(
        detail=False,
        methods=['get'],
        url_path='activate/(?P<uidb64>[^/]+)/(?P<token>[^/]+)',
        permission_classes=[permissions.AllowAny]
    )
    def activate(
        self: 'UserAuthViewSet',
        request: Request,
        uidb64: str,
        token: str
    ) -> Response:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            pending_user = PendingUser.objects.get(pk=uid)
        except Exception:
            return Response(
                {'detail': 'Недействительная ссылка'},
                status.HTTP_400_BAD_REQUEST
            )

        if default_token_generator.check_token(pending_user, token):
            user = User.objects.create(
                username=pending_user.username,
                email=pending_user.email,
                is_active=True,
            )
            user.password = pending_user.password
            user.save()
            pending_user.delete()
            return Response({'detail': 'Пользователь активирован'})
        return Response(
            {'detail': 'Ссылка недействительна или устарела'},
            status.HTTP_400_BAD_REQUEST
        )

    def send_activation_email(
        self: 'UserAuthViewSet', pending_user: PendingUser, request: Request
    ) -> None:
        token = default_token_generator.make_token(pending_user)
        uid = urlsafe_base64_encode(force_bytes(pending_user.pk))
        activation_path = reverse(
            'api:auth-activate', kwargs={'uidb64': uid, 'token': token})
        activation_link = request.build_absolute_uri(activation_path)

        subject = f'Подтверждение почты на {request.get_host()}'

        message = (
            f'Здравствуйте, {pending_user.username}!\n\n'
            f'Вы указали этот адрес при регистрации на {request.get_host()}.\n'
            f'Для подтверждения перейдите по ссылке:\n{activation_link}\n\n'
            f'Срок действия ссылки — 1 день.\n\n'
            f'Если вы не регистрировались — просто проигнорируйте это письмо.'
        )
        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, [pending_user.email]
        )


class MeViewSet(
    mixins.RetrieveModelMixin,
    mixins.UpdateModelMixin,
    mixins.DestroyModelMixin,
    viewsets.GenericViewSet
):
    serializer_class = UserMeSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        # Позволяет выполнять retrieve, update, destroy для текущего пользователя
        return self.request.user

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(self.get_object(), data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)

        updated_email = serializer.validated_data.get('email')
        current_email = request.user.email

        if updated_email and updated_email != current_email:
            pending_user = PendingUser.objects.create(
                username=request.user.username,
                email=updated_email,
                password=make_password(User.objects.make_random_password()),
            )
            self.send_email_change_confirmation(pending_user, request)

        serializer.save()
        return Response(serializer.data)

    def send_email_change_confirmation(self, pending_user, request):
        token = default_token_generator.make_token(pending_user)
        uid = urlsafe_base64_encode(force_bytes(pending_user.pk))
        activation_path = reverse('api:me-confirm-email', kwargs={'uidb64': uid, 'token': token})
        activation_link = request.build_absolute_uri(activation_path)

        subject = f'Подтверждение нового email на {request.get_host()}'
        message = (
            f'Здравствуйте, {pending_user.username}!\n\n'
            f'Для подтверждения нового email перейдите по ссылке:\n{activation_link}\n\n'
            f'Срок действия ссылки — 1 день.'
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [pending_user.email])

    @action(detail=False, methods=["get"], url_path="email-confirm/(?P<uidb64>[^/]+)/(?P<token>[^/]+)", permission_classes=[])
    def confirm_email(self, request, uidb64=None, token=None):
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            pending_user = PendingUser.objects.get(pk=uid)
        except Exception:
            return Response(
                {'detail': 'Недействительная ссылка'},
                status.HTTP_400_BAD_REQUEST
            )

        if default_token_generator.check_token(pending_user, token):
            try:
                user = User.objects.get(username=pending_user.username)
            except User.DoesNotExist:
                return Response(
                    {'detail': 'Пользователь не найден'},
                    status=status.HTTP_400_BAD_REQUEST
                )
            user.email = pending_user.email
            user.save()
            pending_user.delete()
            return Response({'detail': 'Email успешно подтверждён'})
        return Response(
            {'detail': 'Ссылка недействительна или устарела'},
            status.HTTP_400_BAD_REQUEST
        )


class PasswordViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def change(self, request):
        serializer = PasswordChangeSerializer(data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Пароль успешно изменён'})

    @action(detail=False, methods=['post'], permission_classes=[permissions.AllowAny])
    def reset(self, request):
        serializer = PasswordResetSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = get_object_or_404(User, email=email)
        token = default_token_generator.make_token(user)
        uid = urlsafe_base64_encode(force_bytes(user.pk))
        reset_link = request.build_absolute_uri(reverse(
            'api:password-reset-confirm', kwargs={'uidb64': uid, 'token': token}))

        subject = f'Восстановление пароля на {request.get_host()}'
        message = (
            f'Здравствуйте, {user.username}!\n\n'
            f'Для восстановления пароля перейдите по ссылке:\n{reset_link}\n\n'
            f'Срок действия ссылки — 1 день.'
        )
        send_mail(subject, message, settings.DEFAULT_FROM_EMAIL, [user.email])
        return Response({'detail': 'Письмо для восстановления отправлено'})


class PasswordResetConfirmViewSet(viewsets.ViewSet):
    @action(detail=False, methods=['post'], url_path='(?P<uidb64>[^/]+)/(?P<token>[^/]+)', permission_classes=[permissions.AllowAny])
    def confirm(self, request, uidb64, token):
        serializer = PasswordResetConfirmSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            user = User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, User.DoesNotExist):
            return Response({'detail': 'Недействительная ссылка'}, status=400)

        if default_token_generator.check_token(user, token):
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'detail': 'Пароль успешно сброшен'})
        return Response({'detail': 'Ссылка недействительна или устарела'}, status=400)


class HardSkillNameViewSet(viewsets.ModelViewSet):
    queryset = HardSkillName.objects.all()
    serializer_class = HardSkillNameSerializer


class SoftSkillNameViewSet(viewsets.ModelViewSet):
    queryset = SoftSkillName.objects.all()
    serializer_class = SoftSkillNameSerializer


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer


# class ResumeViewSet(viewsets.ModelViewSet):
#     lookup_field = 'slug'
#     queryset = Resume.objects.all()
#     serializer_class = ResumeSerializer

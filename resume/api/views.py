from rest_framework import viewsets, permissions, status, mixins
from django.utils.encoding import force_bytes, force_str
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.urls import reverse
from rest_framework.decorators import action
from rest_framework.response import Response
from django.core.mail import send_mail
from django.conf import settings
from rest_framework.request import Request
from django.contrib.auth.hashers import make_password
from urllib.parse import urljoin
from django.db.models import QuerySet, Q

from user.models import (
    HardSkillName,
    SoftSkillName,
    Location,
    User,
    Resume,
    Position,
)
from .serializers import (
    HardSkillNameSerializer,
    SoftSkillNameSerializer,
    LocationSerializer,
    UserSerializer,
    ResumeSerializer,
    PositionSerializer,
    PendingUserSerializer,
    UserMeSerializer,
    PasswordChangeSerializer,
)
from .permissions import StaffOrReadOnly, IsOwnerOrReadOnly, IsOwner
from services.models import PendingUser
from core.config import WebConfig


class UserAuthViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        methods=['post'],
        permission_classes=(permissions.AllowAny,)
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
        permission_classes=(permissions.AllowAny,)
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
        activation_link = urljoin(WebConfig.SITE_URL, activation_path)

        subject = f'Подтверждение почты на {WebConfig.FULL_SITE_URL}'

        message = (
            f'Здравствуйте, {pending_user.username}!\n\n'
            'Вы указали этот адрес при регистрации на '
            f'{WebConfig.FULL_SITE_URL}.\n'
            f'Для подтверждения перейдите по ссылке:\n{activation_link}\n\n'
            f'Срок действия ссылки — 1 день.\n\n'
            f'Если вы не регистрировались — просто проигнорируйте это письмо.'
        )
        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, [pending_user.email]
        )


class MeViewSet(viewsets.ViewSet):
    permission_classes = (IsOwner,)

    def get_object(self: 'MeViewSet') -> User:
        return self.request.user

    def retrieve(self: 'MeViewSet', request: Request) -> Response:
        serializer = UserMeSerializer(self.get_object())
        return Response(serializer.data)

    def update(self: 'MeViewSet', request: Request) -> Response:
        serializer = UserMeSerializer(
            self.get_object(), data=request.data, partial=True
        )
        serializer.is_valid(raise_exception=True)

        updated_email = serializer.validated_data.get('email')
        current_email = request.user.email

        if updated_email is not None and updated_email != current_email:
            pending_user = PendingUser.objects.create(
                username=request.user.username,
                email=updated_email,
                password=make_password(User.objects.make_random_password()),
            )
            self.send_email_change_confirmation(pending_user, request)

            return Response(
                {
                    'detail': (
                        'На новый email отправлена ссылка для подтверждения.'
                    )
                },
                status=status.HTTP_202_ACCEPTED
            )

        serializer.save()
        return Response(serializer.data)

    def destroy(self: 'MeViewSet', request: Request) -> Response:
        user = self.get_object()
        user.delete()

        return Response(
            {'detail': 'Пользователь и все связанные данные удалены'},
            status.HTTP_204_NO_CONTENT
        )

    def send_email_change_confirmation(
        self: 'MeViewSet', pending_user: PendingUser, request: Request
    ) -> Response:
        token = default_token_generator.make_token(pending_user)
        uid = urlsafe_base64_encode(force_bytes(pending_user.pk))
        activation_path = reverse(
            'api:me-confirm-email', kwargs={'uidb64': uid, 'token': token})
        activation_link = urljoin(WebConfig.SITE_URL, activation_path)

        subject = f'Подтверждение нового email на {WebConfig.FULL_SITE_URL}'
        message = (
            f'Здравствуйте, {pending_user.username}!\n\n'
            'Для подтверждения нового email перейдите по ссылке:\n'
            f'{activation_link}\n\n'
            f'Срок действия ссылки — 1 день.'
        )
        send_mail(
            subject, message, settings.DEFAULT_FROM_EMAIL, [pending_user.email]
        )

    @action(
        detail=False,
        methods=['get'],
        url_path=r'email-confirm/(?P<uidb64>[^/]+)/(?P<token>[^/]+)',
        permission_classes=(IsOwner,),
        name='me-confirm-email'
    )
    def confirm_email(
        self: 'MeViewSet',
        request: Request,
        uidb64: str | None = None,
        token: str | None = None
    ) -> Response:
        try:
            uid = force_str(urlsafe_base64_decode(uidb64))
            pending_user = PendingUser.objects.get(pk=uid)
        except Exception:
            return Response(
                {'detail': 'Недействительная ссылка'},
                status=status.HTTP_400_BAD_REQUEST
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
            status=status.HTTP_400_BAD_REQUEST
        )


class PasswordViewSet(viewsets.ViewSet):
    @action(
        detail=False,
        methods=['post'],
        permission_classes=(IsOwner,)
    )
    def change(self: 'PasswordViewSet', request: Request) -> Response:
        serializer = PasswordChangeSerializer(
            data=request.data, context={'request': request})
        serializer.is_valid(raise_exception=True)
        request.user.set_password(serializer.validated_data['new_password'])
        request.user.save()
        return Response({'detail': 'Пароль успешно изменён'})


class HardSkillNameViewSet(viewsets.ModelViewSet):
    queryset = HardSkillName.objects.all()
    serializer_class = HardSkillNameSerializer
    permission_classes = (StaffOrReadOnly,)


class SoftSkillNameViewSet(viewsets.ModelViewSet):
    queryset = SoftSkillName.objects.all()
    serializer_class = SoftSkillNameSerializer
    permission_classes = (StaffOrReadOnly,)


class LocationViewSet(viewsets.ModelViewSet):
    queryset = Location.objects.all()
    serializer_class = LocationSerializer
    permission_classes = (StaffOrReadOnly,)


class PositionViewSet(viewsets.ModelViewSet):
    queryset = Position.objects.all()
    serializer_class = PositionSerializer
    permission_classes = (StaffOrReadOnly,)


class UserViewSet(
    mixins.RetrieveModelMixin, mixins.UpdateModelMixin, viewsets.GenericViewSet
):
    serializer_class = UserSerializer
    permission_classes = (IsOwner,)

    def get_queryset(self: 'UserViewSet') -> QuerySet[User]:
        return User.objects.filter(pk=self.request.user.pk)


class ResumeViewSet(viewsets.ModelViewSet):
    lookup_field = 'slug'
    queryset = Resume.objects.all()
    serializer_class = ResumeSerializer
    permission_classes = (IsOwnerOrReadOnly,)

    def get_queryset(self: 'ResumeViewSet') -> QuerySet[Resume]:
        user = self.request.user
        if user.is_authenticated:
            return Resume.objects.filter(
                Q(is_published=True) | Q(user=user)
            )
        else:
            return Resume.objects.filter(
                Q(user__is_active=True) & Q(is_published=True)
            )

import pytest
from http import HTTPStatus

from django.test import Client
from django.urls import reverse
from django.contrib.auth.models import AbstractUser

from .models import Resume, Position, User


@pytest.fixture
def author(django_user_model: type[AbstractUser]) -> User:
    return django_user_model.objects.create(username='Автор')


@pytest.fixture
def not_author(django_user_model: type[AbstractUser]) -> User:
    return django_user_model.objects.create(username='Не автор')


@pytest.fixture
def author_client(author: User) -> Client:
    client = Client()
    client.force_login(author)
    return client


@pytest.fixture
def not_author_client(not_author: User) -> Client:
    client = Client()
    client.force_login(not_author)
    return client


@pytest.fixture
def position() -> Position:
    return Position.objects.create(
        position='Тестировщик',
        category='IT',
    )


@pytest.fixture
def published_resume(author: User, position: Position) -> Resume:
    return Resume.objects.create(
        user=author,
        position=position,
        is_published=True,
        about_me='Публичное резюме',
    )


@pytest.fixture
def draft_resume(author: User, position: Position) -> Resume:
    return Resume.objects.create(
        user=author,
        position=position,
        is_published=False,
        about_me='Черновик',
    )


@pytest.mark.django_db
@pytest.mark.parametrize(
    ('name', 'expected_status'),
    [
        ('user:resume_list', HTTPStatus.OK),
        ('schema-swagger-ui', HTTPStatus.OK),
        ('schema-redoc', HTTPStatus.OK),
        ('pages:about', HTTPStatus.OK),
        ('login', HTTPStatus.OK),
        ('logout', HTTPStatus.FOUND),
        ('services:register', HTTPStatus.OK),
    ]
)
def test_pages_availability_for_anonymous_user(
    client: Client, name: str, expected_status: int
) -> None:
    url = reverse(name)
    response = client.post(url) if name == 'logout' else client.get(url)
    assert response.status_code == expected_status


@pytest.mark.django_db
@pytest.mark.parametrize(
    'client_fixture, expected_status, expect_redirect_to_login',
    [
        (pytest.lazy_fixture('author_client'), HTTPStatus.OK, False),
        (Client(), HTTPStatus.FOUND, True),
    ]
)
def test_resume_my_list_access_combined(
    client_fixture: Client,
    expected_status: int,
    expect_redirect_to_login: bool
) -> None:
    url = reverse('user:resume_my_list')
    response = client_fixture.get(url)
    assert response.status_code == expected_status

    if expect_redirect_to_login:
        assert response.url.startswith(reverse('login'))

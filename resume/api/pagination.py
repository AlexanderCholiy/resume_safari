from rest_framework.pagination import PageNumberPagination

from .constants import (
    MAX_LOCATIONS_PER_REQUEST,
    MAX_SKILLS_PER_REQUEST,
    MAX_POSITIONS_PER_REQUEST,
    MAX_RESUMES_PER_REQUEST,
)


class LocationPagination(PageNumberPagination):
    page_size = MAX_LOCATIONS_PER_REQUEST


class SkillPagination(PageNumberPagination):
    page_size = MAX_SKILLS_PER_REQUEST


class PositionPagination(PageNumberPagination):
    page_size = MAX_POSITIONS_PER_REQUEST


class ResumePagination(PageNumberPagination):
    page_size = MAX_RESUMES_PER_REQUEST

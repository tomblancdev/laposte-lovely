import pytest
from rest_framework import status
from rest_framework.test import APIRequestFactory

from django_overtuned.user_tags.api.views import UserTagViewSet
from django_overtuned.user_tags.tests.factories import UserTagFactory
from django_overtuned.users.models import User


class TestUserTagViewSet:
    @pytest.fixture
    def api_rf(self) -> APIRequestFactory:
        return APIRequestFactory()

    def test_get_queryset_filters_by_user(
        self,
        user: User,
        api_rf: APIRequestFactory,
    ):
        """Test that users only see their own tags."""
        # Create tags for the user
        tag1 = UserTagFactory(user=user, name="personal")
        tag2 = UserTagFactory(user=user, name="work")

        # Create tags for another user
        other_user = UserTagFactory().user
        UserTagFactory(user=other_user, name="other")

        view = UserTagViewSet()
        request = api_rf.get("/fake-url/")
        request.user = user

        view.request = request

        queryset = view.get_queryset()

        assert tag1 in queryset
        assert tag2 in queryset
        assert queryset.count() == 2  # noqa: PLR2004

    def test_get_queryset_with_query_param(
        self,
        user: User,
        api_rf: APIRequestFactory,
    ):
        """Test filtering tags by name query parameter."""
        UserTagFactory(user=user, name="personal")
        UserTagFactory(user=user, name="work")
        UserTagFactory(user=user, name="project")

        view = UserTagViewSet()
        request = api_rf.get("/fake-url/?query=per")
        request.user = user

        view.request = request

        queryset = view.get_queryset()

        assert queryset.count() == 1
        assert queryset.first().name == "personal"

    def test_get_queryset_with_max_number_param(
        self,
        user: User,
        api_rf: APIRequestFactory,
    ):
        """Test limiting results with max_number parameter."""
        UserTagFactory(user=user, name="tag1")
        UserTagFactory(user=user, name="tag2")
        UserTagFactory(user=user, name="tag3")
        UserTagFactory(user=user, name="tag4")

        view = UserTagViewSet()
        request = api_rf.get("/fake-url/?max_number=2")
        request.user = user

        view.request = request

        queryset = view.get_queryset()

        assert len(list(queryset)) == 2  # noqa: PLR2004

    def test_get_queryset_with_query_and_max_number(
        self,
        user: User,
        api_rf: APIRequestFactory,
    ):
        """Test combining query and max_number parameters."""
        UserTagFactory(user=user, name="work-project")
        UserTagFactory(user=user, name="work-task")
        UserTagFactory(user=user, name="work-meeting")
        UserTagFactory(user=user, name="personal")

        view = UserTagViewSet()
        request = api_rf.get("/fake-url/?query=work&max_number=2")
        request.user = user

        view.request = request

        queryset = view.get_queryset()

        assert len(list(queryset)) == 2  # noqa: PLR2004
        for tag in queryset:
            assert "work" in tag.name

    def test_list_endpoint(self, user: User, api_rf: APIRequestFactory):
        """Test the list endpoint returns correct data."""
        tag1 = UserTagFactory(user=user, name="test-tag")

        view = UserTagViewSet.as_view({"get": "list"})
        request = api_rf.get("/api/user-tags/")
        request.user = user

        response = view(request)

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) == 1
        assert response.data[0]["name"] == "test-tag"
        assert response.data[0]["id"] == tag1.id
        assert "slug" in response.data[0]

from rest_framework.mixins import ListModelMixin
from rest_framework.viewsets import GenericViewSet

from django_overtuned.user_tags.models import UserTag

from .serializers import UserTagSerializer


class UserTagViewSet(ListModelMixin, GenericViewSet):
    serializer_class = UserTagSerializer
    queryset = UserTag.objects.all()

    def get_queryset(self, *args, **kwargs):
        # Only return tags for the current user
        assert isinstance(self.request.user.id, int)
        queryset = self.queryset.filter(user=self.request.user)

        # Filter by name query parameter
        query = self.request.GET.get("query", None)
        if query:
            queryset = queryset.filter(name__icontains=query)

        # Limit by max_number parameter
        max_number = self.request.GET.get("max_number", None)
        if max_number:
            try:
                limit = int(max_number)
                queryset = queryset[:limit]
            except ValueError:
                pass

        return queryset

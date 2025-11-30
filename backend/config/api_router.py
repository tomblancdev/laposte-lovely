from django.conf import settings
from django_overtuned.user_tags.api.views import UserTagViewSet
from django_overtuned.users.api.views import UserViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("user-tags", UserTagViewSet)


app_name = "api"
urlpatterns = router.urls

from django.conf import settings
from django_overtuned.emails.api.views import EmailAccountViewSet
from django_overtuned.emails.api.views import EmailAddressesViewSet
from django_overtuned.emails.api.views import EmailFolderPersonalizationViewSet
from django_overtuned.emails.api.views import EmailFolderViewSet
from django_overtuned.emails.api.views import EmailPersonalizationViewSet
from django_overtuned.emails.api.views import EmailViewSet
from django_overtuned.user_tags.api.views import UserTagViewSet
from django_overtuned.users.api.views import UserViewSet
from rest_framework.routers import DefaultRouter
from rest_framework.routers import SimpleRouter

router = DefaultRouter() if settings.DEBUG else SimpleRouter()

router.register("users", UserViewSet)
router.register("user-tags", UserTagViewSet)
router.register("email-accounts", EmailAccountViewSet, basename="emailaccount")
router.register("email-addresses", EmailAddressesViewSet, basename="emailaddresses")
router.register("emails", EmailViewSet, basename="email")
router.register("email-folders", EmailFolderViewSet, basename="emailfolder")
router.register(
    "email-personalizations",
    EmailPersonalizationViewSet,
    basename="emailpersonalization",
)
router.register(
    "email-folder-personalizations",
    EmailFolderPersonalizationViewSet,
    basename="emailfolderpersonalization",
)


app_name = "api"
urlpatterns = router.urls

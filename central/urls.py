from rest_framework.routers import SimpleRouter

from central.views import NotificationViewSet

router = SimpleRouter()
router.register('notifications', NotificationViewSet)

app_name = 'central'
urlpatterns = [] + router.urls

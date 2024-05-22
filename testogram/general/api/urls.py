from rest_framework.routers import SimpleRouter
from general.api.views import UserViewSet, PostViewSet, CommentsViewSet

router = SimpleRouter()
router.register(r'posts', PostViewSet, basename='posts')
router.register(r'comments', CommentsViewSet, basename='comments')
router.register(r'users', UserViewSet, basename='users')

urlpatterns = router.urls
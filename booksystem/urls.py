from rest_framework.routers import DefaultRouter
from .views import AuthorViewSet, BookViewSet, CategoryViewSet , BorrowViewSet

router = DefaultRouter()
router.register(r'authors', AuthorViewSet, basename='author')
router.register(r'books', BookViewSet, basename='book')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'borrowings', BorrowViewSet, basename='borrowing')


urlpatterns = router.urls
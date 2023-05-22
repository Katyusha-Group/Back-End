from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'carts', viewset=views.CartViewSet, basename='carts')
router.register(r'orders', viewset=views.OrderViewSet, basename='orders')
router.register(r'teacher-reviews/(?P<teacher_pk>\d+)', viewset=views.TeacherReviewViewSet, basename='teacher-reviews')
router.register(r'teacher-votes/(?P<teacher_pk>\d+)', viewset=views.TeacherVoteViewSet, basename='teacher-votes')

carts_router = routers.NestedSimpleRouter(router, r'carts', lookup='cart')
carts_router.register(r'items', viewset=views.CartItemViewSet, basename='cart-items')

reviews_router = routers.NestedSimpleRouter(router, r'teacher-reviews/(?P<teacher_pk>\d+)', lookup='teacher_review')
reviews_router.register(r'votes', viewset=views.ReviewVoteViewSet, basename='votes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(carts_router.urls)),
    path('', include(reviews_router.urls)),
]

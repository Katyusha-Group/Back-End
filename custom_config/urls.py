from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'shop/carts', viewset=views.CartViewSet, basename='carts')
router.register(r'shop/orders', viewset=views.OrderViewSet, basename='orders')
router.register(r'teacher-reviews/(?P<teacher_pk>\d+)', viewset=views.TeacherReviewViewSet, basename='teacher-reviews')
router.register(r'teacher-votes/(?P<teacher_pk>\d+)', viewset=views.TeacherVoteViewSet, basename='teacher-votes')
router.register(r'course-cart-order-info',
                viewset=views.CourseCartOrderInfoRetrieveViewSet,
                basename='course-cart-order-info')
router.register(r'notifications', viewset=views.WebNotificationViewSet, basename='notifications')


reviews_router = routers.NestedSimpleRouter(router, r'teacher-reviews/(?P<teacher_pk>\d+)', lookup='teacher_review')
reviews_router.register(r'votes', viewset=views.ReviewVoteViewSet, basename='votes')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(reviews_router.urls)),
    path('shop/get-prices/', views.GetPricesView.as_view(), name='get-prices'),
]

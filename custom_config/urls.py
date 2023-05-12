from django.urls import path
from django.urls.conf import include
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()
router.register(r'carts', viewset=views.CartViewSet, basename='carts')
router.register(r'orders', viewset=views.OrderViewSet, basename='orders')

carts_router = routers.NestedSimpleRouter(router, r'carts', lookup='cart')
carts_router.register(r'items', viewset=views.CartItemViewSet, basename='cart-items')

urlpatterns = [
    path('', include(router.urls)),
    path('', include(carts_router.urls)),
]

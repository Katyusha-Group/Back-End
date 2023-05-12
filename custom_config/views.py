from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated

from custom_config.models import Cart, CartItem, Order
from custom_config.serializers import CartSerializer, CartItemSerializer, \
    AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, CreateOrderSerializer


# Create your views here.
class CartViewSet(CreateModelMixin, RetrieveModelMixin, DestroyModelMixin, GenericViewSet):
    queryset = Cart.objects.prefetch_related('items', 'items__course').all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete', 'options', 'head']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        if self.request.method == 'PUT':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk'], 'request': self.request}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('course')


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'put', 'delete', 'options', 'head']
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(data=order)
        return Response(data=serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user_id=self.request.user.id)

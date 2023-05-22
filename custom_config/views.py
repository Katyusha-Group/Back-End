from django.contrib.auth import get_user_model
from django.shortcuts import render
from rest_framework import status
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, ListModelMixin, DestroyModelMixin
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from custom_config.models import Cart, CartItem, Order, TeacherReview
from custom_config.serializers import CartSerializer, CartItemSerializer, \
    AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer, \
    ModifyTeacherReviewSerializer, TeacherReviewSerializer
from university.models import Teacher


# Create your views here.
class CartViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'delete', 'options', 'head']
    queryset = Cart.objects.prefetch_related('items', 'items__course').all()
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]


class CartItemViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']
    permission_classes = [IsAuthenticated]

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return AddCartItemSerializer
        if self.request.method == 'PATCH':
            return UpdateCartItemSerializer
        return CartItemSerializer

    def get_serializer_context(self):
        return {'cart_id': self.kwargs['cart_pk'], 'request': self.request}

    def get_queryset(self):
        return CartItem.objects.filter(cart_id=self.kwargs['cart_pk']).select_related('course')


class OrderViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'head', 'options']

    def get_permissions(self):
        if self.request.method in ['PATCH', 'DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def create(self, request, *args, **kwargs):
        serializer = CreateOrderSerializer(data=request.data, context={'user_id': request.user.id})
        serializer.is_valid(raise_exception=True)
        order = serializer.save()
        serializer = OrderSerializer(order)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        if self.request.method == 'PATCH':
            return UpdateOrderSerializer
        return OrderSerializer

    def get_queryset(self):
        if self.request.user.is_staff:
            return Order.objects.all()
        return Order.objects.filter(user_id=self.request.user.id)


class TeacherReviewViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']
    permission_classes = [IsAuthenticated]

    def get_teacher(self):
        teacher_pk = self.kwargs['teacher_pk']
        teacher = Teacher.objects.get(pk=teacher_pk)
        return teacher

    def create(self, request, *args, **kwargs):
        context = {'teacher': self.get_teacher(), 'user': self.request.user, 'is_admin': self.request.user.is_staff}
        serializer = ModifyTeacherReviewSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        serializer = TeacherReviewSerializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return ModifyTeacherReviewSerializer
        return TeacherReviewSerializer

    def get_serializer_context(self):
        return {'teacher': self.get_teacher(), 'user': self.request.user, 'is_admin': self.request.user.is_staff}

    def get_queryset(self):
        return TeacherReview.objects.filter(teacher=self.get_teacher()).all()

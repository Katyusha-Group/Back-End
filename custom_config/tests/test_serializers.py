import pytest
from rest_framework import serializers

from custom_config.models import CartItem, Cart, OrderItem, Order
from custom_config.serializers import CartItemSerializer, CartSerializer, OrderItemSerializer, OrderSerializer, \
    CourseCartOrderInfoSerializer, AddCartItemSerializer, UpdateCartItemSerializer, CreateOrderSerializer, \
    ModifyReviewVoteSerializer, ModifyTeacherVoteSerializer, ModifyTeacherReviewSerializer
from model_bakery import baker

from university.models import Course

pytestmark = pytest.mark.django_db


class TestSerializers:
    def test_cart_item_serializer(self, course_instance):
        cart_item = baker.make(CartItem, course=course_instance)
        serializer = CartItemSerializer(instance=cart_item)
        data = serializer.data
        assert str(data['id']) == str(cart_item.id)
        assert data['contain_telegram'] == cart_item.contain_telegram
        assert data['contain_sms'] == cart_item.contain_sms
        assert data['contain_email'] == cart_item.contain_email

    def test_cart_serializer(self):
        cart = baker.make(Cart)
        serializer = CartSerializer(instance=cart)
        data = serializer.data
        assert str(data['id']) == str(cart.id)

    def test_order_item_serializer(self, course_instance):
        order_item = baker.make(OrderItem, course=course_instance)
        serializer = OrderItemSerializer(instance=order_item)
        data = serializer.data
        assert str(data['id']) == str(order_item.id)
        assert data['contain_telegram'] == order_item.contain_telegram
        assert data['contain_sms'] == order_item.contain_sms
        assert data['contain_email'] == order_item.contain_email

    def test_order_serializer(self):
        order = baker.make(Order)
        serializer = OrderSerializer(instance=order)
        data = serializer.data
        assert str(data['id']) == str(order.id)
        assert data['payment_method'] == order.payment_method
        assert data['payment_status'] == order.payment_status

    def test_cart_item_serializer_method_fields(self, course_instance):
        cart_item = baker.make(CartItem, course=course_instance)
        serializer = CartItemSerializer(instance=cart_item)
        data = serializer.data
        assert data['price'] == cart_item.get_item_price()

    def test_cart_serializer_method_fields(self):
        cart = baker.make(Cart)
        serializer = CartSerializer(instance=cart)
        data = serializer.data
        assert data['total_price'] == sum([item.get_item_price() for item in cart.items.all()])
        assert data['total_number'] == cart.items.count()

    def test_get_course_from_cart(self, cart_instance, course_instance):
        cart_item = CartItem.objects.create(cart=cart_instance, course=course_instance)
        serializer = CourseCartOrderInfoSerializer(context={'cart_id': cart_instance.id})
        result = serializer.get_course_from_cart(course_instance)
        assert result == cart_item

    def test_add_cart_item_serializer_validation(self):
        serializer = AddCartItemSerializer(data={})
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert 'complete_course_number' in exc_info.value.detail

    def test_create_order_serializer_validation(self):
        serializer = CreateOrderSerializer(data={})
        with pytest.raises(serializers.ValidationError) as exc_info:
            serializer.is_valid(raise_exception=True)
        assert 'payment_method' in exc_info.value.detail

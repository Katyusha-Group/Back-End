from django.db import transaction

from rest_framework import serializers

from accounts.api.serializers import SimpleUserSerializer
from custom_config.models import Cart, CartItem, Order, OrderItem, TeacherReview

from university.models import Course
from university.serializers import SimpleCourseSerializer

from custom_config.scripts.get_item_price import get_item_price
from university.scripts.get_or_create import get_course
from utils import project_variables


class CartItemSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    def get_price(self, obj: CartItem):
        return get_item_price(obj)

    class Meta:
        model = CartItem
        fields = ['id', 'course', 'contain_telegram', 'contain_sms', 'contain_email', 'price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    def save(self, **kwargs):
        contain_telegram = self.validated_data['contain_telegram']
        contain_sms = self.validated_data['contain_sms']
        contain_email = self.validated_data['contain_email']

        if not contain_telegram and not contain_sms and not contain_email:
            self.instance.delete()
            return

        self.instance.contain_telegram = contain_telegram
        self.instance.contain_sms = contain_sms
        self.instance.contain_email = contain_email
        self.instance.save()
        return self.instance

    class Meta:
        model = CartItem
        fields = ['contain_telegram', 'contain_sms', 'contain_email']


class AddCartItemSerializer(serializers.ModelSerializer):
    complete_course_number = serializers.CharField(write_only=True)

    def validate(self, attrs):
        complete_course_number = attrs['complete_course_number']
        base_course_id, class_gp = complete_course_number.split('_')
        contain_telegram = attrs['contain_telegram']
        contain_sms = attrs['contain_sms']
        contain_email = attrs['contain_email']
        if not Course.objects.filter(base_course_id=base_course_id, class_gp=class_gp).exists():
            raise serializers.ValidationError('This course does not exist.')
        if not contain_email and not contain_sms and not contain_telegram:
            raise serializers.ValidationError('You must choose at least one notification method.')
        course_id = get_course(course_code=complete_course_number, semester=project_variables.CURRENT_SEMESTER).id
        attrs['course_id'] = course_id
        return attrs

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        complete_course_number = self.validated_data['complete_course_number']
        course_id = get_course(course_code=complete_course_number, semester=project_variables.CURRENT_SEMESTER).id
        contain_telegram = self.validated_data['contain_telegram']
        contain_sms = self.validated_data['contain_sms']
        contain_email = self.validated_data['contain_email']

        try:
            cart_item = CartItem.objects.get(
                cart_id=cart_id, course_id=course_id)
            cart_item.contain_telegram = contain_telegram
            cart_item.contain_sms = contain_sms
            cart_item.contain_email = contain_email
            cart_item.save()
            self.instance = cart_item
        except CartItem.DoesNotExist:
            if 'complete_course_number' in self.validated_data:
                del self.validated_data['complete_course_number']
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'complete_course_number', 'contain_telegram', 'contain_sms', 'contain_email']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)
    total_number = serializers.SerializerMethodField(read_only=True)

    def get_total_number(self, obj: Cart):
        return obj.items.count()

    def get_total_price(self, obj: Cart):
        return sum([get_item_price(item) for item in obj.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_number']


class OrderItemSerializer(serializers.ModelSerializer):
    course = SimpleCourseSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'course', 'contain_telegram', 'contain_sms', 'contain_email', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_number = serializers.SerializerMethodField(read_only=True)

    def get_total_number(self, obj: Cart):
        return obj.items.count()

    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'payment_status', 'user', 'items', 'total_number']


class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField(write_only=True)

    def validate_cart_id(self, value):
        if not Cart.objects.filter(id=value).exists():
            raise serializers.ValidationError('This cart does not exist.')
        if Cart.objects.get(id=value).items.count() == 0:
            raise serializers.ValidationError('This cart is empty.')
        return value

    def save(self, **kwargs):
        with transaction.atomic():
            user_id = self.context['user_id']
            cart_id = self.validated_data['cart_id']
            cart = Cart.objects.get(id=cart_id)
            order = Order.objects.create(user_id=user_id)
            order_items = [
                OrderItem(
                    order=order,
                    course=item.course,
                    contain_telegram=item.contain_telegram,
                    contain_sms=item.contain_sms,
                    contain_email=item.contain_email,
                    unit_price=get_item_price(item)
                ) for item in cart.items.select_related('course').all()
            ]
            OrderItem.objects.bulk_create(order_items)
            cart.delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class TeacherReviewSerializer(serializers.ModelSerializer):
    user = SimpleUserSerializer()

    class Meta:
        model = TeacherReview
        fields = ['user', 'vote', 'text']

from rest_framework import serializers

from custom_config.models import Cart, CartItem
from university.models import Course
from university.serializers import SimpleCourseSerializer

from custom_config.scripts.get_item_price import get_item_price


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
    course_id = serializers.IntegerField(write_only=True)

    def validate(self, attrs):
        course_id = attrs['course_id']
        contain_telegram = attrs['contain_telegram']
        contain_sms = attrs['contain_sms']
        contain_email = attrs['contain_email']
        # if not self.context['request'].user.courses.filter(id=course_id).exists():
        #     raise serializers.ValidationError('You have not chosen this course yet.')
        if not Course.objects.filter(id=course_id).exists():
            raise serializers.ValidationError('This course does not exist.')
        if not contain_email and not contain_sms and not contain_telegram:
            raise serializers.ValidationError('You must choose at least one notification method.')
        return attrs

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        course_id = self.validated_data['course_id']
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
            self.instance = CartItem.objects.create(
                cart_id=cart_id, **self.validated_data)

        return self.instance

    class Meta:
        model = CartItem
        fields = ['id', 'course_id', 'contain_telegram', 'contain_sms', 'contain_email']


class CartSerializer(serializers.ModelSerializer):
    id = serializers.UUIDField(read_only=True)
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, obj: Cart):
        return sum([get_item_price(item) for item in obj.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price']

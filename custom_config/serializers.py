from django.db import transaction

from rest_framework import serializers

from accounts.api.serializers import SimpleUserSerializer
from custom_config.models import Cart, CartItem, Order, OrderItem, TeacherReview, TeacherVote, ReviewVote

from university.models import Course
from university.serializers import ShoppingCourseSerializer

from custom_config.scripts.get_item_price import get_item_price
from university.scripts.get_or_create import get_course
from utils import project_variables


class CartItemSerializer(serializers.ModelSerializer):
    course = ShoppingCourseSerializer(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    teacher_image = serializers.ImageField(source='course.teacher.image', read_only=True)

    def get_price(self, obj: CartItem):
        return get_item_price(obj)

    class Meta:
        model = CartItem
        fields = ['id', 'course', 'contain_telegram', 'contain_sms', 'contain_email', 'price', 'teacher_image']


class UpdateCartItemViewSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, obj: CartItem):
        return get_item_price(obj)

    class Meta:
        model = CartItem
        fields = ['contain_telegram', 'contain_sms', 'contain_email', 'total_price']


class UpdateCartItemSerializer(serializers.ModelSerializer):
    def update(self, instance, validated_data):
        contain_telegram = validated_data['contain_telegram']
        contain_sms = validated_data['contain_sms']
        contain_email = validated_data['contain_email']

        if not contain_telegram and not contain_sms and not contain_email:
            instance.delete()
            return

        instance.contain_telegram = contain_telegram
        instance.contain_sms = contain_sms
        instance.contain_email = contain_email
        instance.save()
        return instance

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
            cart_item = CartItem.objects.get(cart_id=cart_id, course_id=course_id)
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
    course = ShoppingCourseSerializer(read_only=True)

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
        user_id = self.context['user_id']
        cart_id = self.validated_data['cart_id']
        cart = Cart.objects.get(id=cart_id)
        for item in cart.items.select_related('course').all():
            if Order.objects.filter(user_id=user_id, items__course=item.course).exists():
                raise serializers.ValidationError(
                    'You have already course with with id {}. Delete it  from your cart and try again.'.format(
                        item.course.id))
        with transaction.atomic():
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


class BaseFlatteningSerializer(serializers.ModelSerializer):
    def to_representation(self, obj):
        representation = super().to_representation(obj)
        if 'user' in representation:
            user_representation = representation.pop('user')
            for sub_key in user_representation:
                representation[sub_key] = user_representation[sub_key]
            if self.context.get('is_admin'):
                return representation
            # TODO: Check if you want to show id to every one or just the admin
            # if 'id' in representation:
            #     representation.pop('id')
            return representation


class ReviewVoteSerializer(BaseFlatteningSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = ReviewVote
        fields = ['id', 'user', 'vote', ]


class ModifyReviewVoteSerializer(serializers.ModelSerializer):
    def validate_vote(self, value):
        if value > 1 or value < -1:
            raise serializers.ValidationError('You must send a vote between -1 and 1.')
        return value

    def save(self, **kwargs):
        user = self.context.get('user')
        review = self.context.get('review')
        vote = self.validated_data['vote']

        review_vote, _ = ReviewVote.objects.get_or_create(user=user, review=review)
        review_vote.vote = vote
        review_vote.save()
        self.instance = review_vote
        return self.instance

    class Meta:
        model = ReviewVote
        fields = ['vote', ]


class TeacherVoteSerializer(BaseFlatteningSerializer):
    user = SimpleUserSerializer(read_only=True)

    class Meta:
        model = TeacherVote
        fields = ['id', 'user', 'vote', ]


class ModifyTeacherVoteSerializer(serializers.ModelSerializer):
    def validate_vote(self, value):
        if value > 1 or value < -1:
            raise serializers.ValidationError('You must send a vote between -1 and 1.')
        return value

    def save(self, **kwargs):
        user = self.context.get('user')
        teacher = self.context.get('teacher')
        vote = self.validated_data['vote']

        teacher_vote, _ = TeacherVote.objects.get_or_create(user=user, teacher=teacher)
        teacher_vote.vote = vote
        teacher_vote.save()
        self.instance = teacher_vote
        return self.instance

    class Meta:
        model = TeacherVote
        fields = ['vote', ]


class TeacherReviewSerializer(BaseFlatteningSerializer):
    user = SimpleUserSerializer(read_only=True)
    votes = ReviewVoteSerializer(many=True, read_only=True)
    total_votes_count = serializers.SerializerMethodField(read_only=True)
    total_votes_score = serializers.SerializerMethodField(read_only=True)
    total_up_vote_count = serializers.SerializerMethodField(read_only=True)
    total_down_vote_count = serializers.SerializerMethodField(read_only=True)

    def get_total_votes_count(self, teacher_review: TeacherReview):
        return teacher_review.votes.count()

    def get_total_votes_score(self, teacher_review: TeacherReview):
        return sum(vote.vote for vote in teacher_review.votes.all())

    def get_total_up_vote_count(self, teacher_review: TeacherReview):
        return teacher_review.votes.filter(vote=1).count()

    def get_total_down_vote_count(self, teacher_review: TeacherReview):
        return teacher_review.votes.filter(vote=-1).count()

    class Meta:
        model = TeacherReview
        fields = ['id', 'user', 'text', 'votes',
                  'total_votes_count', 'total_votes_score',
                  'total_up_vote_count', 'total_down_vote_count']


class ModifyTeacherReviewSerializer(serializers.ModelSerializer):
    def validate_text(self, value):
        if value is None or len(value) == 0:
            raise serializers.ValidationError('You need to fill in the text of review.')
        return value

    def save(self, **kwargs):
        user = self.context.get('user')
        teacher = self.context.get('teacher')
        text = self.validated_data['text']

        teacher_review = TeacherReview.objects.create(user=user, teacher=teacher)
        teacher_review.text = text
        teacher_review.save()
        self.instance = teacher_review
        return self.instance

    class Meta:
        model = TeacherReview
        fields = ['text', ]

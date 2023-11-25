from django.db import transaction

from rest_framework import serializers

from accounts.serializers import SimpleUserSerializer
from botapp.models import User_telegram
from custom_config.models import Cart, CartItem, Order, OrderItem, TeacherReview, TeacherVote, ReviewVote, \
    WebNotification
from custom_config.signals import order_created

from university.models import Course
from university.serializers import ShoppingCourseSerializer

from university.scripts.get_or_create import get_course
from utils.variables import project_variables
from utils.telegram.telegram_functions import get_bot_url


class CartItemSerializer(serializers.ModelSerializer):
    course = ShoppingCourseSerializer(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)

    def get_price(self, obj: CartItem):
        return obj.get_item_price()

    class Meta:
        model = CartItem
        fields = ['id', 'course', 'contain_telegram', 'contain_sms', 'contain_email', 'price']


class CartItemsViewSerializer(serializers.ModelSerializer):
    total_price = serializers.SerializerMethodField(read_only=True)

    def get_total_price(self, obj: CartItem):
        return obj.get_item_price()

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
    complete_course_number = serializers.CharField(write_only=True, min_length=10, max_length=10)

    def validate(self, attrs):
        complete_course_number = attrs['complete_course_number']
        base_course_id, class_gp = complete_course_number.split('_')
        contain_telegram = attrs['contain_telegram']
        contain_sms = attrs['contain_sms']
        contain_email = attrs['contain_email']
        user = self.context['request'].user
        if not Course.objects.filter(base_course_id=base_course_id, class_gp=class_gp,
                                     semester=project_variables.CURRENT_SEMESTER).exists():
            raise serializers.ValidationError({'course': 'درس مورد نظر یافت نشد.'})
        if not contain_email and not contain_sms and not contain_telegram:
            raise serializers.ValidationError({'notification': 'حداقل یکی از روش های ارتباطی را انتخاب کنید.'})
        course = get_course(course_code=complete_course_number, semester=project_variables.CURRENT_SEMESTER)
        order_item = OrderItem.get_same_items_with_same_course_user(user=user, course=course)
        if order_item:
            if contain_telegram and order_item.contain_telegram or \
                    contain_sms and order_item.contain_sms or \
                    contain_email and order_item.contain_email:
                raise serializers.ValidationError(
                    {'order': 'این درس با این روش اطلاع رسانی، در سفارش های شما ثبت شده است.'})
        attrs['course_id'] = course.id
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
        return sum([item.get_item_price() for item in obj.items.all()])

    class Meta:
        model = Cart
        fields = ['id', 'items', 'total_price', 'total_number']


class OrderItemSerializer(serializers.ModelSerializer):
    course_code = serializers.SerializerMethodField(read_only=True)

    def get_course_code(self, obj: OrderItem):
        return str(obj.course_number) + '_' + obj.class_gp

    class Meta:
        model = OrderItem
        fields = ['id', 'course_code', 'contain_telegram', 'contain_sms', 'contain_email', 'unit_price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    total_number = serializers.SerializerMethodField(read_only=True)
    placed_at = serializers.SerializerMethodField(read_only=True)

    def get_placed_at(self, obj: Order):
        return obj.jalali_placed_at

    def get_total_number(self, obj: Cart):
        return obj.items.count()

    class Meta:
        model = Order
        fields = ['id', 'placed_at', 'ref_code', 'payment_method', 'payment_status', 'user', 'items', 'total_number']


class CreateOrderSerializer(serializers.Serializer):
    payment_method = serializers.ChoiceField(choices=Order.PAYMENT_METHOD_CHOICES, write_only=True)

    def validate(self, attrs):
        user = self.context['user']
        user_carts = Cart.get_user_available_carts(user=user)
        if not user_carts.exists():
            raise serializers.ValidationError({'cart': 'امکان ثبت سفارش وجود ندارد. سبد خرید مورد نظر یافت نشد.'})
        cart = user_carts.first()
        if cart.items.count() == 0:
            raise serializers.ValidationError({'cart': 'امکان ثبت سفارش وجود ندارد. سبد خرید شما خالی است.'})
        # # Check for Telegram activation
        # for item in cart.items.all():
        #     if item.contain_telegram and not User_telegram.objects.filter(email=user.email).exists():
        #         raise serializers.ValidationError(
        #             {
        #                 'telegram': 'امکان ثبت سفارش وجود ندارد. شما تلگرام خود را فعال نکرده اید.',
        #                 'telegram_link': get_bot_url(csrftoken=self.context['csrftoken'],
        #                                              token=self.context['token'])
        #             }
        #         )
        payment_method = attrs['payment_method']
        if payment_method == Order.PAY_WALLET:
            if cart.total_price() > user.wallet.balance:
                raise serializers.ValidationError(
                    {'wallet': 'امکان ثبت سفارش وجود ندارد. موجودی کیف پول شما کافی نیست.'})
        return attrs

    def save(self, **kwargs):
        user = self.context['user']
        cart = Cart.get_user_available_carts(user=user).first()
        with transaction.atomic():
            if self.validated_data['payment_method'] == Order.PAY_WALLET:
                order = Order.objects.create(user_id=user.id, payment_method=self.validated_data['payment_method'],
                                             payment_status=Order.PAYMENT_STATUS_COMPLETED)
            else:
                order = Order.objects.create(user_id=user.id, payment_method=self.validated_data['payment_method'])
            order_items = [
                OrderItem(
                    order=order,
                    course=item.course,
                    class_gp=item.course.class_gp,
                    course_number=item.course.base_course.course_number,
                    contain_telegram=item.contain_telegram,
                    contain_sms=item.contain_sms,
                    contain_email=item.contain_email,
                    unit_price=item.get_item_price()
                ) for item in cart.items.select_related('course__base_course').all()
            ]
            OrderItem.objects.bulk_create(order_items)
            order_created.send_robust(sender=Order, order=order, total_price=order.total_price())
            cart.delete()
            return order


class UpdateOrderSerializer(serializers.ModelSerializer):
    class Meta:
        model = Order
        fields = ['payment_status']


class CourseCartOrderInfoSerializer(serializers.ModelSerializer):
    contain_telegram = serializers.SerializerMethodField(read_only=True)
    contain_sms = serializers.SerializerMethodField(read_only=True)
    contain_email = serializers.SerializerMethodField(read_only=True)
    price = serializers.SerializerMethodField(read_only=True)
    name = serializers.CharField(source='base_course.name', read_only=True)

    def get_course_from_cart(self, course):
        cart_id = self.context.get('cart_id')
        if cart_id is None:
            raise serializers.ValidationError('You need to send cart_id in context.')
        cart = Cart.objects.filter(id=cart_id).first()
        if cart is None:
            raise serializers.ValidationError('Cart not found.')
        course_cart_item = cart.items.filter(course=course).first()
        return course_cart_item

    def get_contain_telegram(self, course: Course):
        course_cart_item = self.get_course_from_cart(course)
        if course_cart_item is not None:
            if course_cart_item.contain_telegram:
                return 'C'
        user = self.context.get('user')
        if user.orders.filter(items__course=course, items__contain_telegram=True).first():
            return 'O'
        return 'N'

    def get_contain_sms(self, course: Course):
        course_cart_item = self.get_course_from_cart(course)
        if course_cart_item is not None:
            if course_cart_item.contain_sms:
                return 'C'
        user = self.context.get('user')
        if user.orders.filter(items__course=course, items__contain_sms=True).first():
            return 'O'
        return 'N'

    def get_contain_email(self, course: Course):
        course_cart_item = self.get_course_from_cart(course)
        if course_cart_item is not None:
            if course_cart_item.contain_email:
                return 'C'
        user = self.context.get('user')
        if user.orders.filter(items__course=course, items__contain_email=True).first():
            return 'O'
        return 'N'

    def get_price(self, course: Course):
        course_cart_item = self.get_course_from_cart(course)
        if course_cart_item is not None:
            return course_cart_item.get_item_price()
        return 0

    class Meta:
        model = Course
        fields = ['name', 'price', 'contain_telegram', 'contain_sms',
                  'contain_email']


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


class WebNotificationSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(read_only=True)
    title = serializers.CharField(read_only=True)
    text = serializers.CharField(read_only=True)
    applied_at = serializers.SerializerMethodField(read_only=True)
    is_read = serializers.BooleanField()

    def get_applied_at(self, web_notification: WebNotification):
        return web_notification.jalali_applied_at

    class Meta:
        model = WebNotification
        fields = ['id', 'title', 'text', 'applied_at', 'is_read']

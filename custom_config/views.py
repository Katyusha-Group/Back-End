from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.viewsets import ModelViewSet
from rest_framework.permissions import IsAuthenticated, IsAdminUser

from custom_config.models import Cart, CartItem, Order, TeacherReview, TeacherVote, ReviewVote
from custom_config.serializers import CartSerializer, CartItemSerializer, \
    AddCartItemSerializer, UpdateCartItemSerializer, OrderSerializer, CreateOrderSerializer, UpdateOrderSerializer, \
    TeacherVoteSerializer, ModifyTeacherVoteSerializer, ModifyTeacherReviewSerializer, TeacherReviewSerializer, \
    ModifyReviewVoteSerializer, ReviewVoteSerializer, UpdateCartItemViewSerializer, CourseCartOrderInfoSerializer
from university.models import Teacher, Course
from university.scripts.get_or_create import get_course
from utils import project_variables


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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'cart_id': self.kwargs['cart_pk'], 'request': self.request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.save()
        serializer = UpdateCartItemViewSerializer(instance)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data,
                                         context={'cart_id': self.kwargs['cart_pk'], 'request': self.request})
        serializer.is_valid(raise_exception=True)
        instance = serializer.update(self.get_object(), serializer.validated_data)
        serializer = UpdateCartItemViewSerializer(instance)
        return Response(serializer.data, status=status.HTTP_200_OK)

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
        serializer = CreateOrderSerializer(data=request.data,
                                           context={'user_id': request.user.id, 'user': request.user})
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


class CourseCartOrderInfoRetrieveViewSet(ModelViewSet):
    http_method_names = ['get', 'options', 'head']
    serializer_class = CourseCartOrderInfoSerializer
    permission_classes = [IsAuthenticated]

    def get_serializer_context(self):
        return {'user': self.request.user, 'cart_id': self.request.query_params.get('cart_id', None), }

    def get_queryset(self):
        complete_course_number = self.request.query_params.get('complete_course_number', None)
        if complete_course_number is None:
            raise ValidationError('You need to send complete_course_number as query string.')
        course = get_course(course_code=complete_course_number, semester=project_variables.CURRENT_SEMESTER)
        if course is None:
            raise ValidationError('Course not found.')
        return Course.objects.filter(id=course.id).prefetch_related('order_items__order', 'cart_items')


class GetPricesView(APIView):
    http_method_names = ['get', 'options', 'head']

    def get(self, request, *args, **kwargs):
        data = {
            'T': project_variables.TELEGRAM_PRICE,
            'S': project_variables.SMS_PRICE,
            'E': project_variables.EMAIL_PRICE,
        }
        return Response(data, status=status.HTTP_200_OK)


class BaseVoteReviewViewSet(ModelViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.objects = None
        self.modification_serializer = None
        self.show_serializer = None

    def get_teacher(self):
        teacher_pk = self.kwargs.get('teacher_pk')
        teacher = Teacher.objects.get(pk=teacher_pk)
        return teacher

    def create(self, request, *args, **kwargs):
        context = {'teacher': self.get_teacher(), 'user': self.request.user, 'is_admin': self.request.user.is_staff}
        serializer = self.modification_serializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        review = serializer.save()
        serializer = self.show_serializer(review)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in ['DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        return {'teacher': self.get_teacher(), 'user': self.request.user, 'is_admin': self.request.user.is_staff}

    def get_queryset(self):
        return self.objects.filter(teacher=self.get_teacher()).all()


class TeacherVoteViewSet(BaseVoteReviewViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.objects = TeacherVote.objects
        self.modification_serializer = ModifyTeacherVoteSerializer
        self.show_serializer = TeacherVoteSerializer

    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return self.modification_serializer
        return self.show_serializer

    def list(self, request, *args, **kwargs):
        data = self.objects.filter(teacher=self.get_teacher())
        total_score = sum([entry.vote for entry in data.only('vote')])
        up_votes = data.filter(vote=1).count()
        down_votes = data.filter(vote=-1).count()
        serializer = self.show_serializer(data, many=True)
        new_data = {
            'total_count': len(serializer.data),
            'total_score': total_score,
            'up_votes': up_votes,
            'down_votes': down_votes,
            'data': serializer.data,
        }
        return Response(new_data)


class TeacherReviewViewSet(BaseVoteReviewViewSet):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.objects = TeacherReview.objects
        self.modification_serializer = ModifyTeacherReviewSerializer
        self.show_serializer = TeacherReviewSerializer

    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return self.modification_serializer
        return self.show_serializer

    def get_permissions(self):
        if self.request.method in ['DELETE', 'PATCH']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def list(self, request, *args, **kwargs):
        data = self.objects.filter(teacher=self.get_teacher()).all()
        serializer = self.show_serializer(data, many=True)
        new_data = {'total_count': len(serializer.data), 'data': serializer.data}
        return Response(new_data)


class ReviewVoteViewSet(ModelViewSet):
    http_method_names = ['get', 'post', 'patch', 'delete', 'options', 'head']

    def get_serializer_class(self):
        if self.request.method == 'POST' or self.request.method == 'PATCH':
            return ModifyReviewVoteSerializer
        return ReviewVoteSerializer

    def get_review(self):
        review_pk = self.kwargs.get('teacher_review_pk')
        review = TeacherReview.objects.get(pk=review_pk)
        return review

    def create(self, request, *args, **kwargs):
        context = {'review': self.get_review(), 'user': self.request.user, 'is_admin': self.request.user.is_staff}
        serializer = ModifyReviewVoteSerializer(data=request.data, context=context)
        serializer.is_valid(raise_exception=True)
        vote = serializer.save()
        serializer = ReviewVoteSerializer(vote)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def get_permissions(self):
        if self.request.method in ['DELETE']:
            return [IsAdminUser()]
        return [IsAuthenticated()]

    def get_serializer_context(self):
        return {'review': self.get_review(), 'user': self.request.user, 'is_admin': self.request.user.is_staff}

    def get_queryset(self):
        return ReviewVote.objects.filter(review=self.get_review()).all()

    def list(self, request, *args, **kwargs):
        data = ReviewVote.objects.filter(review=self.get_review())
        total_score = sum([entry.vote for entry in data.only('vote')])
        up_votes = data.filter(vote=1).count()
        down_votes = data.filter(vote=-1).count()
        serializer = ReviewVoteSerializer(data, many=True)
        new_data = {
            'total_count': len(serializer.data),
            'total_score': total_score,
            'up_votes': up_votes,
            'down_votes': down_votes,
            'data': serializer.data,
        }
        return Response(new_data)

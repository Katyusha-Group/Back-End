import uuid

import pytest
from django.db import models, IntegrityError
from model_bakery import baker
from django.core.exceptions import ValidationError

from core import settings
from custom_config.models import ModelTracker, FieldTracker, Cart, CartItem, OrderItem, Order
from university.models import AllowedDepartment, CourseTimePlace, ExamTimePlace, BaseCourse, Course
from utils.model_functions.date import get_persian_date
from utils.variables import project_variables

pytestmark = pytest.mark.django_db


class TestModelTrackerModel:
    @pytest.fixture
    def model_tracker_instance(self):
        return baker.make(ModelTracker)

    def test_return_str(self):
        base_course = baker.make(BaseCourse, course_number='1234567', name='test')
        course = baker.make(Course, base_course=base_course)
        allowed_department = baker.make(AllowedDepartment, course=course)
        course_time_place = baker.make(CourseTimePlace, course=course)
        exam_time_place = baker.make(ExamTimePlace, course=course)
        model_tracker = baker.make(ModelTracker, instance_id=allowed_department.id, model=AllowedDepartment.__name__)
        model_tracker1 = baker.make(ModelTracker, instance_id=course_time_place.id, model=CourseTimePlace.__name__)
        model_tracker2 = baker.make(ModelTracker, instance_id=exam_time_place.id, model=ExamTimePlace.__name__)

        assert str(model_tracker) == str(allowed_department)
        assert str(model_tracker1) == str(course_time_place)
        assert str(model_tracker2) == str(exam_time_place)

    def test_model_max_length(self, model_tracker_instance):
        max_length = model_tracker_instance._meta.get_field('model').max_length
        assert max_length == 255

    def test_action_choices(self, model_tracker_instance):
        action_choices = model_tracker_instance._meta.get_field('action').choices
        assert action_choices == (('C', 'ایجاد'),
                                  ('U', 'بروزرسانی'),
                                  ('D', 'حذف'),)

    def test_status_choices(self, model_tracker_instance):
        status_choices = model_tracker_instance._meta.get_field('status').choices
        assert status_choices == (('U', 'اعمال نشده'),
                                  ('C', 'اعمال شده'),)

    def test_course_number_max_length(self, model_tracker_instance):
        max_length = model_tracker_instance._meta.get_field('course_number').max_length
        assert max_length == 11

    def test_course_name_max_length(self, model_tracker_instance):
        max_length = model_tracker_instance._meta.get_field('course_name').max_length
        assert max_length == 255

    def test_applied_at_auto_now_add(self, model_tracker_instance):
        assert model_tracker_instance._meta.get_field('applied_at').auto_now_add is True


class TestFieldTracker:
    @pytest.fixture
    def model_tracker_instance(self):
        return baker.make(ModelTracker)

    @pytest.fixture
    def field_tracker_instance(self):
        return baker.make(FieldTracker)

    def test_return_str(self, field_tracker_instance):
        assert str(field_tracker_instance) == str(field_tracker_instance.field) + ' : ' + str(
            field_tracker_instance.value)

    def test_field_max_length(self, field_tracker_instance):
        max_length = field_tracker_instance._meta.get_field('field').max_length
        assert max_length == 255

    def test_value_max_length(self, field_tracker_instance):
        max_length = field_tracker_instance._meta.get_field('value').max_length
        assert max_length == 1023

    def test_model_tracker_is_foreign_key(self, field_tracker_instance):
        tracker = field_tracker_instance._meta.get_field('tracker')
        assert isinstance(tracker, models.ForeignKey)

    def test_tracker_on_delete(self, field_tracker_instance):
        tracker = field_tracker_instance._meta.get_field('tracker')
        assert tracker.remote_field.on_delete == models.CASCADE


class TestCartModel:
    @pytest.fixture
    def cart_instance(self, user_instance):
        return baker.make(Cart, user=user_instance)

    def test_return_str(self, cart_instance):
        assert str(cart_instance) == str(cart_instance.id) + ' : ' + str(cart_instance.created_at)

    def test_user_is_foreign_key(self, cart_instance):
        user = cart_instance._meta.get_field('user')
        assert isinstance(user, models.ForeignKey)

    def test_user_on_delete(self, cart_instance):
        user = cart_instance._meta.get_field('user')
        assert user.remote_field.on_delete == models.CASCADE

    def test_id_is_uuid64(self, cart_instance):
        cart_id = cart_instance._meta.get_field('id')
        assert isinstance(cart_id, models.UUIDField)
        assert cart_id.primary_key is True
        assert cart_id.default == uuid.uuid4

    def test_user_null_false(self, cart_instance):
        user = cart_instance._meta.get_field('user')
        assert user.null is False

    def test_user_blank_false(self, cart_instance):
        user = cart_instance._meta.get_field('user')
        assert user.blank is False

    def test_created_at_auto_now_add(self, cart_instance):
        assert cart_instance._meta.get_field('created_at').auto_now_add is True

    def test_total_price(self, cart_instance, courses):
        cart_item_1 = baker.make(CartItem, cart=cart_instance, contain_email=True, contain_sms=True,
                                 contain_telegram=True, course=courses[0])
        cart_item_2 = baker.make(CartItem, cart=cart_instance, contain_email=False, contain_sms=True,
                                 contain_telegram=True, course=courses[1])
        cart_item_3 = baker.make(CartItem, cart=cart_instance, contain_email=True, contain_sms=False,
                                 contain_telegram=True, course=courses[2])
        cart_item_4 = baker.make(CartItem, cart=cart_instance, contain_email=True, contain_sms=True,
                                 contain_telegram=False, course=courses[3])

        total_price = cart_item_1.get_item_price() + cart_item_2.get_item_price() + \
                      cart_item_3.get_item_price() + cart_item_4.get_item_price()
        assert cart_instance.total_price() == total_price * project_variables.TAX + total_price


class TestCartItemModel:
    @pytest.fixture
    def cart_instance(self, user_instance):
        return baker.make(Cart, user=user_instance)

    @pytest.fixture
    def cart_item_instance(self, cart_instance, courses):
        return baker.make(CartItem, cart=cart_instance, course=courses[0])

    def test_return_str(self, cart_item_instance):
        assert str(cart_item_instance) == str(cart_item_instance.cart) + ' : ' + str(cart_item_instance.course)

    def test_cart_is_foreign_key(self, cart_item_instance):
        cart = cart_item_instance._meta.get_field('cart')
        assert isinstance(cart, models.ForeignKey)

    def test_cart_on_delete(self, cart_item_instance):
        cart = cart_item_instance._meta.get_field('cart')
        assert cart.remote_field.on_delete == models.CASCADE

    def test_course_on_delete(self, cart_item_instance):
        course = cart_item_instance._meta.get_field('course')
        assert course.remote_field.on_delete == models.CASCADE

    def test_course_is_foreign_key(self, cart_item_instance):
        course = cart_item_instance._meta.get_field('course')
        assert isinstance(course, models.ForeignKey)

    def test_cart_related_name(self, cart_item_instance):
        cart = cart_item_instance._meta.get_field('cart')
        assert cart.remote_field.related_name == 'items'

    def test_course_related_name(self, cart_item_instance):
        course = cart_item_instance._meta.get_field('course')
        assert course.remote_field.related_name == 'cart_items'

    def test_contain_telegram_default_false(self, cart_item_instance):
        contain_telegram = cart_item_instance._meta.get_field('contain_telegram')
        assert contain_telegram.default is False

    def test_contain_sms_default_false(self, cart_item_instance):
        contain_sms = cart_item_instance._meta.get_field('contain_sms')
        assert contain_sms.default is False

    def test_contain_email_default_false(self, cart_item_instance):
        contain_email = cart_item_instance._meta.get_field('contain_email')
        assert contain_email.default is False

    def test_get_item_price_with_contain_telegram(self, cart_item_instance):
        cart_item_instance.contain_telegram = True
        assert cart_item_instance.get_item_price() == project_variables.TELEGRAM_PRICE

    def test_get_item_price_with_contain_sms(self, cart_item_instance):
        cart_item_instance.contain_sms = True
        assert cart_item_instance.get_item_price() == project_variables.SMS_PRICE

    def test_get_item_price_with_contain_email(self, cart_item_instance):
        cart_item_instance.contain_email = True
        assert cart_item_instance.get_item_price() == project_variables.EMAIL_PRICE

    def test_meta_unique_together(self):
        assert CartItem._meta.unique_together == (('cart', 'course'),)


class TestOrderModel:
    @pytest.fixture
    def order_instance(self, user_instance):
        return baker.make(Order, user=user_instance)

    def test_return_str(self, order_instance):
        assert str(order_instance) == str(order_instance.id) + ' : ' + str(order_instance.payment_status)

    def test_user_is_foreign_key(self, order_instance):
        user = order_instance._meta.get_field('user')
        assert isinstance(user, models.ForeignKey)

    def test_user_on_delete(self, order_instance):
        user = order_instance._meta.get_field('user')
        assert user.remote_field.on_delete == models.SET_NULL

    def test_user_related_name(self, order_instance):
        user = order_instance._meta.get_field('user')
        assert user.remote_field.related_name == 'orders'

    def test_user_null_true(self, order_instance):
        user = order_instance._meta.get_field('user')
        assert user.null is True

    def test_placed_at_auto_now_add(self, order_instance):
        assert order_instance._meta.get_field('placed_at').auto_now_add is True

    def test_payment_status_choices(self, order_instance):
        payment_status_choices = order_instance._meta.get_field('payment_status').choices
        assert payment_status_choices == [('P', 'در حال پردازش'),
                                          ('C', 'موفق'),
                                          ('F', 'ناموفق'), ]

    def test_payment_status_default(self, order_instance):
        payment_status = order_instance._meta.get_field('payment_status')
        assert payment_status.default == 'P'

    def test_payment_method_choices(self, order_instance):
        payment_method_choices = order_instance._meta.get_field('payment_method').choices
        assert payment_method_choices == (('O', 'پرداخت آنلاین'),
                                          ('W', 'پرداخت از طریق کیف پول'),)

    def test_payment_method_default(self, order_instance):
        payment_method = order_instance._meta.get_field('payment_method')
        assert payment_method.default == 'O'

    def test_ref_code_max_length(self, order_instance):
        max_length = order_instance._meta.get_field('ref_code').max_length
        assert max_length == 20

    def test_ref_code_unique(self, order_instance):
        with pytest.raises(IntegrityError):
            baker.make(Order, ref_code=order_instance.ref_code)

    def test_total_price(self, order_instance, courses):
        order_item_1 = baker.make(OrderItem, order=order_instance, contain_email=True, contain_sms=True,
                                  contain_telegram=True, course=courses[0])
        order_item_2 = baker.make(OrderItem, order=order_instance, contain_email=False, contain_sms=True,
                                  contain_telegram=True, course=courses[1])
        order_item_3 = baker.make(OrderItem, order=order_instance, contain_email=True, contain_sms=False,
                                  contain_telegram=True, course=courses[2])
        order_item_4 = baker.make(OrderItem, order=order_instance, contain_email=True, contain_sms=True,
                                  contain_telegram=False, course=courses[3])

        total = order_item_1.unit_price + order_item_2.unit_price + \
                order_item_3.unit_price + order_item_4.unit_price
        assert order_instance.total_price() == float(total) * project_variables.TAX + float(total)

    def test_jalali_placed_at(self, order_instance):
        assert order_instance.jalali_placed_at == get_persian_date(order_instance.placed_at)


class TestOrderItemModel:
    @pytest.fixture
    def order_instance(self, user_instance):
        return baker.make(Order, user=user_instance)

    @pytest.fixture
    def order_item_instance(self, order_instance, courses):
        return baker.make(OrderItem, order=order_instance, course=courses[0])

    def test_return_str(self, order_item_instance):
        assert str(order_item_instance) == str(order_item_instance.id) + ' : ' + str(
            order_item_instance.order.id) + ' : ' + str(order_item_instance.course_number) + '_' + str(
            order_item_instance.class_gp)

    def test_order_is_foreign_key(self, order_item_instance):
        order = order_item_instance._meta.get_field('order')
        assert isinstance(order, models.ForeignKey)

    def test_order_on_delete(self, order_item_instance):
        order = order_item_instance._meta.get_field('order')
        assert order.remote_field.on_delete == models.CASCADE

    def test_course_is_foreign_key(self, order_item_instance):
        course = order_item_instance._meta.get_field('course')
        assert isinstance(course, models.ForeignKey)

    def test_course_on_delete(self, order_item_instance):
        course = order_item_instance._meta.get_field('course')
        assert course.remote_field.on_delete == models.SET_NULL

    def test_order_related_name(self, order_item_instance):
        order = order_item_instance._meta.get_field('order')
        assert order.remote_field.related_name == 'items'

    def test_course_related_name(self, order_item_instance):
        course = order_item_instance._meta.get_field('course')
        assert course.remote_field.related_name == 'order_items'

    def test_contain_telegram_default_false(self, order_item_instance):
        contain_telegram = order_item_instance._meta.get_field('contain_telegram')
        assert contain_telegram.default is False

    def test_contain_sms_default_false(self, order_item_instance):
        contain_sms = order_item_instance._meta.get_field('contain_sms')
        assert contain_sms.default is False

    def test_contain_email_default_false(self, order_item_instance):
        contain_email = order_item_instance._meta.get_field('contain_email')
        assert contain_email.default is False

    def test_unit_price_max_digits(self, order_item_instance):
        max_digits = order_item_instance._meta.get_field('unit_price').max_digits
        assert max_digits == 10

    def test_unit_price_decimal_places(self, order_item_instance):
        decimal_places = order_item_instance._meta.get_field('unit_price').decimal_places
        assert decimal_places == 0

    def test_meta_index(self):
        assert len(OrderItem._meta.indexes) == 1
        for field in OrderItem._meta.indexes:
            assert field.fields == ['course_number', 'class_gp']
            break

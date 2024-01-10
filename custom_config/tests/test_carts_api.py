import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnList, ReturnDict

from custom_config.models import ModelTracker, FieldTracker, Cart, CartItem, OrderItem, Order

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestCartAPI:
    @pytest.fixture
    def get_carts_url(self, cart_instance):
        return reverse('custom_config:carts-list')

    @pytest.fixture
    def post_cart_url(self):
        return reverse('custom_config:carts-list')

    def test_get_carts_200_for_authenticated_user(self, api_client, user_instance, cart_instance, get_carts_url):
        api_client.force_authenticate(user_instance)
        response = api_client.get(get_carts_url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_carts_403_for_unauthenticated_user(self, api_client, get_carts_url):
        response = api_client.get(get_carts_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_post_cart_403_for_non_staff_users(self, api_client, user_instance, post_cart_url):
        api_client.force_authenticate(user_instance)
        response = api_client.post(post_cart_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_cart_403_for_non_staff_users(self, api_client, user_instance, cart_instance):
        api_client.force_authenticate(user_instance)
        response = api_client.put(reverse('custom_config:carts-detail', kwargs={'pk': cart_instance.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_cart_403_for_non_staff_users(self, api_client, user_instance, cart_instance):
        api_client.force_authenticate(user_instance)
        response = api_client.patch(reverse('custom_config:carts-detail', kwargs={'pk': cart_instance.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_cart_403_for_all_users(self, api_client, user_instance, cart_instance):
        api_client.force_authenticate(user_instance)
        response = api_client.delete(reverse('custom_config:carts-detail', kwargs={'pk': cart_instance.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_add_to_cart_201_for_authenticated_user(self, api_client, user_instance, cart_instance, course_instance):
        api_client.force_authenticate(user_instance)
        url = reverse('custom_config:carts-add-to-cart')
        data = {
            'complete_course_number': str(course_instance.base_course.course_number) + '_' + course_instance.class_gp,
            'contain_telegram': True, 'contain_sms': True, 'contain_email': True}
        response = api_client.post(url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert CartItem.objects.filter(cart=cart_instance, course=course_instance).exists()

    def test_update_cart(self, api_client, user_instance, cart_instance, course_instance):
        api_client.force_authenticate(user_instance)
        cart_item = CartItem.objects.create(cart=cart_instance, course=course_instance, contain_telegram=True,
                                            contain_sms=True, contain_email=True)
        url = reverse('custom_config:carts-update-cart', kwargs={'item_id': cart_item.id})
        data = {'contain_telegram': False, 'contain_sms': True, 'contain_email': False}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        cart_item = CartItem.objects.get(id=cart_item.id)
        assert not cart_item.contain_telegram
        assert cart_item.contain_sms
        assert not cart_item.contain_email

    def test_deleting_cart_with_update_cart(self, api_client, user_instance, cart_instance, course_instance):
        api_client.force_authenticate(user_instance)
        cart_item = CartItem.objects.create(cart=cart_instance, course=course_instance, contain_telegram=True,
                                            contain_sms=True, contain_email=True)
        url = reverse('custom_config:carts-update-cart', kwargs={'item_id': cart_item.id})
        data = {'contain_telegram': False, 'contain_sms': False, 'contain_email': False}
        response = api_client.patch(url, data)
        assert response.status_code == status.HTTP_200_OK
        assert not CartItem.objects.filter(cart=cart_instance, course=course_instance).exists()

    def test_remove_item_204_for_authenticated_user(self, api_client, user_instance, cart_instance, course_instance):
        api_client.force_authenticate(user_instance)
        cart_item = CartItem.objects.create(cart=cart_instance, course=course_instance)
        url = reverse('custom_config:carts-remove-item', kwargs={'item_id': cart_item.id})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_204_NO_CONTENT
        assert not CartItem.objects.filter(cart=cart_instance, course=course_instance).exists()

    def test_list_carts_200_for_authenticated_user(self, api_client, user_instance, cart_instance):
        api_client.force_authenticate(user_instance)
        url = reverse('custom_config:carts-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        # is dict
        assert type(response.data) == ReturnDict
        assert 'id' in response.data
        assert response.data['id'] == str(cart_instance.id)

    def test_list_carts_200_for_staff_user(self, api_client, admin_user_instance, cart_instance):
        api_client.force_authenticate(admin_user_instance)
        url = reverse('custom_config:carts-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK
        assert type(response.data) == ReturnList

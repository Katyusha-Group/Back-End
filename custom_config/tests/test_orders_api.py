import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.utils.serializer_helpers import ReturnList

from custom_config.models import Order, CartItem
from custom_config.serializers import CreateOrderSerializer, OrderSerializer

pytestmark = pytest.mark.django_db


@pytest.mark.django_db
class TestOrderAPI:
    @pytest.fixture
    def get_orders_url(self):
        return reverse('custom_config:orders-list')

    @pytest.fixture
    def post_order_url(self):
        return reverse('custom_config:orders-list')

    def test_get_orders_200_for_authenticated_user(self, api_client, user_instance, get_orders_url):
        api_client.force_authenticate(user_instance)
        response = api_client.get(get_orders_url)
        assert response.status_code == status.HTTP_200_OK

    def test_get_orders_403_for_unauthenticated_user(self, api_client, get_orders_url):
        response = api_client.get(get_orders_url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_retrieve_order_200_for_authenticated_user(self, api_client, user_instance, order_instance):
        api_client.force_authenticate(user_instance)
        url = reverse('custom_config:orders-detail', kwargs={'pk': order_instance.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_retrieve_order_403_for_unauthenticated_user(self, api_client, order_instance):
        url = reverse('custom_config:orders-detail', kwargs={'pk': order_instance.pk})
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_list_orders_200_for_authenticated_user(self, api_client, user_instance):
        api_client.force_authenticate(user_instance)
        url = reverse('custom_config:orders-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_200_OK

    def test_list_orders_403_for_unauthenticated_user(self, api_client):
        url = reverse('custom_config:orders-list')
        response = api_client.get(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_order_403_for_authenticated_user(self, api_client, user_instance, order_instance):
        api_client.force_authenticate(user_instance)
        url = reverse('custom_config:orders-detail', kwargs={'pk': order_instance.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_order_403_for_unauthenticated_user(self, api_client, order_instance):
        url = reverse('custom_config:orders-detail', kwargs={'pk': order_instance.pk})
        response = api_client.delete(url)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_post_order_400_for_authenticated_user_with_no_cart(self, api_client, user_instance, post_order_url):
        api_client.force_authenticate(user_instance)
        data = {'payment_method': Order.PAY_WALLET}
        response = api_client.post(post_order_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_order_400_for_authenticated_user_with_empty_cart(self, api_client, user_instance, post_order_url,
                                                                   cart_instance):
        api_client.force_authenticate(user_instance)
        data = {'payment_method': Order.PAY_WALLET}
        response = api_client.post(post_order_url, data)
        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_post_order_201_for_authenticated_user_with_cart(self, api_client, user_instance, post_order_url,
                                                             cart_instance, course_instance):
        api_client.force_authenticate(user_instance)
        cart_item = CartItem.objects.create(cart=cart_instance, course=course_instance, contain_telegram=True,
                                            contain_sms=True, contain_email=True)
        data = {'payment_method': Order.PAY_WALLET}
        response = api_client.post(post_order_url, data)
        assert response.status_code == status.HTTP_201_CREATED
        assert Order.objects.filter(user=user_instance, items__course=course_instance).exists()

    def test_post_order_403_for_unauthenticated_user(self, api_client, post_order_url):
        data = {'payment_method': Order.PAY_WALLET}
        response = api_client.post(post_order_url, data)
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_put_order_403_for_non_staff_users(self, api_client, user_instance, order_instance):
        api_client.force_authenticate(user_instance)
        response = api_client.put(reverse('custom_config:orders-detail', kwargs={'pk': order_instance.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_patch_order_403_for_non_staff_users(self, api_client, user_instance, order_instance):
        api_client.force_authenticate(user_instance)
        response = api_client.patch(reverse('custom_config:orders-detail', kwargs={'pk': order_instance.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_delete_order_403_for_all_users(self, api_client, user_instance, order_instance):
        api_client.force_authenticate(user_instance)
        response = api_client.delete(reverse('custom_config:orders-detail', kwargs={'pk': order_instance.pk}))
        assert response.status_code == status.HTTP_403_FORBIDDEN

from django.shortcuts import render, get_object_or_404
from django.utils.safestring import mark_safe
from django.contrib.auth.decorators import login_required
import json
from django.http import HttpRequest, HttpResponse
from rest_framework.decorators import permission_classes
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework import status
from .serializers import ChatSerializer
from .models import *
from social_media.models import *
from django.http import JsonResponse
from django.db.models import Q
from itertools import chain
from rest_framework import serializers
from django.db.models import Q

"""Get chat messages of a specific room between a specific customer and manager"""


def room(request, custId, mngId):
    custid = custId
    mngid = mngId
    room_name = f"{custid}_{mngid}"
    messages = Chat.objects.filter(room_name=room_name)
    serializer = ChatSerializer(messages, many=True)
    return HttpResponse(serializer.data, status=status.HTTP_200_OK)


"""Get the names of  contacts """


def get_names(request, *args, **kwargs):
    uid = kwargs["user_id"]  # get the user id which has send the request
    query_set = None
    names = {}
    name = ""
    query_set = Room.objects.filter(customer_id=uid).values_list("manager_id", flat=True)
    for query in query_set:
        name = Profile.objects.filter(id=query).first().username
        names[name] = query
    return HttpResponse(json.dumps(names))


def delete_all_chats(request):
    messages = Chat.objects.all()
    for ms in messages:
        Chat.objects.filter(id=ms.id).delete()
    return HttpResponse("done", status=status.HTTP_200_OK)

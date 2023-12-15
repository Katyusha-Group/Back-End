from django.http import HttpRequest, HttpResponse
from rest_framework import status
from .serializers import ChatSerializer, RoomSerializer
from .models import Chat, Room
from django.db.models import Q

"""Get chat messages of a specific room between a specific customer and manager"""


def room(request, room_name):
    messages = Chat.objects.filter(room_name=room_name)
    serializer = ChatSerializer(messages, many=True)
    return HttpResponse(serializer.data, status=status.HTTP_200_OK)


"""Get the names of  contacts """


def get_names(request, *args, **kwargs):
    username = kwargs['username']  # get the username which has send the request
    rooms = Room.objects.filter(Q(profile1__username=username) | Q(profile2__username=username))
    serializer = RoomSerializer(rooms, many=True, context={'username': username})
    return HttpResponse(serializer.data, status=status.HTTP_200_OK)


def delete_all_chats(request):
    messages = Chat.objects.all()
    for ms in messages:
        Chat.objects.filter(id=ms.id).delete()
    return HttpResponse("done", status=status.HTTP_200_OK)

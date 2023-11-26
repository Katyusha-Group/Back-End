from django.dispatch.dispatcher import Signal

send_notification = Signal()
# This signal provides following arguments:
# recipient: is the profile who will receive the notification
# actor: is the profile who triggered the notification
# notification_type: is the type of notification, it can be one of the following:
#       - TYPE_LIKE: when someone likes a post
#       - TYPE_REPLY: when someone replies to a post
#       - TYPE_FOLLOW: when someone follows a profile
#       - TYPE_MENTION: when someone mentions a profile in a post
#       - TYPE_NEW_POST: when someone creates a new post
# tweet: is the post which is related to the notification, it can be null if the notification is not related to a post

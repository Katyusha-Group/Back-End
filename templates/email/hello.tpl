{% extends "mail_templated/base.tpl" %}

{% block subject %}
Hello {{ user.name }}
{% endblock %}

{% block html %}
This is an <strong>html</strong> message.
<img src="https://www.google.com/url?sa=i&url=https%3A%2F%2Ffr.wikipedia.org%2Fwiki%2FImage&psig=AOvVaw1kGA0CPKWvjUQ8aCM0mDlG&ust=1679905019045000&source=images&cd=vfe&ved=0CA8QjRxqFwoTCOier5KU-f0CFQAAAAAdAAAAABAE">
{% endblock %}
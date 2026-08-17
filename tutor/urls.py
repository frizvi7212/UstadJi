# chat/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("", views.index, name="index"),
    path("<int:conversation_id>/", views.index, name="index_with_id"),
    path("new/", views.new_conversation, name="new_conversation"),
]
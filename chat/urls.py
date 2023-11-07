from django.urls import path
from . import views

# urls.py is the file that maps URLs to views.

urlpatterns = [
	path('', views.index_view, name='chat-index'),
	path('<str:room_name>/', views.room_view, name='chat-room'),
]
from django.urls import path

from assistant import views

app_name = "assistant"
urlpatterns = [
    path('threads/', views.threads, name='threads'),
    path('threads/<int:thread_id>/', views.view_thread, name='view_thread'),
    path('threads/<int:thread_id>/messages/', views.get_thread_messages, name='get_thread_messages'),
    path('threads/<int:thread_id>/messages/send/', views.send_message_to_thread, name='send_message_to_thread'),
    path('threads/create/', views.create_thread, name='create_thread'),
    path('threads/create/<str:app_label>/<str:model_name>/<int:object_id>/', views.create_thread, name='create_thread'),
]

from django.urls import path

from assistant import views

app_name = "assistant"
urlpatterns = [
    path('threads/', views.threads, name='threads'),
    path('threads/<int:thread_id>', views.view_thread, name='view_thread'),
    path('threads/create/', views.create_thread, name='create_thread'),
]

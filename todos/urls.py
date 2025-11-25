from django.urls import path
from . import views

app_name = 'todos'

urlpatterns = [
    path('', views.TodoListView.as_view(), name='todo_list'),
    path('todo/<int:pk>/', views.TodoDetailView.as_view(), name='todo_detail'),
    path('todo/new/', views.TodoCreateView.as_view(), name='todo_create'),
    path('todo/<int:pk>/edit/', views.TodoUpdateView.as_view(), name='todo_update'),
    path('todo/<int:pk>/delete/', views.TodoDeleteView.as_view(), name='todo_delete'),
    path('todo/<int:pk>/toggle-complete/', views.toggle_complete, name='todo_toggle_complete'),
]

# tests.py
from django.test import TestCase, Client
from django.urls import reverse
from django.utils import timezone
from .models import Todo
from django.contrib.messages import get_messages

class TodoModelTest(TestCase):
    def test_create_todo(self):
        todo = Todo.objects.create(
            title='Test Todo',
            description='Test Description',
            due_date=timezone.now()
        )
        self.assertEqual(str(todo), 'Test Todo')
        self.assertFalse(todo.completed)
        self.assertIsNotNone(todo.created_at)
        self.assertIsNotNone(todo.updated_at)

class TodoViewTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.todo = Todo.objects.create(
            title='Test Todo',
            description='Test Description',
            due_date=timezone.now()
        )

    def test_todo_list_view(self):
        response = self.client.get(reverse('todos:todo_list'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Todo')
        self.assertTemplateUsed(response, 'todos/todo_list.html')

    def test_todo_detail_view(self):
        response = self.client.get(reverse('todos:todo_detail', args=[self.todo.pk]))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'Test Todo')
        self.assertTemplateUsed(response, 'todos/todo_detail.html')

    def test_todo_create_view(self):
        response = self.client.post(reverse('todos:todo_create'), {
            'title': 'New Test Todo',
            'description': 'New Test Description',
            'due_date': '2023-12-31 23:59'
        })
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Todo.objects.count(), 2)
        self.assertTrue(Todo.objects.filter(title='New Test Todo').exists())

    def test_todo_update_view(self):
        response = self.client.post(reverse('todos:todo_update', args=[self.todo.pk]), {
            'title': 'Updated Test Todo',
            'description': 'Updated Description',
            'due_date': '2023-12-31 23:59',
            'completed': True
        })
        self.assertEqual(response.status_code, 302)
        self.todo.refresh_from_db()
        self.assertEqual(self.todo.title, 'Updated Test Todo')
        self.assertTrue(self.todo.completed)

    def test_todo_delete_view(self):
        todo_id = self.todo.pk
        response = self.client.post(reverse('todos:todo_delete', args=[todo_id]))
        self.assertEqual(response.status_code, 302)
        self.assertEqual(Todo.objects.count(), 0)
        # Check the redirect after deletion
        self.assertRedirects(response, reverse('todos:todo_list'))

    def test_toggle_complete_view(self):
        self.assertFalse(self.todo.completed)
        response = self.client.post(reverse('todos:todo_toggle_complete', args=[self.todo.pk]))
        self.todo.refresh_from_db()
        self.assertTrue(self.todo.completed)
        self.assertEqual(response.status_code, 302)
        messages = list(get_messages(response.wsgi_request))
        self.assertIn('marked as complete', str(messages[0]).lower())

    def test_sorting_functionality(self):
        now = timezone.now()
        Todo.objects.create(title='B Todo', due_date=now, completed=False)
        Todo.objects.create(title='A Todo', due_date=now + timezone.timedelta(days=1), completed=True)
        
        # Test title sort
        response = self.client.get(reverse('todos:todo_list') + '?sort=title')
        todos = response.context['todos']
        self.assertEqual(todos[0].title, 'A Todo')
        self.assertEqual(todos[1].title, 'B Todo')
        
        # Test due_date sort
        response = self.client.get(reverse('todos:todo_list') + '?sort=-due_date')
        todos = response.context['todos']
        self.assertTrue(todos[0].due_date > todos[1].due_date)

    def test_past_due_indicator(self):
        past_due = timezone.now() - timezone.timedelta(days=1)
        todo = Todo.objects.create(
            title='Past Due Todo',
            due_date=past_due,
            completed=False
        )
        response = self.client.get(reverse('todos:todo_list'))
        self.assertContains(response, 'Past Due')
        self.assertContains(response, 'table-danger')

    def test_pagination(self):
        # Create more than 10 todos to test pagination
        for i in range(15):
            Todo.objects.create(
                title=f'Test Todo {i}',
                due_date=timezone.now()
            )
        response = self.client.get(reverse('todos:todo_list'))
        self.assertEqual(len(response.context['todos']), 10)  # 10 items per page
        self.assertTrue('is_paginated' in response.context)
        self.assertTrue(response.context['is_paginated'])
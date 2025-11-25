from django.db import models
from django.utils import timezone
from django.urls import reverse

class Todo(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    due_date = models.DateTimeField('due date')
    completed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        return reverse('todo_detail', kwargs={'pk': self.pk})

    class Meta:
        ordering = ['-created_at']

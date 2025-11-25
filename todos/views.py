from django.views.generic import ListView, DetailView, CreateView, UpdateView, DeleteView
from django.urls import reverse_lazy
from django.utils import timezone
from django.shortcuts import get_object_or_404, redirect
from django.contrib import messages
from .models import Todo

class TodoListView(ListView):
    model = Todo
    template_name = 'todos/todo_list.html'
    context_object_name = 'todos'
    paginate_by = 10

    def get_queryset(self):
        queryset = Todo.objects.all()
        
        # Handle sorting
        sort_by = self.request.GET.get('sort', '')
        self.sort_order = ''
        
        if sort_by.startswith('-'):
            self.sort_order = '-'
            sort_by = sort_by[1:]
            
        if sort_by in ['title', 'due_date', 'created_at', 'completed']:
            if sort_by == 'completed':
                queryset = sorted(queryset, 
                               key=lambda x: (x.completed, x.due_date), 
                               reverse=(self.sort_order == '-'))
            else:
                queryset = queryset.order_by(f"{self.sort_order}{sort_by}")
        else:
            # Default sorting: incomplete first, then by due date
            queryset = queryset.order_by('completed', 'due_date')
            
        return queryset

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['now'] = timezone.now()
        sort_by = self.request.GET.get('sort', '')
        if sort_by.startswith('-'):
            context['sort_by'] = sort_by[1:]
            context['sort_order'] = '-'
        else:
            context['sort_by'] = sort_by
            context['sort_order'] = ''
        return context
       
        return Todo.objects.all().order_by('completed', 'due_date')

class TodoDetailView(DetailView):
    model = Todo
    template_name = 'todos/todo_detail.html'
    context_object_name = 'todo'

class TodoCreateView(CreateView):
    model = Todo
    template_name = 'todos/todo_form.html'
    fields = ['title', 'description', 'due_date']
    
    def get_success_url(self):
        messages.success(self.request, 'Todo created successfully!')
        return reverse_lazy('todos:todo_detail', kwargs={'pk': self.object.pk})
        
    def form_valid(self, form):
        # Set any additional fields here if needed
        return super().form_valid(form)

class TodoUpdateView(UpdateView):
    model = Todo
    template_name = 'todos/todo_form.html'
    fields = ['title', 'description', 'due_date', 'completed']
    context_object_name = 'todo'

    def get_success_url(self):
        messages.success(self.request, 'Todo updated successfully!')
        return reverse_lazy('todos:todo_detail', kwargs={'pk': self.object.pk})

def toggle_complete(request, pk):
    todo = get_object_or_404(Todo, pk=pk)
    todo.completed = not todo.completed
    todo.save()
    action = 'marked as complete' if todo.completed else 'marked as incomplete'
    messages.success(request, f'Todo "{todo.title}" {action}!')
    return redirect('todos:todo_list')

class TodoDeleteView(DeleteView):
    model = Todo
    template_name = 'todos/todo_confirm_delete.html'
    success_url = reverse_lazy('todos:todo_list')
    context_object_name = 'todo'

    def delete(self, request, *args, **kwargs):
        messages.success(request, 'Todo deleted successfully!')
        return super().delete(request, *args, **kwargs)

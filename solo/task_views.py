# solo/task_views.py
"""
Task/Goals API Views
Simple CRUD operations for tasks
"""
from django.shortcuts import get_object_or_404, render
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_POST, require_http_methods
from django.utils import timezone
import json

from tracker.models import Task


@login_required
def study_goals_page(request):
    """
    Study Goals management page
    """
    goals = Task.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'tracker/study_goals.html', {'goals': goals})


@login_required
@require_POST
def create_task(request):
    """
    Create a new task/goal
    """
    try:
        data = json.loads(request.body)
        title = data.get('title', '').strip()
        
        if not title:
            return JsonResponse({'success': False, 'error': 'Title is required'}, status=400)
        
        # Create task
        task = Task.objects.create(
            user=request.user,
            title=title,
            notes=data.get('notes', ''),
            priority=data.get('priority', 'medium'),
            due_date=data.get('due_date', None)
        )
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'notes': task.notes,
                'priority': task.priority,
                'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                'completed': task.completed
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def update_task(request, task_id):
    """
    Update an existing task
    """
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        data = json.loads(request.body)
        
        # Update fields if provided
        if 'title' in data:
            task.title = data['title']
        if 'notes' in data:
            task.notes = data['notes']
        if 'priority' in data:
            task.priority = data['priority']
        if 'due_date' in data:
            task.due_date = data['due_date']
        
        task.save()
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'notes': task.notes,
                'priority': task.priority,
                'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                'completed': task.completed
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def toggle_task(request, task_id):
    """
    Mark task as complete or incomplete (toggle)
    """
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        if task.completed:
            # Mark as incomplete
            task.completed = False
            task.completed_at = None
        else:
            # Mark as complete
            task.mark_complete()
        
        task.save()
        
        return JsonResponse({
            'success': True,
            'completed': task.completed
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
@require_POST
def delete_task(request, task_id):
    """
    Delete a task
    """
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        task.delete()
        
        return JsonResponse({'success': True})
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def get_tasks(request):
    """
    Get all user's tasks (both active and completed)
    """
    try:
        # Get completed parameter (show completed tasks or not)
        show_completed = request.GET.get('completed', 'false').lower() == 'true'
        
        if show_completed:
            tasks = Task.objects.filter(user=request.user)
        else:
            tasks = Task.objects.filter(user=request.user, completed=False)
        
        tasks_data = [{
            'id': task.id,
            'title': task.title,
            'notes': task.notes,
            'priority': task.priority,
            'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
            'completed': task.completed,
            'created_at': task.created_at.strftime('%Y-%m-%d %H:%M')
        } for task in tasks]
        
        return JsonResponse({
            'success': True,
            'tasks': tasks_data
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)


@login_required
def get_task(request, task_id):
    """
    Get a single task by ID
    """
    try:
        task = get_object_or_404(Task, id=task_id, user=request.user)
        
        return JsonResponse({
            'success': True,
            'task': {
                'id': task.id,
                'title': task.title,
                'notes': task.notes,
                'priority': task.priority,
                'due_date': task.due_date.strftime('%Y-%m-%d') if task.due_date else None,
                'completed': task.completed,
            }
        })
    
    except Exception as e:
        return JsonResponse({'success': False, 'error': str(e)}, status=400)

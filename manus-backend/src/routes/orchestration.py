from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import json
import asyncio
from typing import Dict, Any

from ..services.orchestration_service import orchestrator, TaskPriority, TaskStatus

orchestration_bp = Blueprint('orchestration', __name__)

def run_async(coro):
    """Helper function to run async functions in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@orchestration_bp.route('/tasks/templates', methods=['GET'])
@jwt_required()
def get_task_templates():
    """Get available task templates"""
    try:
        templates = orchestrator.get_task_templates()
        
        return jsonify({
            'success': True,
            'templates': templates
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting task templates: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get task templates'}), 500

@orchestration_bp.route('/tasks/create-from-template', methods=['POST'])
@jwt_required()
def create_task_from_template():
    """Create a task from a template"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        template_name = data.get('template_name')
        parameters = data.get('parameters', {})
        
        if not template_name:
            return jsonify({'success': False, 'error': 'template_name is required'}), 400
        
        # Create task from template
        task_id = run_async(orchestrator.create_task_from_template(
            user_id, template_name, parameters
        ))
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Task created successfully'
        })
        
    except ValueError as e:
        return jsonify({'success': False, 'error': str(e)}), 400
    except Exception as e:
        current_app.logger.error(f"Error creating task from template: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create task'}), 500

@orchestration_bp.route('/tasks/create-custom', methods=['POST'])
@jwt_required()
def create_custom_task():
    """Create a custom task"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        title = data.get('title')
        description = data.get('description')
        task_type = data.get('task_type', 'custom')
        steps = data.get('steps', [])
        priority_str = data.get('priority', 'normal')
        
        if not title or not description or not steps:
            return jsonify({
                'success': False, 
                'error': 'title, description, and steps are required'
            }), 400
        
        # Convert priority string to enum
        priority_map = {
            'low': TaskPriority.LOW,
            'normal': TaskPriority.NORMAL,
            'high': TaskPriority.HIGH,
            'urgent': TaskPriority.URGENT
        }
        priority = priority_map.get(priority_str.lower(), TaskPriority.NORMAL)
        
        # Create custom task
        task_id = run_async(orchestrator.create_custom_task(
            user_id, title, description, task_type, steps, priority
        ))
        
        return jsonify({
            'success': True,
            'task_id': task_id,
            'message': 'Custom task created successfully'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error creating custom task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create custom task'}), 500

@orchestration_bp.route('/tasks/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    try:
        user_id = get_jwt_identity()
        task = orchestrator.get_task(task_id)
        
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task.user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Convert task to dict
        task_data = {
            'id': task.id,
            'user_id': task.user_id,
            'title': task.title,
            'description': task.description,
            'task_type': task.task_type,
            'priority': task.priority.value,
            'status': task.status.value,
            'progress': task.progress,
            'result': task.result,
            'error': task.error,
            'created_at': task.created_at.isoformat() if task.created_at else None,
            'started_at': task.started_at.isoformat() if task.started_at else None,
            'completed_at': task.completed_at.isoformat() if task.completed_at else None,
            'estimated_duration': task.estimated_duration,
            'actual_duration': task.actual_duration,
            'metadata': task.metadata,
            'steps': []
        }
        
        # Add steps
        for step in task.steps:
            step_data = {
                'id': step.id,
                'name': step.name,
                'agent_id': step.agent_id,
                'action': step.action,
                'parameters': step.parameters,
                'dependencies': step.dependencies,
                'status': step.status.value,
                'result': step.result,
                'error': step.error,
                'started_at': step.started_at.isoformat() if step.started_at else None,
                'completed_at': step.completed_at.isoformat() if step.completed_at else None,
                'progress': step.progress
            }
            task_data['steps'].append(step_data)
        
        return jsonify({
            'success': True,
            'task': task_data
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get task'}), 500

@orchestration_bp.route('/tasks', methods=['GET'])
@jwt_required()
def get_user_tasks():
    """Get all tasks for the current user"""
    try:
        user_id = get_jwt_identity()
        tasks = orchestrator.get_user_tasks(user_id)
        
        # Convert tasks to list of dicts
        tasks_data = []
        for task in tasks:
            task_data = {
                'id': task.id,
                'title': task.title,
                'description': task.description,
                'task_type': task.task_type,
                'priority': task.priority.value,
                'status': task.status.value,
                'progress': task.progress,
                'created_at': task.created_at.isoformat() if task.created_at else None,
                'started_at': task.started_at.isoformat() if task.started_at else None,
                'completed_at': task.completed_at.isoformat() if task.completed_at else None,
                'estimated_duration': task.estimated_duration,
                'actual_duration': task.actual_duration,
                'steps_count': len(task.steps),
                'completed_steps': len([s for s in task.steps if s.status == TaskStatus.COMPLETED])
            }
            tasks_data.append(task_data)
        
        # Sort by created_at descending
        tasks_data.sort(key=lambda x: x['created_at'] or '', reverse=True)
        
        return jsonify({
            'success': True,
            'tasks': tasks_data,
            'total': len(tasks_data)
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting user tasks: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get tasks'}), 500

@orchestration_bp.route('/tasks/<task_id>/status', methods=['GET'])
@jwt_required()
def get_task_status(task_id):
    """Get the current status of a task"""
    try:
        user_id = get_jwt_identity()
        task = orchestrator.get_task(task_id)
        
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task.user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        status = orchestrator.get_task_status(task_id)
        
        return jsonify({
            'success': True,
            'status': status
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting task status: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get task status'}), 500

@orchestration_bp.route('/tasks/<task_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_task(task_id):
    """Cancel a task"""
    try:
        user_id = get_jwt_identity()
        task = orchestrator.get_task(task_id)
        
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task.user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        success = run_async(orchestrator.cancel_task(task_id))
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Task cancelled successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Task cannot be cancelled'
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error cancelling task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to cancel task'}), 500

@orchestration_bp.route('/tasks/<task_id>/pause', methods=['POST'])
@jwt_required()
def pause_task(task_id):
    """Pause a task"""
    try:
        user_id = get_jwt_identity()
        task = orchestrator.get_task(task_id)
        
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task.user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        success = run_async(orchestrator.pause_task(task_id))
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Task paused successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Task cannot be paused'
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error pausing task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to pause task'}), 500

@orchestration_bp.route('/tasks/<task_id>/resume', methods=['POST'])
@jwt_required()
def resume_task(task_id):
    """Resume a task"""
    try:
        user_id = get_jwt_identity()
        task = orchestrator.get_task(task_id)
        
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task.user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        success = run_async(orchestrator.resume_task(task_id))
        
        if success:
            return jsonify({
                'success': True,
                'message': 'Task resumed successfully'
            })
        else:
            return jsonify({
                'success': False,
                'error': 'Task cannot be resumed'
            }), 400
        
    except Exception as e:
        current_app.logger.error(f"Error resuming task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to resume task'}), 500

@orchestration_bp.route('/queue/status', methods=['GET'])
@jwt_required()
def get_queue_status():
    """Get the current status of the task queue"""
    try:
        status = orchestrator.get_queue_status()
        
        return jsonify({
            'success': True,
            'queue_status': status
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting queue status: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get queue status'}), 500

@orchestration_bp.route('/start', methods=['POST'])
@jwt_required()
def start_orchestrator():
    """Start the task orchestrator"""
    try:
        orchestrator.start()
        
        return jsonify({
            'success': True,
            'message': 'Task orchestrator started'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error starting orchestrator: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to start orchestrator'}), 500

@orchestration_bp.route('/stop', methods=['POST'])
@jwt_required()
def stop_orchestrator():
    """Stop the task orchestrator"""
    try:
        orchestrator.stop()
        
        return jsonify({
            'success': True,
            'message': 'Task orchestrator stopped'
        })
        
    except Exception as e:
        current_app.logger.error(f"Error stopping orchestrator: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to stop orchestrator'}), 500

# WebSocket support would be added here with Flask-SocketIO
# For now, we'll use polling for real-time updates

@orchestration_bp.route('/tasks/<task_id>/subscribe', methods=['POST'])
@jwt_required()
def subscribe_to_task_updates(task_id):
    """Subscribe to task updates (polling endpoint)"""
    try:
        user_id = get_jwt_identity()
        task = orchestrator.get_task(task_id)
        
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task.user_id != user_id:
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # For now, just return the current task status
        # In a real implementation, this would set up WebSocket subscription
        status = orchestrator.get_task_status(task_id)
        
        return jsonify({
            'success': True,
            'message': 'Subscribed to task updates',
            'current_status': status
        })
        
    except Exception as e:
        current_app.logger.error(f"Error subscribing to task updates: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to subscribe to updates'}), 500


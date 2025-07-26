from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime, timedelta
import asyncio
import uuid
import json

from ..models.user import User, Task, db
from ..services.agent_service import agent_service

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get user's tasks with optional filtering"""
    try:
        user_id = get_jwt_identity()
        
        # Get query parameters
        status = request.args.get('status')
        task_type = request.args.get('task_type')
        page = int(request.args.get('page', 1))
        per_page = int(request.args.get('per_page', 20))
        
        # Build query
        query = Task.query.filter_by(user_id=user_id)
        
        if status:
            query = query.filter_by(status=status)
        if task_type:
            query = query.filter_by(task_type=task_type)
        
        # Order by creation date (newest first)
        query = query.order_by(Task.created_at.desc())
        
        # Paginate
        tasks = query.paginate(
            page=page, 
            per_page=per_page, 
            error_out=False
        )
        
        return jsonify({
            'success': True,
            'tasks': [task.to_dict() for task in tasks.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': tasks.total,
                'pages': tasks.pages
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting tasks: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get tasks'}), 500

@tasks_bp.route('', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        # Validate required fields
        if not data.get('title') or not data.get('task_type'):
            return jsonify({'success': False, 'error': 'Title and task_type are required'}), 400
        
        # Get user to check credits
        user = User.query.get(user_id)
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        # Estimate credits needed
        estimated_credits = estimate_task_credits(data.get('task_type'), data.get('description', ''))
        
        # Check if user has enough credits
        if user.credits_balance < estimated_credits:
            return jsonify({
                'success': False, 
                'error': 'Insufficient credits',
                'required': estimated_credits,
                'available': user.credits_balance
            }), 400
        
        # Create task
        task = Task(
            id=str(uuid.uuid4()),
            user_id=user_id,
            title=data.get('title'),
            description=data.get('description', ''),
            task_type=data.get('task_type'),
            priority=data.get('priority', 'medium'),
            estimated_credits=estimated_credits,
            parameters=json.dumps(data.get('parameters', {})),
            status='pending'
        )
        
        db.session.add(task)
        db.session.commit()
        
        # Start task execution asynchronously
        asyncio.create_task(execute_task_async(task.id, task.to_dict()))
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        }), 201
        
    except Exception as e:
        current_app.logger.error(f"Error creating task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create task'}), 500

@tasks_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    try:
        user_id = get_jwt_identity()
        
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get task'}), 500

@tasks_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # Update allowed fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        if 'priority' in data:
            task.priority = data['priority']
        if 'parameters' in data:
            task.parameters = json.dumps(data['parameters'])
        
        task.updated_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'success': True,
            'task': task.to_dict()
        })
        
    except Exception as e:
        current_app.logger.error(f"Error updating task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to update task'}), 500

@tasks_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    try:
        user_id = get_jwt_identity()
        
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        # Cancel if running
        if task.status == 'running':
            agent_service.cancel_task(task_id)
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'success': True})
        
    except Exception as e:
        current_app.logger.error(f"Error deleting task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to delete task'}), 500

@tasks_bp.route('/<task_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_task(task_id):
    """Cancel a running task"""
    try:
        user_id = get_jwt_identity()
        
        task = Task.query.filter_by(id=task_id, user_id=user_id).first()
        if not task:
            return jsonify({'success': False, 'error': 'Task not found'}), 404
        
        if task.status != 'running':
            return jsonify({'success': False, 'error': 'Task is not running'}), 400
        
        # Cancel the task
        success = agent_service.cancel_task(task_id)
        
        if success:
            task.status = 'cancelled'
            task.updated_at = datetime.utcnow()
            db.session.commit()
            
            return jsonify({
                'success': True,
                'task': task.to_dict()
            })
        else:
            return jsonify({'success': False, 'error': 'Failed to cancel task'}), 500
        
    except Exception as e:
        current_app.logger.error(f"Error cancelling task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to cancel task'}), 500

@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """Get user's task statistics"""
    try:
        user_id = get_jwt_identity()
        
        # Get basic counts
        total_tasks = Task.query.filter_by(user_id=user_id).count()
        completed_tasks = Task.query.filter_by(user_id=user_id, status='completed').count()
        running_tasks = Task.query.filter_by(user_id=user_id, status='running').count()
        failed_tasks = Task.query.filter_by(user_id=user_id, status='failed').count()
        
        # Get tasks by type
        task_types = db.session.query(
            Task.task_type, 
            db.func.count(Task.id)
        ).filter_by(user_id=user_id).group_by(Task.task_type).all()
        
        by_type = {task_type: count for task_type, count in task_types}
        
        # Get credits used
        credits_used = db.session.query(
            db.func.sum(Task.estimated_credits)
        ).filter_by(user_id=user_id, status='completed').scalar() or 0
        
        return jsonify({
            'success': True,
            'stats': {
                'total': total_tasks,
                'completed': completed_tasks,
                'running': running_tasks,
                'failed': failed_tasks,
                'by_type': by_type,
                'credits_used': credits_used
            }
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting task stats: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get task stats'}), 500

def estimate_task_credits(task_type: str, description: str) -> int:
    """Estimate credits needed for a task"""
    base_credits = {
        'image': 10,
        'video': 50,
        'slides': 15,
        'webpage': 25,
        'analysis': 20,
        'research': 30,
        'code': 20,
        'audio': 15,
        'document': 10
    }
    
    credits = base_credits.get(task_type, 10)
    
    # Adjust based on description length (complexity)
    if len(description) > 500:
        credits = int(credits * 1.5)
    elif len(description) > 200:
        credits = int(credits * 1.2)
    
    return credits

async def execute_task_async(task_id: str, task_data: dict):
    """Execute task asynchronously"""
    try:
        # Update task status to running
        task = Task.query.get(task_id)
        if task:
            task.status = 'running'
            task.started_at = datetime.utcnow()
            db.session.commit()
        
        # Execute the task using agent service
        result = await agent_service.execute_task(task_id, task_data)
        
        # Update task with results
        if task:
            if result['success']:
                task.status = 'completed'
                task.result = json.dumps(result)
                task.completed_at = datetime.utcnow()
                
                # Deduct credits from user
                user = User.query.get(task.user_id)
                if user:
                    user.credits_balance -= task.estimated_credits
                    user.credits_used += task.estimated_credits
            else:
                task.status = 'failed'
                task.error_message = result.get('error', 'Unknown error')
            
            task.updated_at = datetime.utcnow()
            db.session.commit()
            
    except Exception as e:
        current_app.logger.error(f"Error executing task {task_id}: {str(e)}")
        
        # Mark task as failed
        task = Task.query.get(task_id)
        if task:
            task.status = 'failed'
            task.error_message = str(e)
            task.updated_at = datetime.utcnow()
            db.session.commit()


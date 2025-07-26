from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
from src.models.user import User, Task, db

tasks_bp = Blueprint('tasks', __name__)

@tasks_bp.route('/', methods=['GET'])
@jwt_required()
def get_tasks():
    """Get all tasks for the current user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get query parameters
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        status = request.args.get('status')
        task_type = request.args.get('task_type')
        
        # Build query
        query = Task.query.filter_by(user_id=current_user_id)
        
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
            'tasks': [task.to_dict() for task in tasks.items],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': tasks.total,
                'pages': tasks.pages,
                'has_next': tasks.has_next,
                'has_prev': tasks.has_prev
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/', methods=['POST'])
@jwt_required()
def create_task():
    """Create a new task"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('title') or not data.get('task_type'):
            return jsonify({'error': 'Title and task_type are required'}), 400
        
        # Validate task type
        valid_task_types = ['image', 'slides', 'webpage', 'visualization', 'document', 'video', 'audio', 'research', 'code']
        if data['task_type'] not in valid_task_types:
            return jsonify({'error': f'Invalid task_type. Must be one of: {", ".join(valid_task_types)}'}), 400
        
        # Estimate credits needed (basic estimation)
        credits_needed = estimate_credits(data['task_type'], data.get('input_data', {}))
        
        # Check if user has enough credits
        user.reset_daily_credits()  # Reset daily credits if needed
        if not user.use_credits(credits_needed):
            return jsonify({
                'error': 'Insufficient credits',
                'credits_needed': credits_needed,
                'credits_available': user.credits_balance
            }), 402
        
        # Create task
        task = Task(
            user_id=current_user_id,
            title=data['title'],
            description=data.get('description'),
            task_type=data['task_type'],
            input_data=data.get('input_data', {}),
            credits_used=credits_needed
        )
        
        db.session.add(task)
        db.session.commit()
        
        # TODO: Queue task for processing by agents
        # This would typically involve sending the task to a message queue
        # For now, we'll just mark it as pending
        
        return jsonify({
            'message': 'Task created successfully',
            'task': task.to_dict(),
            'credits_remaining': user.credits_balance
        }), 201
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<task_id>', methods=['GET'])
@jwt_required()
def get_task(task_id):
    """Get a specific task"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        return jsonify({'task': task.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<task_id>', methods=['PUT'])
@jwt_required()
def update_task(task_id):
    """Update a task (limited fields)"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        data = request.get_json()
        
        # Only allow updating certain fields
        if 'title' in data:
            task.title = data['title']
        if 'description' in data:
            task.description = data['description']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Task updated successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<task_id>', methods=['DELETE'])
@jwt_required()
def delete_task(task_id):
    """Delete a task"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        # Only allow deletion of pending or failed tasks
        if task.status in ['running', 'completed']:
            return jsonify({'error': 'Cannot delete running or completed tasks'}), 400
        
        db.session.delete(task)
        db.session.commit()
        
        return jsonify({'message': 'Task deleted successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/<task_id>/cancel', methods=['POST'])
@jwt_required()
def cancel_task(task_id):
    """Cancel a running task"""
    try:
        current_user_id = get_jwt_identity()
        
        task = Task.query.filter_by(id=task_id, user_id=current_user_id).first()
        
        if not task:
            return jsonify({'error': 'Task not found'}), 404
        
        if task.status != 'running':
            return jsonify({'error': 'Task is not running'}), 400
        
        # TODO: Implement actual task cancellation logic
        # This would involve stopping the agents and cleaning up resources
        
        task.status = 'cancelled'
        task.completed_at = datetime.utcnow()
        db.session.commit()
        
        return jsonify({
            'message': 'Task cancelled successfully',
            'task': task.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@tasks_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_task_stats():
    """Get task statistics for the current user"""
    try:
        current_user_id = get_jwt_identity()
        
        # Get task counts by status
        stats = {
            'total': Task.query.filter_by(user_id=current_user_id).count(),
            'pending': Task.query.filter_by(user_id=current_user_id, status='pending').count(),
            'running': Task.query.filter_by(user_id=current_user_id, status='running').count(),
            'completed': Task.query.filter_by(user_id=current_user_id, status='completed').count(),
            'failed': Task.query.filter_by(user_id=current_user_id, status='failed').count(),
            'cancelled': Task.query.filter_by(user_id=current_user_id, status='cancelled').count()
        }
        
        # Get task counts by type
        task_types = db.session.query(Task.task_type, db.func.count(Task.id)).filter_by(
            user_id=current_user_id
        ).group_by(Task.task_type).all()
        
        stats['by_type'] = {task_type: count for task_type, count in task_types}
        
        # Get recent activity (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        recent_tasks = Task.query.filter(
            Task.user_id == current_user_id,
            Task.created_at >= week_ago
        ).count()
        
        stats['recent_activity'] = recent_tasks
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

def estimate_credits(task_type, input_data):
    """Estimate credits needed for a task"""
    # Basic credit estimation based on task type
    base_credits = {
        'image': 10,
        'slides': 20,
        'webpage': 15,
        'visualization': 12,
        'document': 8,
        'video': 50,
        'audio': 15,
        'research': 25,
        'code': 30
    }
    
    credits = base_credits.get(task_type, 10)
    
    # Adjust based on complexity indicators in input_data
    if input_data.get('complexity') == 'high':
        credits *= 2
    elif input_data.get('complexity') == 'medium':
        credits *= 1.5
    
    # Adjust based on output requirements
    if input_data.get('high_quality', False):
        credits *= 1.3
    
    return int(credits)


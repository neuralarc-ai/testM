from flask import Blueprint, jsonify, request
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User, db

user_bp = Blueprint('user', __name__)

@user_bp.route('/', methods=['GET'])
@jwt_required()
def get_current_user():
    """Get current user information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Reset daily credits if needed
        user.reset_daily_credits()
        
        return jsonify({'user': user.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/profile', methods=['PUT'])
@jwt_required()
def update_profile():
    """Update user profile"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        # Update allowed fields
        if 'first_name' in data:
            user.first_name = data['first_name']
        if 'last_name' in data:
            user.last_name = data['last_name']
        if 'username' in data:
            # Check if username is available
            existing_user = User.query.filter_by(username=data['username']).first()
            if existing_user and existing_user.id != user.id:
                return jsonify({'error': 'Username already taken'}), 409
            user.username = data['username']
        if 'avatar_url' in data:
            user.avatar_url = data['avatar_url']
        
        db.session.commit()
        
        return jsonify({
            'message': 'Profile updated successfully',
            'user': user.to_dict()
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/credits', methods=['GET'])
@jwt_required()
def get_credits():
    """Get user credit information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Reset daily credits if needed
        user.reset_daily_credits()
        
        return jsonify({
            'credits_balance': user.credits_balance,
            'daily_credits': user.daily_credits,
            'subscription_type': user.subscription_type,
            'last_credit_reset': user.last_credit_reset.isoformat() if user.last_credit_reset else None
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/subscription', methods=['GET'])
@jwt_required()
def get_subscription():
    """Get user subscription information"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        subscription_info = {
            'type': user.subscription_type,
            'credits_balance': user.credits_balance,
            'daily_credits': user.daily_credits,
            'features': get_subscription_features(user.subscription_type)
        }
        
        return jsonify({'subscription': subscription_info}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/subscription', methods=['PUT'])
@jwt_required()
def update_subscription():
    """Update user subscription (placeholder for payment integration)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('subscription_type'):
            return jsonify({'error': 'Subscription type is required'}), 400
        
        new_subscription = data['subscription_type']
        
        if new_subscription not in ['free', 'premium', 'enterprise']:
            return jsonify({'error': 'Invalid subscription type'}), 400
        
        # TODO: Implement actual payment processing
        # This is a placeholder for Stripe/PayPal integration
        
        user.subscription_type = new_subscription
        
        # Update credits based on subscription
        if new_subscription == 'premium':
            user.daily_credits = 1000
        elif new_subscription == 'enterprise':
            user.daily_credits = 5000
        else:
            user.daily_credits = 300
        
        db.session.commit()
        
        return jsonify({
            'message': 'Subscription updated successfully',
            'subscription': {
                'type': user.subscription_type,
                'daily_credits': user.daily_credits,
                'features': get_subscription_features(user.subscription_type)
            }
        }), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

@user_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_user_stats():
    """Get user statistics"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get task statistics
        from src.models.user import Task
        
        total_tasks = Task.query.filter_by(user_id=current_user_id).count()
        completed_tasks = Task.query.filter_by(user_id=current_user_id, status='completed').count()
        
        # Calculate total credits used
        total_credits_used = db.session.query(db.func.sum(Task.credits_used)).filter_by(
            user_id=current_user_id
        ).scalar() or 0
        
        stats = {
            'account_created': user.created_at.isoformat() if user.created_at else None,
            'last_login': user.last_login.isoformat() if user.last_login else None,
            'total_tasks': total_tasks,
            'completed_tasks': completed_tasks,
            'success_rate': (completed_tasks / total_tasks * 100) if total_tasks > 0 else 0,
            'total_credits_used': total_credits_used,
            'current_credits': user.credits_balance,
            'subscription_type': user.subscription_type
        }
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@user_bp.route('/deactivate', methods=['POST'])
@jwt_required()
def deactivate_account():
    """Deactivate user account"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        user.is_active = False
        db.session.commit()
        
        return jsonify({'message': 'Account deactivated successfully'}), 200
        
    except Exception as e:
        db.session.rollback()
        return jsonify({'error': str(e)}), 500

def get_subscription_features(subscription_type):
    """Get features available for a subscription type"""
    features = {
        'free': {
            'daily_credits': 300,
            'max_concurrent_tasks': 1,
            'advanced_agents': False,
            'priority_support': False,
            'api_access': False
        },
        'premium': {
            'daily_credits': 1000,
            'max_concurrent_tasks': 5,
            'advanced_agents': True,
            'priority_support': True,
            'api_access': True
        },
        'enterprise': {
            'daily_credits': 5000,
            'max_concurrent_tasks': 20,
            'advanced_agents': True,
            'priority_support': True,
            'api_access': True,
            'custom_agents': True,
            'dedicated_support': True
        }
    }
    
    return features.get(subscription_type, features['free'])

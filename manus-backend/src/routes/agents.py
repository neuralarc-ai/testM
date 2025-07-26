from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity

from ..services.agent_service import agent_service

agents_bp = Blueprint('agents', __name__)

@agents_bp.route('', methods=['GET'])
@jwt_required()
def get_agents():
    """Get all available agents"""
    try:
        agents = agent_service.get_agents()
        
        return jsonify({
            'success': True,
            'agents': agents
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting agents: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get agents'}), 500

@agents_bp.route('/<agent_id>', methods=['GET'])
@jwt_required()
def get_agent(agent_id):
    """Get details of a specific agent"""
    try:
        agents = agent_service.get_agents()
        agent = next((a for a in agents if a['id'] == agent_id), None)
        
        if not agent:
            return jsonify({'success': False, 'error': 'Agent not found'}), 404
        
        return jsonify({
            'success': True,
            'agent': agent
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting agent: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get agent'}), 500

@agents_bp.route('/recommendations', methods=['GET'])
@jwt_required()
def get_agent_recommendations():
    """Get agent recommendations for a task type"""
    try:
        task_type = request.args.get('task_type')
        
        if not task_type:
            return jsonify({'success': False, 'error': 'task_type parameter is required'}), 400
        
        recommendations = agent_service.get_agent_recommendations(task_type)
        
        return jsonify({
            'success': True,
            'recommendations': recommendations,
            'task_type': task_type
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting agent recommendations: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get recommendations'}), 500

@agents_bp.route('/capabilities', methods=['GET'])
@jwt_required()
def get_agent_capabilities():
    """Get all agent capabilities"""
    try:
        agents = agent_service.get_agents()
        
        # Extract all unique capabilities
        all_capabilities = set()
        for agent in agents:
            all_capabilities.update(agent['capabilities'])
        
        # Group agents by capability
        capabilities_map = {}
        for capability in all_capabilities:
            capabilities_map[capability] = [
                {
                    'id': agent['id'],
                    'name': agent['name'],
                    'success_rate': agent['success_rate']
                }
                for agent in agents
                if capability in agent['capabilities']
            ]
        
        return jsonify({
            'success': True,
            'capabilities': list(all_capabilities),
            'capabilities_map': capabilities_map
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting agent capabilities: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get capabilities'}), 500

@agents_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_agent_stats():
    """Get agent usage statistics"""
    try:
        user_id = get_jwt_identity()
        
        # For now, return mock stats
        # In a real implementation, you'd query the database for actual usage
        stats = {
            'total_agents': len(agent_service.get_agents()),
            'most_used': [
                {'agent_id': 'content', 'name': 'Content Creator', 'usage_count': 45},
                {'agent_id': 'image', 'name': 'Visual Designer', 'usage_count': 32},
                {'agent_id': 'code', 'name': 'Code Developer', 'usage_count': 28}
            ],
            'success_rates': {
                'content': 0.95,
                'image': 0.92,
                'code': 0.88,
                'research': 0.94,
                'data': 0.91
            },
            'avg_completion_time': {
                'content': 45,  # seconds
                'image': 30,
                'code': 120,
                'research': 180,
                'data': 90
            }
        }
        
        return jsonify({
            'success': True,
            'stats': stats
        })
        
    except Exception as e:
        current_app.logger.error(f"Error getting agent stats: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get agent stats'}), 500


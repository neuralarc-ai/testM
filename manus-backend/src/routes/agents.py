from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from src.models.user import User

agents_bp = Blueprint('agents', __name__)

# Agent definitions based on Manus AI architecture
AVAILABLE_AGENTS = {
    'executor': {
        'id': 'executor',
        'name': 'Central Executor Agent',
        'description': 'Orchestrates and coordinates all other agents to complete complex tasks',
        'capabilities': ['task_planning', 'agent_coordination', 'workflow_management'],
        'status': 'active',
        'model': 'gpt-4'
    },
    'planning': {
        'id': 'planning',
        'name': 'Planning Agent',
        'description': 'Specializes in strategic planning, goal decomposition, and workflow optimization',
        'capabilities': ['strategic_planning', 'goal_decomposition', 'workflow_optimization'],
        'status': 'active',
        'model': 'claude-3.5-sonnet'
    },
    'knowledge': {
        'id': 'knowledge',
        'name': 'Knowledge Agent',
        'description': 'Handles information retrieval, research tasks, and knowledge synthesis',
        'capabilities': ['web_search', 'research', 'information_synthesis', 'fact_checking'],
        'status': 'active',
        'model': 'gpt-4'
    },
    'content_generation': {
        'id': 'content_generation',
        'name': 'Content Generation Agent',
        'description': 'Creates various types of content including text, images, videos, and presentations',
        'capabilities': ['text_generation', 'image_generation', 'video_generation', 'presentation_creation'],
        'status': 'active',
        'model': 'gpt-4'
    },
    'data_analysis': {
        'id': 'data_analysis',
        'name': 'Data Analysis Agent',
        'description': 'Focuses on data processing, statistical analysis, and visualization creation',
        'capabilities': ['data_processing', 'statistical_analysis', 'visualization', 'reporting'],
        'status': 'active',
        'model': 'claude-3.5-sonnet'
    },
    'web_automation': {
        'id': 'web_automation',
        'name': 'Web Automation Agent',
        'description': 'Handles web browsing, form filling, data extraction, and web-based automation',
        'capabilities': ['web_browsing', 'form_filling', 'data_extraction', 'web_scraping'],
        'status': 'active',
        'model': 'gpt-4'
    },
    'code_generation': {
        'id': 'code_generation',
        'name': 'Code Generation Agent',
        'description': 'Specializes in software development, code generation, debugging, and testing',
        'capabilities': ['code_generation', 'debugging', 'testing', 'deployment'],
        'status': 'active',
        'model': 'gpt-4'
    },
    'image_processing': {
        'id': 'image_processing',
        'name': 'Image Processing Agent',
        'description': 'Handles image generation, editing, and visual content creation',
        'capabilities': ['image_generation', 'image_editing', 'style_transfer', 'visual_design'],
        'status': 'active',
        'model': 'dall-e-3'
    },
    'video_processing': {
        'id': 'video_processing',
        'name': 'Video Processing Agent',
        'description': 'Creates and edits videos, animations, and multimedia content',
        'capabilities': ['video_generation', 'video_editing', 'animation', 'multimedia_creation'],
        'status': 'active',
        'model': 'runway-ml'
    },
    'audio_processing': {
        'id': 'audio_processing',
        'name': 'Audio Processing Agent',
        'description': 'Handles audio generation, speech synthesis, and audio editing',
        'capabilities': ['speech_synthesis', 'audio_generation', 'voice_cloning', 'audio_editing'],
        'status': 'active',
        'model': 'elevenlabs'
    }
}

@agents_bp.route('/', methods=['GET'])
@jwt_required()
def get_agents():
    """Get all available agents"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Filter agents based on user subscription
        available_agents = AVAILABLE_AGENTS.copy()
        
        # Free users have access to basic agents
        if user.subscription_type == 'free':
            restricted_agents = ['video_processing', 'audio_processing']
            for agent_id in restricted_agents:
                if agent_id in available_agents:
                    available_agents[agent_id]['status'] = 'premium_required'
        
        return jsonify({
            'agents': list(available_agents.values()),
            'total_count': len(available_agents)
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/<agent_id>', methods=['GET'])
@jwt_required()
def get_agent(agent_id):
    """Get details of a specific agent"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if agent_id not in AVAILABLE_AGENTS:
            return jsonify({'error': 'Agent not found'}), 404
        
        agent = AVAILABLE_AGENTS[agent_id].copy()
        
        # Check if user has access to this agent
        if user.subscription_type == 'free' and agent_id in ['video_processing', 'audio_processing']:
            agent['status'] = 'premium_required'
        
        return jsonify({'agent': agent}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/capabilities', methods=['GET'])
@jwt_required()
def get_capabilities():
    """Get all available capabilities across agents"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Collect all capabilities
        all_capabilities = set()
        for agent in AVAILABLE_AGENTS.values():
            all_capabilities.update(agent['capabilities'])
        
        # Group capabilities by category
        capability_categories = {
            'content_creation': [
                'text_generation', 'image_generation', 'video_generation', 
                'audio_generation', 'presentation_creation', 'visual_design'
            ],
            'data_processing': [
                'data_processing', 'statistical_analysis', 'visualization', 'reporting'
            ],
            'automation': [
                'web_browsing', 'form_filling', 'data_extraction', 'web_scraping'
            ],
            'development': [
                'code_generation', 'debugging', 'testing', 'deployment'
            ],
            'research': [
                'web_search', 'research', 'information_synthesis', 'fact_checking'
            ],
            'planning': [
                'strategic_planning', 'goal_decomposition', 'workflow_optimization',
                'task_planning', 'agent_coordination', 'workflow_management'
            ],
            'media_processing': [
                'image_editing', 'video_editing', 'audio_editing', 'style_transfer',
                'animation', 'multimedia_creation', 'speech_synthesis', 'voice_cloning'
            ]
        }
        
        return jsonify({
            'capabilities': sorted(list(all_capabilities)),
            'categories': capability_categories
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/status', methods=['GET'])
@jwt_required()
def get_agent_status():
    """Get status of all agents"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Simulate agent status (in real implementation, this would check actual agent health)
        agent_status = {}
        
        for agent_id, agent_info in AVAILABLE_AGENTS.items():
            # Check if user has access
            has_access = True
            if user.subscription_type == 'free' and agent_id in ['video_processing', 'audio_processing']:
                has_access = False
            
            agent_status[agent_id] = {
                'id': agent_id,
                'name': agent_info['name'],
                'status': 'active' if has_access else 'premium_required',
                'health': 'healthy',  # In real implementation, check actual health
                'load': 'low',  # In real implementation, check actual load
                'last_updated': '2025-01-26T12:00:00Z'  # In real implementation, use actual timestamp
            }
        
        return jsonify({
            'agent_status': agent_status,
            'overall_health': 'healthy',
            'total_agents': len(agent_status),
            'active_agents': len([s for s in agent_status.values() if s['status'] == 'active'])
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@agents_bp.route('/recommend', methods=['POST'])
@jwt_required()
def recommend_agents():
    """Recommend agents for a specific task"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('task_description'):
            return jsonify({'error': 'Task description is required'}), 400
        
        task_description = data['task_description'].lower()
        task_type = data.get('task_type', '').lower()
        
        # Simple keyword-based agent recommendation
        recommended_agents = []
        
        # Always include executor for coordination
        recommended_agents.append('executor')
        
        # Recommend based on keywords and task type
        if any(keyword in task_description for keyword in ['image', 'picture', 'photo', 'visual', 'design']) or task_type == 'image':
            recommended_agents.append('image_processing')
            recommended_agents.append('content_generation')
        
        if any(keyword in task_description for keyword in ['video', 'movie', 'animation', 'clip']) or task_type == 'video':
            recommended_agents.append('video_processing')
            recommended_agents.append('content_generation')
        
        if any(keyword in task_description for keyword in ['audio', 'voice', 'speech', 'sound']) or task_type == 'audio':
            recommended_agents.append('audio_processing')
            recommended_agents.append('content_generation')
        
        if any(keyword in task_description for keyword in ['code', 'program', 'software', 'app', 'website']) or task_type == 'code':
            recommended_agents.append('code_generation')
            recommended_agents.append('web_automation')
        
        if any(keyword in task_description for keyword in ['data', 'analysis', 'chart', 'graph', 'statistics']) or task_type == 'data':
            recommended_agents.append('data_analysis')
        
        if any(keyword in task_description for keyword in ['research', 'search', 'information', 'study']) or task_type == 'research':
            recommended_agents.append('knowledge')
            recommended_agents.append('web_automation')
        
        if any(keyword in task_description for keyword in ['presentation', 'slides', 'powerpoint']) or task_type == 'slides':
            recommended_agents.append('content_generation')
            recommended_agents.append('image_processing')
        
        if any(keyword in task_description for keyword in ['plan', 'strategy', 'organize']) or 'planning' in task_description:
            recommended_agents.append('planning')
        
        # Remove duplicates and ensure executor is first
        recommended_agents = list(dict.fromkeys(recommended_agents))
        if 'executor' in recommended_agents:
            recommended_agents.remove('executor')
            recommended_agents.insert(0, 'executor')
        
        # Get agent details
        agent_recommendations = []
        for agent_id in recommended_agents:
            if agent_id in AVAILABLE_AGENTS:
                agent = AVAILABLE_AGENTS[agent_id].copy()
                
                # Check access
                if user.subscription_type == 'free' and agent_id in ['video_processing', 'audio_processing']:
                    agent['status'] = 'premium_required'
                
                agent_recommendations.append(agent)
        
        return jsonify({
            'recommended_agents': agent_recommendations,
            'task_description': data['task_description'],
            'reasoning': 'Agents recommended based on task keywords and type analysis'
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


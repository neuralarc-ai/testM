#!/usr/bin/env python3
"""
Simplified Manus AI Clone Backend with Dummy Login
"""

from flask import Flask, request, jsonify
from flask_cors import CORS
import json
import uuid
from datetime import datetime, timedelta
import jwt

app = Flask(__name__)
CORS(app)

# Simple configuration
app.config['SECRET_KEY'] = 'demo-secret-key-12345'
JWT_SECRET = 'demo-jwt-secret-12345'

# In-memory storage for demo
users_db = {
    'demo@manus.ai': {
        'id': '1',
        'name': 'Demo User',
        'email': 'demo@manus.ai',
        'password': 'demo123',  # In real app, this would be hashed
        'credits': 1000,
        'subscription': 'premium',
        'created_at': '2024-01-01T00:00:00Z'
    },
    'admin@manus.ai': {
        'id': '2',
        'name': 'Admin User',
        'email': 'admin@manus.ai',
        'password': 'admin123',
        'credits': 5000,
        'subscription': 'enterprise',
        'created_at': '2024-01-01T00:00:00Z'
    }
}

tasks_db = {}
agents_db = {
    '1': {'id': '1', 'name': 'Content Creator', 'description': 'Creates text content and articles', 'capabilities': ['text_generation', 'content_writing']},
    '2': {'id': '2', 'name': 'Visual Designer', 'description': 'Generates images and visual content', 'capabilities': ['image_generation', 'design']},
    '3': {'id': '3', 'name': 'Code Developer', 'description': 'Writes and debugs code', 'capabilities': ['code_generation', 'debugging']},
    '4': {'id': '4', 'name': 'Research Specialist', 'description': 'Conducts research and analysis', 'capabilities': ['web_research', 'data_analysis']},
    '5': {'id': '5', 'name': 'Automation Expert', 'description': 'Automates web tasks and workflows', 'capabilities': ['web_automation', 'task_automation']},
}

def generate_token(user_id):
    """Generate JWT token for user"""
    payload = {
        'user_id': user_id,
        'exp': datetime.utcnow() + timedelta(days=7)
    }
    return jwt.encode(payload, JWT_SECRET, algorithm='HS256')

def verify_token(token):
    """Verify JWT token"""
    try:
        payload = jwt.decode(token, JWT_SECRET, algorithms=['HS256'])
        return payload['user_id']
    except:
        return None

@app.route('/')
def home():
    return jsonify({
        'message': 'Manus AI Clone Backend - Demo Version',
        'status': 'running',
        'version': '1.0.0-demo'
    })

@app.route('/health')
def health():
    return jsonify({
        'status': 'healthy',
        'service': 'manus-ai-clone-backend',
        'version': '1.0.0-demo'
    })

@app.route('/api')
def api_info():
    return jsonify({
        'name': 'Manus AI Clone API - Demo',
        'version': '1.0.0-demo',
        'description': 'Demo backend API for Manus AI Clone',
        'endpoints': {
            'auth': '/api/auth',
            'users': '/api/users',
            'tasks': '/api/tasks',
            'agents': '/api/agents'
        },
        'demo_credentials': {
            'email': 'demo@manus.ai',
            'password': 'demo123'
        }
    })

# Authentication endpoints
@app.route('/api/auth/login', methods=['POST'])
def login():
    try:
        data = request.get_json()
        email = data.get('email')
        password = data.get('password')
        
        if not email or not password:
            return jsonify({'success': False, 'error': 'Email and password required'}), 400
        
        user = users_db.get(email)
        if not user or user['password'] != password:
            return jsonify({'success': False, 'error': 'Invalid credentials'}), 401
        
        token = generate_token(user['id'])
        user_data = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/register', methods=['POST'])
def register():
    try:
        data = request.get_json()
        name = data.get('name')
        email = data.get('email')
        password = data.get('password')
        
        if not all([name, email, password]):
            return jsonify({'success': False, 'error': 'Name, email and password required'}), 400
        
        if email in users_db:
            return jsonify({'success': False, 'error': 'User already exists'}), 400
        
        user_id = str(len(users_db) + 1)
        user = {
            'id': user_id,
            'name': name,
            'email': email,
            'password': password,
            'credits': 300,
            'subscription': 'free',
            'created_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        users_db[email] = user
        token = generate_token(user_id)
        user_data = {k: v for k, v in user.items() if k != 'password'}
        
        return jsonify({
            'success': True,
            'token': token,
            'user': user_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/auth/profile', methods=['GET'])
def get_profile():
    try:
        auth_header = request.headers.get('Authorization')
        if not auth_header or not auth_header.startswith('Bearer '):
            return jsonify({'success': False, 'error': 'No token provided'}), 401
        
        token = auth_header.split(' ')[1]
        user_id = verify_token(token)
        if not user_id:
            return jsonify({'success': False, 'error': 'Invalid token'}), 401
        
        # Find user by ID
        user = None
        for u in users_db.values():
            if u['id'] == user_id:
                user = u
                break
        
        if not user:
            return jsonify({'success': False, 'error': 'User not found'}), 404
        
        user_data = {k: v for k, v in user.items() if k != 'password'}
        return jsonify({
            'success': True,
            'user': user_data
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

# Agents endpoints
@app.route('/api/agents', methods=['GET'])
def get_agents():
    return jsonify({
        'success': True,
        'agents': list(agents_db.values())
    })

@app.route('/api/agents/<agent_id>', methods=['GET'])
def get_agent(agent_id):
    agent = agents_db.get(agent_id)
    if not agent:
        return jsonify({'success': False, 'error': 'Agent not found'}), 404
    
    return jsonify({
        'success': True,
        'agent': agent
    })

# Tasks endpoints
@app.route('/api/tasks', methods=['GET'])
def get_tasks():
    return jsonify({
        'success': True,
        'tasks': list(tasks_db.values())
    })

@app.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        data = request.get_json()
        task_id = str(uuid.uuid4())
        
        task = {
            'id': task_id,
            'title': data.get('title', 'New Task'),
            'description': data.get('description', ''),
            'type': data.get('type', 'general'),
            'status': 'pending',
            'created_at': datetime.utcnow().isoformat() + 'Z',
            'updated_at': datetime.utcnow().isoformat() + 'Z'
        }
        
        tasks_db[task_id] = task
        
        return jsonify({
            'success': True,
            'task': task
        })
    except Exception as e:
        return jsonify({'success': False, 'error': str(e)}), 500

@app.route('/api/tasks/<task_id>', methods=['GET'])
def get_task(task_id):
    task = tasks_db.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    
    return jsonify({
        'success': True,
        'task': task
    })

@app.route('/api/tasks/<task_id>/execute', methods=['POST'])
def execute_task(task_id):
    task = tasks_db.get(task_id)
    if not task:
        return jsonify({'success': False, 'error': 'Task not found'}), 404
    
    # Simulate task execution
    task['status'] = 'running'
    task['updated_at'] = datetime.utcnow().isoformat() + 'Z'
    
    return jsonify({
        'success': True,
        'message': 'Task execution started',
        'task': task
    })

# Demo endpoints
@app.route('/api/demo/info', methods=['GET'])
def demo_info():
    return jsonify({
        'success': True,
        'demo': True,
        'message': 'This is a demo version of Manus AI Clone',
        'features': [
            'User authentication with dummy accounts',
            'Task management system',
            'AI agent selection',
            'Basic API functionality'
        ],
        'demo_accounts': [
            {'email': 'demo@manus.ai', 'password': 'demo123', 'role': 'user'},
            {'email': 'admin@manus.ai', 'password': 'admin123', 'role': 'admin'}
        ]
    })

if __name__ == '__main__':
    print("🚀 Starting Manus AI Clone Backend (Demo Version)")
    print("📧 Demo Login: demo@manus.ai / demo123")
    print("🔧 Admin Login: admin@manus.ai / admin123")
    print("🌐 Server running on http://localhost:8001")
    app.run(host='0.0.0.0', port=8001, debug=True)


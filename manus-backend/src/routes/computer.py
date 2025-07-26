from flask import Blueprint, request, jsonify, current_app
from flask_jwt_extended import jwt_required, get_jwt_identity
import uuid
import asyncio

from ..services.computer_service import computer_service

computer_bp = Blueprint('computer', __name__)

@computer_bp.route('/sessions', methods=['POST'])
@jwt_required()
def create_browser_session():
    """Create a new browser automation session"""
    try:
        user_id = get_jwt_identity()
        session_id = f"{user_id}_{uuid.uuid4().hex[:8]}"
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.create_browser_session(session_id)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error creating browser session: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create browser session'}), 500

@computer_bp.route('/sessions', methods=['GET'])
@jwt_required()
def get_active_sessions():
    """Get list of active browser sessions"""
    try:
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.get_active_sessions()
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error getting sessions: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to get sessions'}), 500

@computer_bp.route('/sessions/<session_id>', methods=['DELETE'])
@jwt_required()
def close_browser_session(session_id):
    """Close a browser session"""
    try:
        user_id = get_jwt_identity()
        
        # Verify session belongs to user
        if not session_id.startswith(user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.close_session(session_id)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error closing session: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to close session'}), 500

@computer_bp.route('/navigate', methods=['POST'])
@jwt_required()
def navigate_to_url():
    """Navigate to a URL in a browser session"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        url = data.get('url')
        
        if not session_id or not url:
            return jsonify({'success': False, 'error': 'session_id and url are required'}), 400
        
        user_id = get_jwt_identity()
        
        # Verify session belongs to user
        if not session_id.startswith(user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.navigate_to_url(session_id, url)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error navigating: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to navigate'}), 500

@computer_bp.route('/click', methods=['POST'])
@jwt_required()
def click_element():
    """Click an element on the page"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        selector = data.get('selector')
        selector_type = data.get('selector_type', 'css')
        
        if not session_id or not selector:
            return jsonify({'success': False, 'error': 'session_id and selector are required'}), 400
        
        user_id = get_jwt_identity()
        
        # Verify session belongs to user
        if not session_id.startswith(user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.click_element(session_id, selector, selector_type)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error clicking element: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to click element'}), 500

@computer_bp.route('/type', methods=['POST'])
@jwt_required()
def type_text():
    """Type text into an input field"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        selector = data.get('selector')
        text = data.get('text')
        selector_type = data.get('selector_type', 'css')
        
        if not session_id or not selector or not text:
            return jsonify({'success': False, 'error': 'session_id, selector, and text are required'}), 400
        
        user_id = get_jwt_identity()
        
        # Verify session belongs to user
        if not session_id.startswith(user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.type_text(session_id, selector, text, selector_type)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error typing text: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to type text'}), 500

@computer_bp.route('/scroll', methods=['POST'])
@jwt_required()
def scroll_page():
    """Scroll the page"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        direction = data.get('direction', 'down')
        amount = data.get('amount', 3)
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id is required'}), 400
        
        user_id = get_jwt_identity()
        
        # Verify session belongs to user
        if not session_id.startswith(user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.scroll_page(session_id, direction, amount)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error scrolling: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to scroll'}), 500

@computer_bp.route('/extract', methods=['POST'])
@jwt_required()
def extract_page_content():
    """Extract content from the current page"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        
        if not session_id:
            return jsonify({'success': False, 'error': 'session_id is required'}), 400
        
        user_id = get_jwt_identity()
        
        # Verify session belongs to user
        if not session_id.startswith(user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.extract_page_content(session_id)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error extracting content: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to extract content'}), 500

@computer_bp.route('/execute-js', methods=['POST'])
@jwt_required()
def execute_javascript():
    """Execute JavaScript on the current page"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        script = data.get('script')
        
        if not session_id or not script:
            return jsonify({'success': False, 'error': 'session_id and script are required'}), 400
        
        user_id = get_jwt_identity()
        
        # Verify session belongs to user
        if not session_id.startswith(user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.execute_javascript(session_id, script)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error executing JavaScript: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to execute JavaScript'}), 500

@computer_bp.route('/wait', methods=['POST'])
@jwt_required()
def wait_for_element():
    """Wait for an element to appear on the page"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        selector = data.get('selector')
        timeout = data.get('timeout', 10)
        selector_type = data.get('selector_type', 'css')
        
        if not session_id or not selector:
            return jsonify({'success': False, 'error': 'session_id and selector are required'}), 400
        
        user_id = get_jwt_identity()
        
        # Verify session belongs to user
        if not session_id.startswith(user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.wait_for_element(session_id, selector, timeout, selector_type)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error waiting for element: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to wait for element'}), 500

@computer_bp.route('/automate', methods=['POST'])
@jwt_required()
def automate_task():
    """Use AI to automate a web task"""
    try:
        data = request.get_json()
        session_id = data.get('session_id')
        task_description = data.get('task_description')
        url = data.get('url')
        
        if not session_id or not task_description:
            return jsonify({'success': False, 'error': 'session_id and task_description are required'}), 400
        
        user_id = get_jwt_identity()
        
        # Verify session belongs to user
        if not session_id.startswith(user_id):
            return jsonify({'success': False, 'error': 'Unauthorized'}), 403
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.automate_task_with_ai(session_id, task_description, url)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error automating task: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to automate task'}), 500

@computer_bp.route('/cleanup', methods=['POST'])
@jwt_required()
def cleanup_sessions():
    """Clean up old browser sessions"""
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 2)
        
        # Run async function
        loop = asyncio.new_event_loop()
        asyncio.set_event_loop(loop)
        result = loop.run_until_complete(
            computer_service.cleanup_old_sessions(max_age_hours)
        )
        loop.close()
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up sessions: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to cleanup sessions'}), 500


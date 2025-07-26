from flask import Blueprint, request, jsonify, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
from datetime import datetime
import os
import uuid
from werkzeug.utils import secure_filename
from src.models.user import User, db

content_bp = Blueprint('content', __name__)

# Content storage configuration
UPLOAD_FOLDER = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'uploads')
ALLOWED_EXTENSIONS = {
    'image': {'png', 'jpg', 'jpeg', 'gif', 'webp', 'svg'},
    'video': {'mp4', 'avi', 'mov', 'wmv', 'flv', 'webm'},
    'audio': {'mp3', 'wav', 'ogg', 'aac', 'm4a'},
    'document': {'pdf', 'doc', 'docx', 'txt', 'md', 'html'},
    'presentation': {'ppt', 'pptx', 'pdf'},
    'data': {'csv', 'xlsx', 'json', 'xml'}
}

# Ensure upload directory exists
os.makedirs(UPLOAD_FOLDER, exist_ok=True)

def allowed_file(filename, content_type):
    """Check if file extension is allowed for the content type"""
    if '.' not in filename:
        return False
    
    extension = filename.rsplit('.', 1)[1].lower()
    return extension in ALLOWED_EXTENSIONS.get(content_type, set())

def get_content_type_from_extension(filename):
    """Determine content type from file extension"""
    if '.' not in filename:
        return 'unknown'
    
    extension = filename.rsplit('.', 1)[1].lower()
    
    for content_type, extensions in ALLOWED_EXTENSIONS.items():
        if extension in extensions:
            return content_type
    
    return 'unknown'

# Content model (simplified - in production, use a proper database table)
class Content:
    def __init__(self, id, user_id, filename, original_filename, content_type, file_size, task_id=None):
        self.id = id
        self.user_id = user_id
        self.filename = filename
        self.original_filename = original_filename
        self.content_type = content_type
        self.file_size = file_size
        self.task_id = task_id
        self.created_at = datetime.utcnow()
        self.url = f"/api/content/{id}/download"
    
    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'filename': self.original_filename,
            'content_type': self.content_type,
            'file_size': self.file_size,
            'task_id': self.task_id,
            'url': self.url,
            'created_at': self.created_at.isoformat()
        }

# In-memory content storage (in production, use database)
content_storage = {}

@content_bp.route('/upload', methods=['POST'])
@jwt_required()
def upload_content():
    """Upload content file"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        if 'file' not in request.files:
            return jsonify({'error': 'No file provided'}), 400
        
        file = request.files['file']
        content_type = request.form.get('content_type', 'unknown')
        task_id = request.form.get('task_id')
        
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400
        
        # Auto-detect content type if not provided
        if content_type == 'unknown':
            content_type = get_content_type_from_extension(file.filename)
        
        if not allowed_file(file.filename, content_type):
            return jsonify({
                'error': f'File type not allowed for {content_type}',
                'allowed_extensions': list(ALLOWED_EXTENSIONS.get(content_type, set()))
            }), 400
        
        # Generate unique filename
        file_id = str(uuid.uuid4())
        extension = file.filename.rsplit('.', 1)[1].lower() if '.' in file.filename else ''
        filename = f"{file_id}.{extension}" if extension else file_id
        
        # Save file
        file_path = os.path.join(UPLOAD_FOLDER, filename)
        file.save(file_path)
        
        # Get file size
        file_size = os.path.getsize(file_path)
        
        # Create content record
        content = Content(
            id=file_id,
            user_id=current_user_id,
            filename=filename,
            original_filename=secure_filename(file.filename),
            content_type=content_type,
            file_size=file_size,
            task_id=task_id
        )
        
        content_storage[file_id] = content
        
        return jsonify({
            'message': 'File uploaded successfully',
            'content': content.to_dict()
        }), 201
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/', methods=['GET'])
@jwt_required()
def get_content_list():
    """Get list of user's content"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Filter parameters
        content_type = request.args.get('content_type')
        task_id = request.args.get('task_id')
        page = request.args.get('page', 1, type=int)
        per_page = request.args.get('per_page', 20, type=int)
        
        # Filter user's content
        user_content = [
            content for content in content_storage.values()
            if content.user_id == current_user_id
        ]
        
        # Apply filters
        if content_type:
            user_content = [c for c in user_content if c.content_type == content_type]
        
        if task_id:
            user_content = [c for c in user_content if c.task_id == task_id]
        
        # Sort by creation date (newest first)
        user_content.sort(key=lambda x: x.created_at, reverse=True)
        
        # Pagination
        start = (page - 1) * per_page
        end = start + per_page
        paginated_content = user_content[start:end]
        
        return jsonify({
            'content': [content.to_dict() for content in paginated_content],
            'pagination': {
                'page': page,
                'per_page': per_page,
                'total': len(user_content),
                'pages': (len(user_content) + per_page - 1) // per_page
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/<content_id>', methods=['GET'])
@jwt_required()
def get_content_info(content_id):
    """Get content information"""
    try:
        current_user_id = get_jwt_identity()
        
        if content_id not in content_storage:
            return jsonify({'error': 'Content not found'}), 404
        
        content = content_storage[content_id]
        
        if content.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        return jsonify({'content': content.to_dict()}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/<content_id>/download', methods=['GET'])
@jwt_required()
def download_content(content_id):
    """Download content file"""
    try:
        current_user_id = get_jwt_identity()
        
        if content_id not in content_storage:
            return jsonify({'error': 'Content not found'}), 404
        
        content = content_storage[content_id]
        
        if content.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        file_path = os.path.join(UPLOAD_FOLDER, content.filename)
        
        if not os.path.exists(file_path):
            return jsonify({'error': 'File not found on disk'}), 404
        
        return send_file(
            file_path,
            as_attachment=True,
            download_name=content.original_filename
        )
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/<content_id>', methods=['DELETE'])
@jwt_required()
def delete_content(content_id):
    """Delete content"""
    try:
        current_user_id = get_jwt_identity()
        
        if content_id not in content_storage:
            return jsonify({'error': 'Content not found'}), 404
        
        content = content_storage[content_id]
        
        if content.user_id != current_user_id:
            return jsonify({'error': 'Access denied'}), 403
        
        # Delete file from disk
        file_path = os.path.join(UPLOAD_FOLDER, content.filename)
        if os.path.exists(file_path):
            os.remove(file_path)
        
        # Remove from storage
        del content_storage[content_id]
        
        return jsonify({'message': 'Content deleted successfully'}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/types', methods=['GET'])
@jwt_required()
def get_content_types():
    """Get available content types and their allowed extensions"""
    try:
        return jsonify({
            'content_types': ALLOWED_EXTENSIONS,
            'description': {
                'image': 'Images and graphics',
                'video': 'Video files and animations',
                'audio': 'Audio files and recordings',
                'document': 'Text documents and reports',
                'presentation': 'Presentation slides',
                'data': 'Data files and spreadsheets'
            }
        }), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/stats', methods=['GET'])
@jwt_required()
def get_content_stats():
    """Get content statistics for the user"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        # Get user's content
        user_content = [
            content for content in content_storage.values()
            if content.user_id == current_user_id
        ]
        
        # Calculate statistics
        stats = {
            'total_files': len(user_content),
            'total_size': sum(content.file_size for content in user_content),
            'by_type': {},
            'recent_uploads': 0
        }
        
        # Count by type
        for content in user_content:
            content_type = content.content_type
            if content_type not in stats['by_type']:
                stats['by_type'][content_type] = {'count': 0, 'size': 0}
            
            stats['by_type'][content_type]['count'] += 1
            stats['by_type'][content_type]['size'] += content.file_size
        
        # Count recent uploads (last 7 days)
        from datetime import timedelta
        week_ago = datetime.utcnow() - timedelta(days=7)
        stats['recent_uploads'] = len([
            content for content in user_content
            if content.created_at >= week_ago
        ])
        
        return jsonify({'stats': stats}), 200
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@content_bp.route('/generate', methods=['POST'])
@jwt_required()
def generate_content():
    """Generate content using AI (placeholder for actual implementation)"""
    try:
        current_user_id = get_jwt_identity()
        user = User.query.get(current_user_id)
        
        if not user:
            return jsonify({'error': 'User not found'}), 404
        
        data = request.get_json()
        
        if not data or not data.get('content_type') or not data.get('prompt'):
            return jsonify({'error': 'Content type and prompt are required'}), 400
        
        content_type = data['content_type']
        prompt = data['prompt']
        
        # Validate content type
        if content_type not in ALLOWED_EXTENSIONS:
            return jsonify({'error': 'Invalid content type'}), 400
        
        # TODO: Implement actual content generation using AI APIs
        # This is a placeholder that would integrate with OpenAI, Anthropic, etc.
        
        return jsonify({
            'message': 'Content generation initiated',
            'content_type': content_type,
            'prompt': prompt,
            'status': 'processing',
            'note': 'This is a placeholder. Actual AI integration will be implemented in the next phase.'
        }), 202
        
    except Exception as e:
        return jsonify({'error': str(e)}), 500


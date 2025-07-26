from flask import Blueprint, request, jsonify, current_app, send_file
from flask_jwt_extended import jwt_required, get_jwt_identity
import os
import json
import base64
import asyncio
from werkzeug.utils import secure_filename

from ..services.media_service import media_service
from ..services.ai_service import ai_service

media_bp = Blueprint('media', __name__)

def run_async(coro):
    """Helper function to run async functions in sync context"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()

@media_bp.route('/presentations', methods=['POST'])
@jwt_required()
def generate_presentation():
    """Generate a presentation from content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        title = data.get('title')
        slides = data.get('slides', [])
        theme = data.get('theme', 'professional')
        
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        # Generate presentation using media service
        result = run_async(media_service.generate_presentation({
            'title': title,
            'slides': slides,
            'theme': theme
        }))
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error generating presentation: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate presentation'}), 500

@media_bp.route('/presentations/ai-generate', methods=['POST'])
@jwt_required()
def ai_generate_presentation():
    """Generate a presentation using AI"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        topic = data.get('topic')
        slide_count = data.get('slide_count', 5)
        style = data.get('style', 'professional')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        
        # Generate presentation content using AI
        prompt = f"""
        Create a {slide_count}-slide presentation about "{topic}".
        
        For each slide, provide:
        1. A clear, engaging title
        2. Bullet points or content (2-4 points per slide)
        3. Any relevant data or examples
        
        Make it {style} in tone and suitable for a business audience.
        
        Format your response as JSON with this structure:
        {{
            "title": "Main presentation title",
            "slides": [
                {{
                    "title": "Slide title",
                    "content": "Slide content in markdown format"
                }}
            ]
        }}
        """
        
        ai_result = run_async(ai_service.generate_text(prompt, model="gpt-4", max_tokens=2000))
        
        if not ai_result['success']:
            return jsonify({'success': False, 'error': 'AI generation failed'}), 500
        
        try:
            presentation_data = json.loads(ai_result['content'])
        except json.JSONDecodeError:
            return jsonify({'success': False, 'error': 'Invalid AI response format'}), 500
        
        # Generate the actual presentation
        presentation_data['theme'] = style
        result = run_async(media_service.generate_presentation(presentation_data))
        
        if result['success']:
            result['ai_generated'] = True
            result['topic'] = topic
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error generating AI presentation: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate AI presentation'}), 500

@media_bp.route('/documents', methods=['POST'])
@jwt_required()
def generate_document():
    """Generate a document from content"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        title = data.get('title')
        body = data.get('body')
        format_type = data.get('format', 'pdf')
        style = data.get('style', 'professional')
        
        if not title or not body:
            return jsonify({'success': False, 'error': 'Title and body are required'}), 400
        
        # Generate document using media service
        result = run_async(media_service.generate_document({
            'title': title,
            'body': body,
            'format': format_type,
            'style': style
        }))
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error generating document: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate document'}), 500

@media_bp.route('/documents/ai-generate', methods=['POST'])
@jwt_required()
def ai_generate_document():
    """Generate a document using AI"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        topic = data.get('topic')
        document_type = data.get('type', 'article')
        length = data.get('length', 'medium')
        tone = data.get('tone', 'professional')
        format_type = data.get('format', 'pdf')
        
        if not topic:
            return jsonify({'success': False, 'error': 'Topic is required'}), 400
        
        # Determine word count based on length
        word_counts = {
            'short': '300-500 words',
            'medium': '800-1200 words',
            'long': '1500-2500 words'
        }
        
        word_count = word_counts.get(length, '800-1200 words')
        
        # Generate document content using AI
        prompt = f"""
        Write a comprehensive {document_type} about "{topic}".
        
        Requirements:
        - Length: {word_count}
        - Tone: {tone}
        - Format: Well-structured with clear headings and sections
        - Include relevant examples, data, or case studies where appropriate
        
        Structure the content with:
        1. Introduction
        2. Main sections (3-5 sections)
        3. Conclusion
        
        Use markdown formatting for headings, lists, and emphasis.
        Make it engaging and informative for the target audience.
        """
        
        ai_result = run_async(ai_service.generate_text(prompt, model="gpt-4", max_tokens=3000))
        
        if not ai_result['success']:
            return jsonify({'success': False, 'error': 'AI generation failed'}), 500
        
        # Generate the actual document
        result = run_async(media_service.generate_document({
            'title': topic,
            'body': ai_result['content'],
            'format': format_type,
            'style': tone
        }))
        
        if result['success']:
            result['ai_generated'] = True
            result['topic'] = topic
            result['document_type'] = document_type
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error generating AI document: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate AI document'}), 500

@media_bp.route('/audio/process', methods=['POST'])
@jwt_required()
def process_audio():
    """Process audio file"""
    try:
        user_id = get_jwt_identity()
        
        if 'audio' not in request.files:
            return jsonify({'success': False, 'error': 'No audio file provided'}), 400
        
        audio_file = request.files['audio']
        operation = request.form.get('operation', 'transcribe')
        parameters = json.loads(request.form.get('parameters', '{}'))
        
        if audio_file.filename == '':
            return jsonify({'success': False, 'error': 'No audio file selected'}), 400
        
        # Read audio data
        audio_data = audio_file.read()
        
        # Process audio using media service
        result = run_async(media_service.process_audio(audio_data, operation, parameters))
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error processing audio: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process audio'}), 500

@media_bp.route('/audio/generate-speech', methods=['POST'])
@jwt_required()
def generate_speech():
    """Generate speech from text"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        text = data.get('text')
        voice = data.get('voice', 'alloy')
        speed = data.get('speed', 1.0)
        
        if not text:
            return jsonify({'success': False, 'error': 'Text is required'}), 400
        
        # Generate speech using AI service
        result = run_async(ai_service.generate_speech(text, voice, speed))
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error generating speech: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate speech'}), 500

@media_bp.route('/images/process', methods=['POST'])
@jwt_required()
def process_image():
    """Process image file"""
    try:
        user_id = get_jwt_identity()
        
        if 'image' not in request.files:
            return jsonify({'success': False, 'error': 'No image file provided'}), 400
        
        image_file = request.files['image']
        operation = request.form.get('operation', 'analyze')
        parameters = json.loads(request.form.get('parameters', '{}'))
        
        if image_file.filename == '':
            return jsonify({'success': False, 'error': 'No image file selected'}), 400
        
        # Read image data
        image_data = image_file.read()
        
        # Process image using media service
        result = run_async(media_service.process_image(image_data, operation, parameters))
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error processing image: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to process image'}), 500

@media_bp.route('/images/generate', methods=['POST'])
@jwt_required()
def generate_image():
    """Generate image using AI"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        prompt = data.get('prompt')
        style = data.get('style', 'realistic')
        size = data.get('size', '1024x1024')
        quality = data.get('quality', 'standard')
        
        if not prompt:
            return jsonify({'success': False, 'error': 'Prompt is required'}), 400
        
        # Generate image using AI service
        result = run_async(ai_service.generate_image(prompt, style, size, quality))
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error generating image: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to generate image'}), 500

@media_bp.route('/infographics', methods=['POST'])
@jwt_required()
def create_infographic():
    """Create an infographic from data"""
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        
        title = data.get('title')
        sections = data.get('sections', [])
        style = data.get('style', 'modern')
        
        if not title:
            return jsonify({'success': False, 'error': 'Title is required'}), 400
        
        # Create infographic using media service
        result = run_async(media_service.create_infographic({
            'title': title,
            'sections': sections,
            'style': style
        }))
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error creating infographic: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to create infographic'}), 500

@media_bp.route('/files/<file_id>/download', methods=['GET'])
@jwt_required()
def download_file(file_id):
    """Download a generated media file"""
    try:
        user_id = get_jwt_identity()
        
        # Find file by ID
        temp_dir = media_service.temp_dir
        
        possible_files = [
            f"presentation_{file_id}.html",
            f"presentation_{file_id}.pdf",
            f"document_{file_id}.pdf",
            f"document_{file_id}.html",
            f"document_{file_id}.md",
            f"infographic_{file_id}.png"
        ]
        
        file_path = None
        for filename in possible_files:
            potential_path = os.path.join(temp_dir, filename)
            if os.path.exists(potential_path):
                file_path = potential_path
                break
        
        if not file_path:
            return jsonify({'success': False, 'error': 'File not found'}), 404
        
        return send_file(file_path, as_attachment=True)
        
    except Exception as e:
        current_app.logger.error(f"Error downloading file: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to download file'}), 500

@media_bp.route('/cleanup', methods=['POST'])
@jwt_required()
def cleanup_temp_files():
    """Clean up old temporary files"""
    try:
        data = request.get_json() or {}
        max_age_hours = data.get('max_age_hours', 24)
        
        result = media_service.cleanup_temp_files(max_age_hours)
        
        return jsonify(result)
        
    except Exception as e:
        current_app.logger.error(f"Error cleaning up files: {str(e)}")
        return jsonify({'success': False, 'error': 'Failed to cleanup files'}), 500


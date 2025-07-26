import os
import json
import base64
import tempfile
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from PIL import Image, ImageDraw, ImageFont
import requests
import io
from reportlab.lib.pagesizes import letter, A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Image as RLImage
from reportlab.lib.styles import getSampleStyleSheet, ParagraphStyle
from reportlab.lib.units import inch
from reportlab.lib import colors
import markdown
from weasyprint import HTML, CSS
import tempfile
import subprocess

from .ai_service import ai_service

class MediaService:
    def __init__(self):
        self.temp_dir = tempfile.gettempdir()
        self.supported_formats = {
            'image': ['png', 'jpg', 'jpeg', 'gif', 'webp'],
            'video': ['mp4', 'avi', 'mov', 'webm'],
            'audio': ['mp3', 'wav', 'ogg', 'm4a'],
            'document': ['pdf', 'docx', 'txt', 'md', 'html']
        }
    
    async def generate_presentation(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a presentation from content"""
        try:
            title = content.get('title', 'Untitled Presentation')
            slides = content.get('slides', [])
            theme = content.get('theme', 'professional')
            
            # Generate HTML presentation
            html_content = self._create_html_presentation(title, slides, theme)
            
            # Save to file
            presentation_id = str(uuid.uuid4())
            html_file = os.path.join(self.temp_dir, f"presentation_{presentation_id}.html")
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            # Generate PDF version
            pdf_file = os.path.join(self.temp_dir, f"presentation_{presentation_id}.pdf")
            HTML(html_file).write_pdf(pdf_file)
            
            return {
                'success': True,
                'presentation_id': presentation_id,
                'html_file': html_file,
                'pdf_file': pdf_file,
                'slide_count': len(slides)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate presentation: {str(e)}'
            }
    
    def _create_html_presentation(self, title: str, slides: List[Dict], theme: str) -> str:
        """Create HTML presentation content"""
        theme_styles = {
            'professional': {
                'background': '#f8f9fa',
                'primary': '#2c3e50',
                'secondary': '#3498db',
                'text': '#2c3e50'
            },
            'modern': {
                'background': '#1a1a1a',
                'primary': '#ffffff',
                'secondary': '#00d4aa',
                'text': '#ffffff'
            },
            'minimal': {
                'background': '#ffffff',
                'primary': '#333333',
                'secondary': '#007acc',
                'text': '#333333'
            }
        }
        
        style = theme_styles.get(theme, theme_styles['professional'])
        
        html = f"""
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <title>{title}</title>
            <style>
                body {{
                    font-family: 'Arial', sans-serif;
                    margin: 0;
                    padding: 0;
                    background: {style['background']};
                    color: {style['text']};
                }}
                .slide {{
                    width: 100vw;
                    height: 100vh;
                    display: flex;
                    flex-direction: column;
                    justify-content: center;
                    align-items: center;
                    padding: 2rem;
                    box-sizing: border-box;
                    page-break-after: always;
                }}
                .slide h1 {{
                    font-size: 3rem;
                    color: {style['primary']};
                    text-align: center;
                    margin-bottom: 1rem;
                }}
                .slide h2 {{
                    font-size: 2.5rem;
                    color: {style['primary']};
                    text-align: center;
                    margin-bottom: 1.5rem;
                }}
                .slide h3 {{
                    font-size: 2rem;
                    color: {style['secondary']};
                    margin-bottom: 1rem;
                }}
                .slide p {{
                    font-size: 1.5rem;
                    line-height: 1.6;
                    text-align: center;
                    max-width: 80%;
                    margin-bottom: 1rem;
                }}
                .slide ul {{
                    font-size: 1.3rem;
                    line-height: 1.8;
                    max-width: 80%;
                }}
                .slide li {{
                    margin-bottom: 0.5rem;
                }}
                .title-slide {{
                    background: linear-gradient(135deg, {style['primary']}, {style['secondary']});
                    color: white;
                }}
                .content-slide {{
                    background: {style['background']};
                }}
                .image-container {{
                    max-width: 60%;
                    max-height: 60%;
                    margin: 1rem 0;
                }}
                .image-container img {{
                    max-width: 100%;
                    max-height: 100%;
                    object-fit: contain;
                }}
            </style>
        </head>
        <body>
        """
        
        # Title slide
        html += f"""
        <div class="slide title-slide">
            <h1>{title}</h1>
            <p>Generated by Manus AI</p>
        </div>
        """
        
        # Content slides
        for i, slide in enumerate(slides):
            slide_title = slide.get('title', f'Slide {i + 1}')
            slide_content = slide.get('content', '')
            slide_image = slide.get('image', '')
            
            html += f"""
            <div class="slide content-slide">
                <h2>{slide_title}</h2>
            """
            
            if slide_image:
                html += f"""
                <div class="image-container">
                    <img src="{slide_image}" alt="{slide_title}">
                </div>
                """
            
            # Convert markdown to HTML
            if slide_content:
                content_html = markdown.markdown(slide_content)
                html += content_html
            
            html += "</div>"
        
        html += """
        </body>
        </html>
        """
        
        return html
    
    async def generate_document(self, content: Dict[str, Any]) -> Dict[str, Any]:
        """Generate a document from content"""
        try:
            title = content.get('title', 'Untitled Document')
            body = content.get('body', '')
            format_type = content.get('format', 'pdf')
            style = content.get('style', 'professional')
            
            document_id = str(uuid.uuid4())
            
            if format_type == 'pdf':
                return await self._generate_pdf_document(document_id, title, body, style)
            elif format_type == 'html':
                return await self._generate_html_document(document_id, title, body, style)
            elif format_type == 'markdown':
                return await self._generate_markdown_document(document_id, title, body)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported document format: {format_type}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate document: {str(e)}'
            }
    
    async def _generate_pdf_document(self, doc_id: str, title: str, body: str, style: str) -> Dict[str, Any]:
        """Generate PDF document"""
        try:
            pdf_file = os.path.join(self.temp_dir, f"document_{doc_id}.pdf")
            
            # Create PDF using ReportLab
            doc = SimpleDocTemplate(pdf_file, pagesize=letter)
            styles = getSampleStyleSheet()
            
            # Custom styles based on style parameter
            if style == 'professional':
                title_style = ParagraphStyle(
                    'CustomTitle',
                    parent=styles['Heading1'],
                    fontSize=24,
                    spaceAfter=30,
                    textColor=colors.HexColor('#2c3e50')
                )
                body_style = ParagraphStyle(
                    'CustomBody',
                    parent=styles['Normal'],
                    fontSize=12,
                    leading=18,
                    spaceAfter=12
                )
            else:
                title_style = styles['Heading1']
                body_style = styles['Normal']
            
            # Build document content
            story = []
            story.append(Paragraph(title, title_style))
            story.append(Spacer(1, 20))
            
            # Convert markdown to paragraphs
            paragraphs = body.split('\n\n')
            for para in paragraphs:
                if para.strip():
                    story.append(Paragraph(para.strip(), body_style))
                    story.append(Spacer(1, 12))
            
            doc.build(story)
            
            return {
                'success': True,
                'document_id': doc_id,
                'file_path': pdf_file,
                'format': 'pdf'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate PDF: {str(e)}'
            }
    
    async def _generate_html_document(self, doc_id: str, title: str, body: str, style: str) -> Dict[str, Any]:
        """Generate HTML document"""
        try:
            html_file = os.path.join(self.temp_dir, f"document_{doc_id}.html")
            
            # Convert markdown to HTML
            body_html = markdown.markdown(body)
            
            # Style templates
            style_css = {
                'professional': """
                    body { font-family: 'Georgia', serif; max-width: 800px; margin: 0 auto; padding: 2rem; line-height: 1.6; }
                    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 0.5rem; }
                    h2, h3 { color: #34495e; }
                    p { margin-bottom: 1rem; }
                """,
                'modern': """
                    body { font-family: 'Arial', sans-serif; max-width: 900px; margin: 0 auto; padding: 2rem; background: #f8f9fa; }
                    h1 { color: #007acc; font-weight: 300; font-size: 2.5rem; }
                    h2, h3 { color: #333; font-weight: 400; }
                    p { color: #555; line-height: 1.8; }
                """
            }
            
            css = style_css.get(style, style_css['professional'])
            
            html_content = f"""
            <!DOCTYPE html>
            <html lang="en">
            <head>
                <meta charset="UTF-8">
                <meta name="viewport" content="width=device-width, initial-scale=1.0">
                <title>{title}</title>
                <style>{css}</style>
            </head>
            <body>
                <h1>{title}</h1>
                {body_html}
            </body>
            </html>
            """
            
            with open(html_file, 'w', encoding='utf-8') as f:
                f.write(html_content)
            
            return {
                'success': True,
                'document_id': doc_id,
                'file_path': html_file,
                'format': 'html'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate HTML: {str(e)}'
            }
    
    async def _generate_markdown_document(self, doc_id: str, title: str, body: str) -> Dict[str, Any]:
        """Generate Markdown document"""
        try:
            md_file = os.path.join(self.temp_dir, f"document_{doc_id}.md")
            
            content = f"# {title}\n\n{body}"
            
            with open(md_file, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                'success': True,
                'document_id': doc_id,
                'file_path': md_file,
                'format': 'markdown'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate Markdown: {str(e)}'
            }
    
    async def process_audio(self, audio_data: bytes, operation: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process audio data"""
        try:
            if parameters is None:
                parameters = {}
            
            audio_id = str(uuid.uuid4())
            input_file = os.path.join(self.temp_dir, f"audio_input_{audio_id}.wav")
            output_file = os.path.join(self.temp_dir, f"audio_output_{audio_id}.wav")
            
            # Save input audio
            with open(input_file, 'wb') as f:
                f.write(audio_data)
            
            if operation == 'transcribe':
                return await self._transcribe_audio(input_file)
            elif operation == 'enhance':
                return await self._enhance_audio(input_file, output_file, parameters)
            elif operation == 'convert':
                return await self._convert_audio(input_file, output_file, parameters)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported audio operation: {operation}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to process audio: {str(e)}'
            }
    
    async def _transcribe_audio(self, audio_file: str) -> Dict[str, Any]:
        """Transcribe audio to text using OpenAI Whisper"""
        try:
            with open(audio_file, 'rb') as f:
                # Use OpenAI Whisper API for transcription
                result = await ai_service.openai_client.audio.transcriptions.create(
                    model="whisper-1",
                    file=f
                )
            
            return {
                'success': True,
                'transcription': result.text,
                'operation': 'transcribe'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to transcribe audio: {str(e)}'
            }
    
    async def _enhance_audio(self, input_file: str, output_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance audio quality"""
        try:
            # Basic audio enhancement using ffmpeg
            volume = parameters.get('volume', 1.0)
            noise_reduction = parameters.get('noise_reduction', False)
            
            cmd = ['ffmpeg', '-i', input_file]
            
            if noise_reduction:
                cmd.extend(['-af', 'highpass=f=200,lowpass=f=3000'])
            
            if volume != 1.0:
                cmd.extend(['-af', f'volume={volume}'])
            
            cmd.extend(['-y', output_file])
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output_file': output_file,
                    'operation': 'enhance'
                }
            else:
                return {
                    'success': False,
                    'error': f'FFmpeg error: {result.stderr}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to enhance audio: {str(e)}'
            }
    
    async def _convert_audio(self, input_file: str, output_file: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Convert audio format"""
        try:
            format_type = parameters.get('format', 'mp3')
            bitrate = parameters.get('bitrate', '128k')
            
            # Change output file extension
            base_name = os.path.splitext(output_file)[0]
            output_file = f"{base_name}.{format_type}"
            
            cmd = [
                'ffmpeg', '-i', input_file,
                '-b:a', bitrate,
                '-y', output_file
            ]
            
            result = subprocess.run(cmd, capture_output=True, text=True)
            
            if result.returncode == 0:
                return {
                    'success': True,
                    'output_file': output_file,
                    'format': format_type,
                    'operation': 'convert'
                }
            else:
                return {
                    'success': False,
                    'error': f'FFmpeg error: {result.stderr}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to convert audio: {str(e)}'
            }
    
    async def process_image(self, image_data: bytes, operation: str, parameters: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process image data"""
        try:
            if parameters is None:
                parameters = {}
            
            image_id = str(uuid.uuid4())
            
            # Load image
            image = Image.open(io.BytesIO(image_data))
            
            if operation == 'resize':
                return await self._resize_image(image, image_id, parameters)
            elif operation == 'enhance':
                return await self._enhance_image(image, image_id, parameters)
            elif operation == 'analyze':
                return await self._analyze_image(image_data, parameters)
            elif operation == 'generate_variations':
                return await self._generate_image_variations(image_data, parameters)
            else:
                return {
                    'success': False,
                    'error': f'Unsupported image operation: {operation}'
                }
                
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to process image: {str(e)}'
            }
    
    async def _resize_image(self, image: Image.Image, image_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Resize image"""
        try:
            width = parameters.get('width', 800)
            height = parameters.get('height', 600)
            maintain_aspect = parameters.get('maintain_aspect', True)
            
            if maintain_aspect:
                image.thumbnail((width, height), Image.Resampling.LANCZOS)
            else:
                image = image.resize((width, height), Image.Resampling.LANCZOS)
            
            # Save processed image
            output_file = os.path.join(self.temp_dir, f"image_resized_{image_id}.png")
            image.save(output_file, 'PNG')
            
            return {
                'success': True,
                'output_file': output_file,
                'dimensions': image.size,
                'operation': 'resize'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to resize image: {str(e)}'
            }
    
    async def _enhance_image(self, image: Image.Image, image_id: str, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Enhance image quality"""
        try:
            from PIL import ImageEnhance
            
            brightness = parameters.get('brightness', 1.0)
            contrast = parameters.get('contrast', 1.0)
            saturation = parameters.get('saturation', 1.0)
            sharpness = parameters.get('sharpness', 1.0)
            
            # Apply enhancements
            if brightness != 1.0:
                enhancer = ImageEnhance.Brightness(image)
                image = enhancer.enhance(brightness)
            
            if contrast != 1.0:
                enhancer = ImageEnhance.Contrast(image)
                image = enhancer.enhance(contrast)
            
            if saturation != 1.0:
                enhancer = ImageEnhance.Color(image)
                image = enhancer.enhance(saturation)
            
            if sharpness != 1.0:
                enhancer = ImageEnhance.Sharpness(image)
                image = enhancer.enhance(sharpness)
            
            # Save enhanced image
            output_file = os.path.join(self.temp_dir, f"image_enhanced_{image_id}.png")
            image.save(output_file, 'PNG')
            
            return {
                'success': True,
                'output_file': output_file,
                'operation': 'enhance'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to enhance image: {str(e)}'
            }
    
    async def _analyze_image(self, image_data: bytes, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze image content using AI"""
        try:
            # Convert image to base64 for AI analysis
            image_b64 = base64.b64encode(image_data).decode('utf-8')
            image_url = f"data:image/png;base64,{image_b64}"
            
            prompt = parameters.get('prompt', 'Describe this image in detail')
            
            result = await ai_service.analyze_image(image_url, prompt)
            
            return {
                'success': True,
                'analysis': result.get('analysis', ''),
                'operation': 'analyze'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to analyze image: {str(e)}'
            }
    
    async def _generate_image_variations(self, image_data: bytes, parameters: Dict[str, Any]) -> Dict[str, Any]:
        """Generate variations of an image"""
        try:
            # This would typically use DALL-E 2 variations API
            # For now, return a placeholder
            return {
                'success': True,
                'message': 'Image variation generation coming soon',
                'operation': 'generate_variations'
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to generate variations: {str(e)}'
            }
    
    async def create_infographic(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Create an infographic from data"""
        try:
            title = data.get('title', 'Infographic')
            sections = data.get('sections', [])
            style = data.get('style', 'modern')
            
            infographic_id = str(uuid.uuid4())
            
            # Create infographic using PIL
            width, height = 800, 1200
            image = Image.new('RGB', (width, height), color='white')
            draw = ImageDraw.Draw(image)
            
            # Try to load a font, fallback to default if not available
            try:
                title_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 36)
                header_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", 24)
                body_font = ImageFont.truetype("/usr/share/fonts/truetype/dejavu/DejaVuSans.ttf", 18)
            except:
                title_font = ImageFont.load_default()
                header_font = ImageFont.load_default()
                body_font = ImageFont.load_default()
            
            # Color scheme based on style
            colors_scheme = {
                'modern': {'primary': '#2c3e50', 'secondary': '#3498db', 'accent': '#e74c3c'},
                'professional': {'primary': '#34495e', 'secondary': '#2980b9', 'accent': '#27ae60'},
                'vibrant': {'primary': '#8e44ad', 'secondary': '#f39c12', 'accent': '#e67e22'}
            }
            
            scheme = colors_scheme.get(style, colors_scheme['modern'])
            
            # Draw title
            y_offset = 50
            draw.text((width//2, y_offset), title, font=title_font, fill=scheme['primary'], anchor='mt')
            y_offset += 80
            
            # Draw sections
            for section in sections:
                section_title = section.get('title', '')
                section_content = section.get('content', '')
                
                # Section header
                draw.text((50, y_offset), section_title, font=header_font, fill=scheme['secondary'])
                y_offset += 40
                
                # Section content
                lines = section_content.split('\n')
                for line in lines:
                    if line.strip():
                        draw.text((70, y_offset), line.strip(), font=body_font, fill=scheme['primary'])
                        y_offset += 25
                
                y_offset += 30
            
            # Save infographic
            output_file = os.path.join(self.temp_dir, f"infographic_{infographic_id}.png")
            image.save(output_file, 'PNG')
            
            return {
                'success': True,
                'infographic_id': infographic_id,
                'output_file': output_file,
                'dimensions': (width, height)
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create infographic: {str(e)}'
            }
    
    def get_file_info(self, file_path: str) -> Dict[str, Any]:
        """Get information about a media file"""
        try:
            if not os.path.exists(file_path):
                return {'success': False, 'error': 'File not found'}
            
            file_size = os.path.getsize(file_path)
            file_ext = os.path.splitext(file_path)[1].lower().lstrip('.')
            
            info = {
                'success': True,
                'file_path': file_path,
                'file_size': file_size,
                'file_extension': file_ext,
                'created_at': datetime.fromtimestamp(os.path.getctime(file_path)).isoformat()
            }
            
            # Add format-specific information
            if file_ext in self.supported_formats['image']:
                try:
                    with Image.open(file_path) as img:
                        info.update({
                            'dimensions': img.size,
                            'mode': img.mode,
                            'format': img.format
                        })
                except:
                    pass
            
            return info
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get file info: {str(e)}'
            }
    
    def cleanup_temp_files(self, max_age_hours: int = 24) -> Dict[str, Any]:
        """Clean up old temporary files"""
        try:
            current_time = datetime.now()
            cleaned_files = 0
            
            for filename in os.listdir(self.temp_dir):
                if filename.startswith(('presentation_', 'document_', 'audio_', 'image_', 'infographic_')):
                    file_path = os.path.join(self.temp_dir, filename)
                    file_age = current_time - datetime.fromtimestamp(os.path.getctime(file_path))
                    
                    if file_age.total_seconds() > max_age_hours * 3600:
                        try:
                            os.remove(file_path)
                            cleaned_files += 1
                        except:
                            pass
            
            return {
                'success': True,
                'cleaned_files': cleaned_files
            }
            
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to cleanup files: {str(e)}'
            }

# Global media service instance
media_service = MediaService()


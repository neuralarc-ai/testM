import os
import openai
import anthropic
import requests
import json
from typing import Dict, List, Any, Optional
from datetime import datetime

class AIService:
    def __init__(self):
        # Initialize API clients
        self.openai_client = openai.OpenAI(
            api_key=os.getenv('OPENAI_API_KEY'),
            base_url=os.getenv('OPENAI_API_BASE', 'https://api.openai.com/v1')
        )
        
        self.anthropic_client = anthropic.Anthropic(
            api_key=os.getenv('ANTHROPIC_API_KEY')
        )
        
        # API configurations
        self.replicate_token = os.getenv('REPLICATE_API_TOKEN')
        self.stability_key = os.getenv('STABILITY_API_KEY')
        self.elevenlabs_key = os.getenv('ELEVENLABS_API_KEY')
        self.google_api_key = os.getenv('GOOGLE_API_KEY')
        self.perplexity_key = os.getenv('PERPLEXITY_API_KEY')
        
    async def generate_text(self, prompt: str, model: str = "gpt-4", max_tokens: int = 1000) -> Dict[str, Any]:
        """Generate text using OpenAI or Anthropic models"""
        try:
            if model.startswith('gpt'):
                response = self.openai_client.chat.completions.create(
                    model=model,
                    messages=[{"role": "user", "content": prompt}],
                    max_tokens=max_tokens,
                    temperature=0.7
                )
                return {
                    'success': True,
                    'content': response.choices[0].message.content,
                    'usage': response.usage.dict() if response.usage else None
                }
            elif model.startswith('claude'):
                response = self.anthropic_client.messages.create(
                    model=model,
                    max_tokens=max_tokens,
                    messages=[{"role": "user", "content": prompt}]
                )
                return {
                    'success': True,
                    'content': response.content[0].text,
                    'usage': response.usage.dict() if hasattr(response, 'usage') else None
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_image(self, prompt: str, model: str = "dall-e-3", size: str = "1024x1024") -> Dict[str, Any]:
        """Generate images using DALL-E or Stability AI"""
        try:
            if model.startswith('dall-e'):
                response = self.openai_client.images.generate(
                    model=model,
                    prompt=prompt,
                    size=size,
                    quality="standard",
                    n=1
                )
                return {
                    'success': True,
                    'image_url': response.data[0].url,
                    'revised_prompt': response.data[0].revised_prompt
                }
            elif model == 'stable-diffusion':
                return await self._generate_stability_image(prompt, size)
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_stability_image(self, prompt: str, size: str) -> Dict[str, Any]:
        """Generate image using Stability AI"""
        try:
            width, height = map(int, size.split('x'))
            
            response = requests.post(
                "https://api.stability.ai/v1/generation/stable-diffusion-xl-1024-v1-0/text-to-image",
                headers={
                    "Authorization": f"Bearer {self.stability_key}",
                    "Content-Type": "application/json",
                },
                json={
                    "text_prompts": [{"text": prompt}],
                    "cfg_scale": 7,
                    "height": height,
                    "width": width,
                    "samples": 1,
                    "steps": 30,
                }
            )
            
            if response.status_code == 200:
                data = response.json()
                return {
                    'success': True,
                    'image_data': data['artifacts'][0]['base64'],
                    'seed': data['artifacts'][0]['seed']
                }
            else:
                return {
                    'success': False,
                    'error': f"Stability AI error: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_speech(self, text: str, voice: str = "alloy") -> Dict[str, Any]:
        """Generate speech using OpenAI TTS or ElevenLabs"""
        try:
            if self.elevenlabs_key:
                return await self._generate_elevenlabs_speech(text, voice)
            else:
                response = self.openai_client.audio.speech.create(
                    model="tts-1",
                    voice=voice,
                    input=text
                )
                return {
                    'success': True,
                    'audio_data': response.content
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _generate_elevenlabs_speech(self, text: str, voice_id: str) -> Dict[str, Any]:
        """Generate speech using ElevenLabs"""
        try:
            url = f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}"
            headers = {
                "Accept": "audio/mpeg",
                "Content-Type": "application/json",
                "xi-api-key": self.elevenlabs_key
            }
            data = {
                "text": text,
                "model_id": "eleven_monolingual_v1",
                "voice_settings": {
                    "stability": 0.5,
                    "similarity_boost": 0.5
                }
            }
            
            response = requests.post(url, json=data, headers=headers)
            
            if response.status_code == 200:
                return {
                    'success': True,
                    'audio_data': response.content
                }
            else:
                return {
                    'success': False,
                    'error': f"ElevenLabs error: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_image(self, image_url: str, prompt: str = "Describe this image") -> Dict[str, Any]:
        """Analyze images using GPT-4 Vision"""
        try:
            response = self.openai_client.chat.completions.create(
                model="gpt-4-vision-preview",
                messages=[
                    {
                        "role": "user",
                        "content": [
                            {"type": "text", "text": prompt},
                            {"type": "image_url", "image_url": {"url": image_url}}
                        ]
                    }
                ],
                max_tokens=1000
            )
            return {
                'success': True,
                'analysis': response.choices[0].message.content
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def search_web(self, query: str, num_results: int = 5) -> Dict[str, Any]:
        """Search the web using Perplexity or Google"""
        try:
            if self.perplexity_key:
                return await self._search_perplexity(query)
            elif self.google_api_key:
                return await self._search_google(query, num_results)
            else:
                return {
                    'success': False,
                    'error': 'No search API configured'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _search_perplexity(self, query: str) -> Dict[str, Any]:
        """Search using Perplexity API"""
        try:
            headers = {
                "Authorization": f"Bearer {self.perplexity_key}",
                "Content-Type": "application/json"
            }
            data = {
                "model": "llama-3.1-sonar-small-128k-online",
                "messages": [
                    {"role": "system", "content": "You are a helpful search assistant."},
                    {"role": "user", "content": query}
                ]
            }
            
            response = requests.post(
                "https://api.perplexity.ai/chat/completions",
                headers=headers,
                json=data
            )
            
            if response.status_code == 200:
                result = response.json()
                return {
                    'success': True,
                    'results': result['choices'][0]['message']['content']
                }
            else:
                return {
                    'success': False,
                    'error': f"Perplexity error: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _search_google(self, query: str, num_results: int) -> Dict[str, Any]:
        """Search using Google Custom Search API"""
        try:
            search_engine_id = os.getenv('GOOGLE_SEARCH_ENGINE_ID')
            url = "https://www.googleapis.com/customsearch/v1"
            params = {
                'key': self.google_api_key,
                'cx': search_engine_id,
                'q': query,
                'num': num_results
            }
            
            response = requests.get(url, params=params)
            
            if response.status_code == 200:
                data = response.json()
                results = []
                for item in data.get('items', []):
                    results.append({
                        'title': item.get('title'),
                        'link': item.get('link'),
                        'snippet': item.get('snippet')
                    })
                return {
                    'success': True,
                    'results': results
                }
            else:
                return {
                    'success': False,
                    'error': f"Google Search error: {response.status_code}"
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def generate_code(self, prompt: str, language: str = "python") -> Dict[str, Any]:
        """Generate code using AI models"""
        try:
            system_prompt = f"""You are an expert {language} programmer. Generate clean, efficient, and well-documented code based on the user's requirements. Include comments and follow best practices."""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[
                    {"role": "system", "content": system_prompt},
                    {"role": "user", "content": prompt}
                ],
                max_tokens=2000,
                temperature=0.3
            )
            
            return {
                'success': True,
                'code': response.choices[0].message.content,
                'language': language
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def analyze_data(self, data: str, analysis_type: str = "general") -> Dict[str, Any]:
        """Analyze data using AI models"""
        try:
            prompt = f"""Analyze the following data and provide insights:

Data:
{data}

Analysis Type: {analysis_type}

Please provide:
1. Key findings
2. Patterns and trends
3. Recommendations
4. Summary statistics if applicable
"""
            
            response = self.openai_client.chat.completions.create(
                model="gpt-4",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=1500,
                temperature=0.5
            )
            
            return {
                'success': True,
                'analysis': response.choices[0].message.content
            }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }

# Global AI service instance
ai_service = AIService()


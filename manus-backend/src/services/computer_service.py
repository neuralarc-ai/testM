import asyncio
import json
import base64
import tempfile
import os
from typing import Dict, List, Any, Optional
from datetime import datetime
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.options import Options
from selenium.common.exceptions import TimeoutException, NoSuchElementException
import requests
from PIL import Image
import io

from .ai_service import ai_service

class ComputerService:
    def __init__(self):
        self.active_sessions = {}
        self.chrome_options = self._setup_chrome_options()
    
    def _setup_chrome_options(self):
        """Setup Chrome options for headless browsing"""
        options = Options()
        options.add_argument('--headless')
        options.add_argument('--no-sandbox')
        options.add_argument('--disable-dev-shm-usage')
        options.add_argument('--disable-gpu')
        options.add_argument('--window-size=1920,1080')
        options.add_argument('--user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36')
        return options
    
    async def create_browser_session(self, session_id: str) -> Dict[str, Any]:
        """Create a new browser session"""
        try:
            driver = webdriver.Chrome(options=self.chrome_options)
            self.active_sessions[session_id] = {
                'driver': driver,
                'created_at': datetime.utcnow(),
                'last_activity': datetime.utcnow()
            }
            
            return {
                'success': True,
                'session_id': session_id,
                'message': 'Browser session created successfully'
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to create browser session: {str(e)}'
            }
    
    async def navigate_to_url(self, session_id: str, url: str) -> Dict[str, Any]:
        """Navigate to a specific URL"""
        try:
            if session_id not in self.active_sessions:
                await self.create_browser_session(session_id)
            
            driver = self.active_sessions[session_id]['driver']
            driver.get(url)
            
            # Wait for page to load
            WebDriverWait(driver, 10).until(
                lambda d: d.execute_script("return document.readyState") == "complete"
            )
            
            # Take screenshot
            screenshot = await self._take_screenshot(driver)
            
            # Get page info
            page_info = {
                'title': driver.title,
                'url': driver.current_url,
                'screenshot': screenshot
            }
            
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
            
            return {
                'success': True,
                'page_info': page_info
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to navigate: {str(e)}'
            }
    
    async def click_element(self, session_id: str, selector: str, selector_type: str = 'css') -> Dict[str, Any]:
        """Click an element on the page"""
        try:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'No active browser session'}
            
            driver = self.active_sessions[session_id]['driver']
            
            # Find element
            if selector_type == 'css':
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.CSS_SELECTOR, selector))
                )
            elif selector_type == 'xpath':
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.XPATH, selector))
                )
            elif selector_type == 'id':
                element = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable((By.ID, selector))
                )
            else:
                return {'success': False, 'error': 'Invalid selector type'}
            
            # Click element
            element.click()
            
            # Wait a moment for any page changes
            await asyncio.sleep(1)
            
            # Take screenshot after click
            screenshot = await self._take_screenshot(driver)
            
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
            
            return {
                'success': True,
                'message': 'Element clicked successfully',
                'screenshot': screenshot
            }
        except TimeoutException:
            return {'success': False, 'error': 'Element not found or not clickable'}
        except Exception as e:
            return {'success': False, 'error': f'Failed to click element: {str(e)}'}
    
    async def type_text(self, session_id: str, selector: str, text: str, selector_type: str = 'css') -> Dict[str, Any]:
        """Type text into an input field"""
        try:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'No active browser session'}
            
            driver = self.active_sessions[session_id]['driver']
            
            # Find element
            if selector_type == 'css':
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            elif selector_type == 'xpath':
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            elif selector_type == 'id':
                element = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, selector))
                )
            else:
                return {'success': False, 'error': 'Invalid selector type'}
            
            # Clear existing text and type new text
            element.clear()
            element.send_keys(text)
            
            # Take screenshot after typing
            screenshot = await self._take_screenshot(driver)
            
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
            
            return {
                'success': True,
                'message': 'Text typed successfully',
                'screenshot': screenshot
            }
        except TimeoutException:
            return {'success': False, 'error': 'Input field not found'}
        except Exception as e:
            return {'success': False, 'error': f'Failed to type text: {str(e)}'}
    
    async def scroll_page(self, session_id: str, direction: str = 'down', amount: int = 3) -> Dict[str, Any]:
        """Scroll the page"""
        try:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'No active browser session'}
            
            driver = self.active_sessions[session_id]['driver']
            
            # Calculate scroll amount
            if direction == 'down':
                scroll_script = f"window.scrollBy(0, {amount * 300});"
            elif direction == 'up':
                scroll_script = f"window.scrollBy(0, -{amount * 300});"
            elif direction == 'top':
                scroll_script = "window.scrollTo(0, 0);"
            elif direction == 'bottom':
                scroll_script = "window.scrollTo(0, document.body.scrollHeight);"
            else:
                return {'success': False, 'error': 'Invalid scroll direction'}
            
            driver.execute_script(scroll_script)
            
            # Wait for scroll to complete
            await asyncio.sleep(1)
            
            # Take screenshot after scroll
            screenshot = await self._take_screenshot(driver)
            
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
            
            return {
                'success': True,
                'message': f'Scrolled {direction} successfully',
                'screenshot': screenshot
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to scroll: {str(e)}'}
    
    async def extract_page_content(self, session_id: str) -> Dict[str, Any]:
        """Extract text content from the current page"""
        try:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'No active browser session'}
            
            driver = self.active_sessions[session_id]['driver']
            
            # Extract various content types
            page_content = {
                'title': driver.title,
                'url': driver.current_url,
                'text_content': driver.find_element(By.TAG_NAME, 'body').text,
                'html_content': driver.page_source,
                'links': [
                    {'text': link.text, 'href': link.get_attribute('href')}
                    for link in driver.find_elements(By.TAG_NAME, 'a')
                    if link.get_attribute('href')
                ],
                'images': [
                    {'alt': img.get_attribute('alt'), 'src': img.get_attribute('src')}
                    for img in driver.find_elements(By.TAG_NAME, 'img')
                    if img.get_attribute('src')
                ],
                'forms': [
                    {
                        'action': form.get_attribute('action'),
                        'method': form.get_attribute('method'),
                        'inputs': [
                            {
                                'type': inp.get_attribute('type'),
                                'name': inp.get_attribute('name'),
                                'placeholder': inp.get_attribute('placeholder')
                            }
                            for inp in form.find_elements(By.TAG_NAME, 'input')
                        ]
                    }
                    for form in driver.find_elements(By.TAG_NAME, 'form')
                ]
            }
            
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
            
            return {
                'success': True,
                'content': page_content
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to extract content: {str(e)}'}
    
    async def execute_javascript(self, session_id: str, script: str) -> Dict[str, Any]:
        """Execute JavaScript on the current page"""
        try:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'No active browser session'}
            
            driver = self.active_sessions[session_id]['driver']
            
            # Execute the script
            result = driver.execute_script(script)
            
            # Take screenshot after execution
            screenshot = await self._take_screenshot(driver)
            
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
            
            return {
                'success': True,
                'result': result,
                'screenshot': screenshot
            }
        except Exception as e:
            return {'success': False, 'error': f'Failed to execute JavaScript: {str(e)}'}
    
    async def wait_for_element(self, session_id: str, selector: str, timeout: int = 10, selector_type: str = 'css') -> Dict[str, Any]:
        """Wait for an element to appear on the page"""
        try:
            if session_id not in self.active_sessions:
                return {'success': False, 'error': 'No active browser session'}
            
            driver = self.active_sessions[session_id]['driver']
            
            # Wait for element
            if selector_type == 'css':
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.CSS_SELECTOR, selector))
                )
            elif selector_type == 'xpath':
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.XPATH, selector))
                )
            elif selector_type == 'id':
                element = WebDriverWait(driver, timeout).until(
                    EC.presence_of_element_located((By.ID, selector))
                )
            else:
                return {'success': False, 'error': 'Invalid selector type'}
            
            # Take screenshot when element appears
            screenshot = await self._take_screenshot(driver)
            
            self.active_sessions[session_id]['last_activity'] = datetime.utcnow()
            
            return {
                'success': True,
                'message': 'Element found',
                'element_text': element.text,
                'screenshot': screenshot
            }
        except TimeoutException:
            return {'success': False, 'error': f'Element not found within {timeout} seconds'}
        except Exception as e:
            return {'success': False, 'error': f'Failed to wait for element: {str(e)}'}
    
    async def automate_task_with_ai(self, session_id: str, task_description: str, url: str = None) -> Dict[str, Any]:
        """Use AI to automate a web task"""
        try:
            # Navigate to URL if provided
            if url:
                nav_result = await self.navigate_to_url(session_id, url)
                if not nav_result['success']:
                    return nav_result
            
            # Get current page content
            content_result = await self.extract_page_content(session_id)
            if not content_result['success']:
                return content_result
            
            page_content = content_result['content']
            
            # Use AI to analyze the page and determine actions
            ai_prompt = f"""
            You are an AI assistant that can automate web tasks. 
            
            Task: {task_description}
            
            Current page information:
            - Title: {page_content['title']}
            - URL: {page_content['url']}
            - Available forms: {json.dumps(page_content['forms'], indent=2)}
            - Available links: {json.dumps(page_content['links'][:10], indent=2)}  # First 10 links
            
            Page text content (first 1000 chars):
            {page_content['text_content'][:1000]}
            
            Please provide a step-by-step plan to complete this task. For each step, specify:
            1. Action type (click, type, scroll, wait, navigate)
            2. Target element (CSS selector, XPath, or URL)
            3. Text to type (if applicable)
            4. Explanation of why this step is needed
            
            Format your response as JSON with this structure:
            {{
                "steps": [
                    {{
                        "action": "click|type|scroll|wait|navigate",
                        "target": "selector or URL",
                        "text": "text to type (optional)",
                        "explanation": "why this step is needed"
                    }}
                ],
                "success_criteria": "how to know the task is complete"
            }}
            """
            
            ai_result = await ai_service.generate_text(ai_prompt, model="gpt-4", max_tokens=1500)
            
            if not ai_result['success']:
                return {'success': False, 'error': 'AI analysis failed'}
            
            try:
                ai_response = json.loads(ai_result['content'])
            except json.JSONDecodeError:
                return {'success': False, 'error': 'AI response was not valid JSON'}
            
            # Execute the AI-generated steps
            execution_results = []
            
            for i, step in enumerate(ai_response.get('steps', [])):
                action = step.get('action')
                target = step.get('target')
                text = step.get('text')
                explanation = step.get('explanation')
                
                step_result = {'step': i + 1, 'action': action, 'explanation': explanation}
                
                try:
                    if action == 'click':
                        result = await self.click_element(session_id, target)
                    elif action == 'type':
                        result = await self.type_text(session_id, target, text)
                    elif action == 'scroll':
                        result = await self.scroll_page(session_id, target)
                    elif action == 'wait':
                        result = await self.wait_for_element(session_id, target)
                    elif action == 'navigate':
                        result = await self.navigate_to_url(session_id, target)
                    else:
                        result = {'success': False, 'error': f'Unknown action: {action}'}
                    
                    step_result.update(result)
                    execution_results.append(step_result)
                    
                    # If step failed, stop execution
                    if not result['success']:
                        break
                        
                    # Wait between steps
                    await asyncio.sleep(2)
                    
                except Exception as e:
                    step_result.update({'success': False, 'error': str(e)})
                    execution_results.append(step_result)
                    break
            
            # Get final page state
            final_content = await self.extract_page_content(session_id)
            
            return {
                'success': True,
                'task_description': task_description,
                'ai_plan': ai_response,
                'execution_results': execution_results,
                'final_page_content': final_content.get('content') if final_content['success'] else None
            }
            
        except Exception as e:
            return {'success': False, 'error': f'Task automation failed: {str(e)}'}
    
    async def _take_screenshot(self, driver) -> str:
        """Take a screenshot and return as base64 string"""
        try:
            screenshot_png = driver.get_screenshot_as_png()
            screenshot_b64 = base64.b64encode(screenshot_png).decode('utf-8')
            return screenshot_b64
        except Exception:
            return None
    
    async def close_session(self, session_id: str) -> Dict[str, Any]:
        """Close a browser session"""
        try:
            if session_id in self.active_sessions:
                driver = self.active_sessions[session_id]['driver']
                driver.quit()
                del self.active_sessions[session_id]
                
                return {
                    'success': True,
                    'message': 'Browser session closed successfully'
                }
            else:
                return {
                    'success': False,
                    'error': 'Session not found'
                }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to close session: {str(e)}'
            }
    
    async def get_active_sessions(self) -> Dict[str, Any]:
        """Get list of active browser sessions"""
        try:
            sessions = []
            for session_id, session_data in self.active_sessions.items():
                sessions.append({
                    'session_id': session_id,
                    'created_at': session_data['created_at'].isoformat(),
                    'last_activity': session_data['last_activity'].isoformat(),
                    'current_url': session_data['driver'].current_url if session_data['driver'] else None
                })
            
            return {
                'success': True,
                'sessions': sessions
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to get sessions: {str(e)}'
            }
    
    async def cleanup_old_sessions(self, max_age_hours: int = 2):
        """Clean up old browser sessions"""
        try:
            current_time = datetime.utcnow()
            sessions_to_remove = []
            
            for session_id, session_data in self.active_sessions.items():
                age = current_time - session_data['last_activity']
                if age.total_seconds() > max_age_hours * 3600:
                    sessions_to_remove.append(session_id)
            
            for session_id in sessions_to_remove:
                await self.close_session(session_id)
            
            return {
                'success': True,
                'cleaned_sessions': len(sessions_to_remove)
            }
        except Exception as e:
            return {
                'success': False,
                'error': f'Failed to cleanup sessions: {str(e)}'
            }

# Global computer service instance
computer_service = ComputerService()


import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional
from datetime import datetime
from enum import Enum

from .ai_service import ai_service
from ..models.user import Task

class AgentType(Enum):
    EXECUTOR = "executor"
    PLANNING = "planning"
    KNOWLEDGE = "knowledge"
    CONTENT = "content"
    IMAGE = "image"
    VIDEO = "video"
    CODE = "code"
    DATA = "data"
    WEB = "web"
    RESEARCH = "research"
    COMMUNICATION = "communication"

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"

class Agent:
    def __init__(self, agent_type: AgentType, name: str, description: str, capabilities: List[str]):
        self.agent_type = agent_type
        self.name = name
        self.description = description
        self.capabilities = capabilities
        self.status = "active"
        self.success_rate = 95  # Default success rate
        
    async def execute_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task based on agent type"""
        try:
            if self.agent_type == AgentType.EXECUTOR:
                return await self._execute_general_task(task_data)
            elif self.agent_type == AgentType.PLANNING:
                return await self._plan_task(task_data)
            elif self.agent_type == AgentType.KNOWLEDGE:
                return await self._knowledge_task(task_data)
            elif self.agent_type == AgentType.CONTENT:
                return await self._content_task(task_data)
            elif self.agent_type == AgentType.IMAGE:
                return await self._image_task(task_data)
            elif self.agent_type == AgentType.VIDEO:
                return await self._video_task(task_data)
            elif self.agent_type == AgentType.CODE:
                return await self._code_task(task_data)
            elif self.agent_type == AgentType.DATA:
                return await self._data_task(task_data)
            elif self.agent_type == AgentType.WEB:
                return await self._web_task(task_data)
            elif self.agent_type == AgentType.RESEARCH:
                return await self._research_task(task_data)
            elif self.agent_type == AgentType.COMMUNICATION:
                return await self._communication_task(task_data)
            else:
                return {
                    'success': False,
                    'error': f'Unknown agent type: {self.agent_type}'
                }
        except Exception as e:
            return {
                'success': False,
                'error': str(e)
            }
    
    async def _execute_general_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute general tasks"""
        prompt = f"""
        Task: {task_data.get('title', '')}
        Description: {task_data.get('description', '')}
        
        Please execute this task and provide a detailed response with the results.
        """
        
        result = await ai_service.generate_text(prompt, model="gpt-4", max_tokens=2000)
        
        if result['success']:
            return {
                'success': True,
                'result': result['content'],
                'output_type': 'text'
            }
        else:
            return result
    
    async def _plan_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Create task execution plans"""
        prompt = f"""
        You are a planning agent. Create a detailed execution plan for the following task:
        
        Task: {task_data.get('title', '')}
        Description: {task_data.get('description', '')}
        
        Provide:
        1. Step-by-step execution plan
        2. Required resources
        3. Estimated timeline
        4. Potential challenges
        5. Success criteria
        
        Format as JSON with clear structure.
        """
        
        result = await ai_service.generate_text(prompt, model="gpt-4", max_tokens=1500)
        
        if result['success']:
            return {
                'success': True,
                'plan': result['content'],
                'output_type': 'plan'
            }
        else:
            return result
    
    async def _knowledge_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle knowledge and research tasks"""
        query = task_data.get('description', '')
        
        # First search for information
        search_result = await ai_service.search_web(query)
        
        if search_result['success']:
            # Then analyze and synthesize the information
            analysis_prompt = f"""
            Based on the following search results, provide a comprehensive answer to: {query}
            
            Search Results:
            {search_result['results']}
            
            Please provide:
            1. A clear, comprehensive answer
            2. Key insights
            3. Sources and references
            4. Additional recommendations
            """
            
            analysis = await ai_service.generate_text(analysis_prompt, model="gpt-4", max_tokens=2000)
            
            if analysis['success']:
                return {
                    'success': True,
                    'knowledge': analysis['content'],
                    'sources': search_result['results'],
                    'output_type': 'knowledge'
                }
            else:
                return analysis
        else:
            return search_result
    
    async def _content_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle content creation tasks"""
        content_type = task_data.get('parameters', {}).get('content_type', 'article')
        topic = task_data.get('description', '')
        
        if content_type == 'article':
            prompt = f"""
            Write a comprehensive article about: {topic}
            
            Requirements:
            - Well-structured with clear headings
            - Engaging and informative content
            - Include introduction, main body, and conclusion
            - Use professional tone
            - Minimum 1000 words
            """
        elif content_type == 'blog_post':
            prompt = f"""
            Write an engaging blog post about: {topic}
            
            Requirements:
            - Catchy title and introduction
            - Personal and conversational tone
            - Include actionable insights
            - SEO-friendly structure
            - 800-1200 words
            """
        elif content_type == 'social_media':
            prompt = f"""
            Create social media content about: {topic}
            
            Provide:
            - 3 Twitter posts (280 chars each)
            - 1 LinkedIn post (professional tone)
            - 1 Instagram caption with hashtags
            - 1 Facebook post
            """
        else:
            prompt = f"Create content about: {topic}"
        
        result = await ai_service.generate_text(prompt, model="gpt-4", max_tokens=2500)
        
        if result['success']:
            return {
                'success': True,
                'content': result['content'],
                'content_type': content_type,
                'output_type': 'content'
            }
        else:
            return result
    
    async def _image_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle image generation tasks"""
        prompt = task_data.get('description', '')
        style = task_data.get('parameters', {}).get('style', 'realistic')
        size = task_data.get('parameters', {}).get('size', '1024x1024')
        
        # Enhance prompt based on style
        enhanced_prompt = f"{prompt}, {style} style, high quality, detailed"
        
        result = await ai_service.generate_image(enhanced_prompt, model="dall-e-3", size=size)
        
        if result['success']:
            return {
                'success': True,
                'image_url': result['image_url'],
                'prompt_used': result.get('revised_prompt', enhanced_prompt),
                'output_type': 'image'
            }
        else:
            return result
    
    async def _video_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle video generation tasks"""
        # For now, return a placeholder as video generation requires more complex setup
        return {
            'success': True,
            'message': 'Video generation capability coming soon',
            'output_type': 'video'
        }
    
    async def _code_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle code generation tasks"""
        description = task_data.get('description', '')
        language = task_data.get('parameters', {}).get('language', 'python')
        
        result = await ai_service.generate_code(description, language)
        
        if result['success']:
            return {
                'success': True,
                'code': result['code'],
                'language': result['language'],
                'output_type': 'code'
            }
        else:
            return result
    
    async def _data_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle data analysis tasks"""
        data = task_data.get('parameters', {}).get('data', '')
        analysis_type = task_data.get('parameters', {}).get('analysis_type', 'general')
        
        if not data:
            return {
                'success': False,
                'error': 'No data provided for analysis'
            }
        
        result = await ai_service.analyze_data(data, analysis_type)
        
        if result['success']:
            return {
                'success': True,
                'analysis': result['analysis'],
                'output_type': 'analysis'
            }
        else:
            return result
    
    async def _web_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle web development tasks"""
        description = task_data.get('description', '')
        
        prompt = f"""
        Create a complete web application based on: {description}
        
        Provide:
        1. HTML structure
        2. CSS styling (modern and responsive)
        3. JavaScript functionality
        4. Brief documentation
        
        Make it production-ready and follow best practices.
        """
        
        result = await ai_service.generate_text(prompt, model="gpt-4", max_tokens=3000)
        
        if result['success']:
            return {
                'success': True,
                'web_code': result['content'],
                'output_type': 'web_application'
            }
        else:
            return result
    
    async def _research_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle research tasks"""
        topic = task_data.get('description', '')
        depth = task_data.get('parameters', {}).get('depth', 'comprehensive')
        
        # Conduct web search
        search_result = await ai_service.search_web(topic, num_results=10)
        
        if search_result['success']:
            # Create comprehensive research report
            research_prompt = f"""
            Create a comprehensive research report on: {topic}
            
            Based on the following sources:
            {search_result['results']}
            
            Provide:
            1. Executive Summary
            2. Background and Context
            3. Key Findings
            4. Analysis and Insights
            5. Conclusions and Recommendations
            6. References
            
            Depth level: {depth}
            """
            
            result = await ai_service.generate_text(research_prompt, model="gpt-4", max_tokens=3000)
            
            if result['success']:
                return {
                    'success': True,
                    'research_report': result['content'],
                    'sources': search_result['results'],
                    'output_type': 'research'
                }
            else:
                return result
        else:
            return search_result
    
    async def _communication_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle communication tasks"""
        message_type = task_data.get('parameters', {}).get('type', 'email')
        content = task_data.get('description', '')
        tone = task_data.get('parameters', {}).get('tone', 'professional')
        
        if message_type == 'email':
            prompt = f"""
            Write a professional email with the following requirements:
            Content: {content}
            Tone: {tone}
            
            Include:
            - Appropriate subject line
            - Professional greeting
            - Clear and concise body
            - Professional closing
            """
        elif message_type == 'presentation':
            prompt = f"""
            Create a presentation outline for: {content}
            Tone: {tone}
            
            Include:
            - Title slide
            - Agenda
            - Main content slides (5-10 slides)
            - Conclusion
            - Q&A slide
            """
        else:
            prompt = f"Create {message_type} communication about: {content} with {tone} tone"
        
        result = await ai_service.generate_text(prompt, model="gpt-4", max_tokens=2000)
        
        if result['success']:
            return {
                'success': True,
                'communication': result['content'],
                'type': message_type,
                'output_type': 'communication'
            }
        else:
            return result

class AgentService:
    def __init__(self):
        self.agents = self._initialize_agents()
        self.active_tasks = {}
    
    def _initialize_agents(self) -> Dict[AgentType, Agent]:
        """Initialize all available agents"""
        agents = {
            AgentType.EXECUTOR: Agent(
                AgentType.EXECUTOR,
                "Task Executor",
                "General-purpose agent for executing various tasks",
                ["task_execution", "problem_solving", "general_assistance"]
            ),
            AgentType.PLANNING: Agent(
                AgentType.PLANNING,
                "Strategic Planner",
                "Creates detailed execution plans and strategies",
                ["strategic_planning", "project_management", "task_breakdown"]
            ),
            AgentType.KNOWLEDGE: Agent(
                AgentType.KNOWLEDGE,
                "Knowledge Researcher",
                "Searches and synthesizes information from various sources",
                ["web_search", "information_synthesis", "fact_checking"]
            ),
            AgentType.CONTENT: Agent(
                AgentType.CONTENT,
                "Content Creator",
                "Generates various types of written content",
                ["article_writing", "blog_posts", "social_media", "copywriting"]
            ),
            AgentType.IMAGE: Agent(
                AgentType.IMAGE,
                "Visual Designer",
                "Creates and generates images and visual content",
                ["image_generation", "visual_design", "graphic_creation"]
            ),
            AgentType.VIDEO: Agent(
                AgentType.VIDEO,
                "Video Producer",
                "Creates and edits video content",
                ["video_generation", "video_editing", "animation"]
            ),
            AgentType.CODE: Agent(
                AgentType.CODE,
                "Code Developer",
                "Generates and debugs code in multiple languages",
                ["code_generation", "debugging", "software_development"]
            ),
            AgentType.DATA: Agent(
                AgentType.DATA,
                "Data Analyst",
                "Analyzes data and creates insights",
                ["data_analysis", "visualization", "statistical_analysis"]
            ),
            AgentType.WEB: Agent(
                AgentType.WEB,
                "Web Developer",
                "Creates web applications and websites",
                ["web_development", "frontend", "backend", "full_stack"]
            ),
            AgentType.RESEARCH: Agent(
                AgentType.RESEARCH,
                "Research Specialist",
                "Conducts comprehensive research and analysis",
                ["academic_research", "market_research", "competitive_analysis"]
            ),
            AgentType.COMMUNICATION: Agent(
                AgentType.COMMUNICATION,
                "Communication Expert",
                "Creates professional communications and presentations",
                ["email_writing", "presentations", "business_communication"]
            )
        }
        return agents
    
    def get_agents(self) -> List[Dict[str, Any]]:
        """Get list of all available agents"""
        return [
            {
                'id': agent_type.value,
                'agent_type': agent_type.value,
                'name': agent.name,
                'description': agent.description,
                'capabilities': agent.capabilities,
                'status': agent.status,
                'success_rate': agent.success_rate
            }
            for agent_type, agent in self.agents.items()
        ]
    
    def get_agent_recommendations(self, task_type: str) -> List[Dict[str, Any]]:
        """Get recommended agents for a specific task type"""
        recommendations = []
        
        task_agent_mapping = {
            'image': [AgentType.IMAGE, AgentType.CONTENT],
            'video': [AgentType.VIDEO, AgentType.CONTENT],
            'slides': [AgentType.CONTENT, AgentType.COMMUNICATION],
            'webpage': [AgentType.WEB, AgentType.CODE],
            'analysis': [AgentType.DATA, AgentType.RESEARCH],
            'research': [AgentType.RESEARCH, AgentType.KNOWLEDGE],
            'code': [AgentType.CODE, AgentType.WEB],
            'audio': [AgentType.CONTENT, AgentType.COMMUNICATION],
            'document': [AgentType.CONTENT, AgentType.RESEARCH]
        }
        
        recommended_types = task_agent_mapping.get(task_type, [AgentType.EXECUTOR])
        
        for agent_type in recommended_types:
            if agent_type in self.agents:
                agent = self.agents[agent_type]
                recommendations.append({
                    'id': agent_type.value,
                    'name': agent.name,
                    'description': agent.description,
                    'confidence': 0.9 if agent_type == recommended_types[0] else 0.7
                })
        
        return recommendations
    
    async def execute_task(self, task_id: str, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a task using the appropriate agent"""
        try:
            # Determine the best agent for the task
            task_type = task_data.get('task_type', 'general')
            agent_type = self._get_agent_for_task_type(task_type)
            
            if agent_type not in self.agents:
                return {
                    'success': False,
                    'error': f'No agent available for task type: {task_type}'
                }
            
            # Mark task as running
            self.active_tasks[task_id] = {
                'status': TaskStatus.RUNNING,
                'agent_type': agent_type.value,
                'start_time': datetime.utcnow()
            }
            
            # Execute the task
            agent = self.agents[agent_type]
            result = await agent.execute_task(task_data)
            
            # Update task status
            if result['success']:
                self.active_tasks[task_id]['status'] = TaskStatus.COMPLETED
                self.active_tasks[task_id]['end_time'] = datetime.utcnow()
            else:
                self.active_tasks[task_id]['status'] = TaskStatus.FAILED
                self.active_tasks[task_id]['error'] = result.get('error', 'Unknown error')
            
            return result
            
        except Exception as e:
            self.active_tasks[task_id] = {
                'status': TaskStatus.FAILED,
                'error': str(e)
            }
            return {
                'success': False,
                'error': str(e)
            }
    
    def _get_agent_for_task_type(self, task_type: str) -> AgentType:
        """Get the best agent type for a given task type"""
        mapping = {
            'image': AgentType.IMAGE,
            'video': AgentType.VIDEO,
            'slides': AgentType.CONTENT,
            'webpage': AgentType.WEB,
            'analysis': AgentType.DATA,
            'research': AgentType.RESEARCH,
            'code': AgentType.CODE,
            'audio': AgentType.CONTENT,
            'document': AgentType.CONTENT
        }
        
        return mapping.get(task_type, AgentType.EXECUTOR)
    
    def get_task_status(self, task_id: str) -> Dict[str, Any]:
        """Get the status of a running task"""
        return self.active_tasks.get(task_id, {'status': TaskStatus.PENDING})
    
    def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        if task_id in self.active_tasks:
            self.active_tasks[task_id]['status'] = TaskStatus.CANCELLED
            return True
        return False

# Global agent service instance
agent_service = AgentService()


import asyncio
import json
import uuid
from typing import Dict, List, Any, Optional, Callable
from datetime import datetime, timedelta
from enum import Enum
import threading
import time
from dataclasses import dataclass, asdict
from collections import defaultdict
import logging

from .ai_service import ai_service
from .agent_service import agent_service
from .computer_service import computer_service
from .media_service import media_service

logger = logging.getLogger(__name__)

class TaskStatus(Enum):
    PENDING = "pending"
    RUNNING = "running"
    COMPLETED = "completed"
    FAILED = "failed"
    CANCELLED = "cancelled"
    PAUSED = "paused"

class TaskPriority(Enum):
    LOW = 1
    NORMAL = 2
    HIGH = 3
    URGENT = 4

@dataclass
class TaskStep:
    id: str
    name: str
    agent_id: str
    action: str
    parameters: Dict[str, Any]
    dependencies: List[str]
    status: TaskStatus = TaskStatus.PENDING
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    progress: float = 0.0

@dataclass
class Task:
    id: str
    user_id: str
    title: str
    description: str
    task_type: str
    priority: TaskPriority
    steps: List[TaskStep]
    status: TaskStatus = TaskStatus.PENDING
    progress: float = 0.0
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    created_at: datetime = None
    started_at: Optional[datetime] = None
    completed_at: Optional[datetime] = None
    estimated_duration: Optional[int] = None  # seconds
    actual_duration: Optional[int] = None
    metadata: Dict[str, Any] = None

    def __post_init__(self):
        if self.created_at is None:
            self.created_at = datetime.utcnow()
        if self.metadata is None:
            self.metadata = {}

class TaskOrchestrator:
    def __init__(self):
        self.tasks: Dict[str, Task] = {}
        self.task_queue: List[str] = []
        self.running_tasks: Dict[str, asyncio.Task] = {}
        self.task_subscribers: Dict[str, List[Callable]] = defaultdict(list)
        self.global_subscribers: List[Callable] = []
        self.max_concurrent_tasks = 5
        self.worker_thread = None
        self.is_running = False
        self.task_templates = self._load_task_templates()
    
    def _load_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """Load predefined task templates"""
        return {
            'content_creation': {
                'name': 'Content Creation',
                'description': 'Create various types of content',
                'steps': [
                    {
                        'name': 'Research Topic',
                        'agent_id': 'research',
                        'action': 'web_search',
                        'dependencies': []
                    },
                    {
                        'name': 'Generate Content',
                        'agent_id': 'content',
                        'action': 'generate_text',
                        'dependencies': ['research_topic']
                    },
                    {
                        'name': 'Review and Edit',
                        'agent_id': 'content',
                        'action': 'review_content',
                        'dependencies': ['generate_content']
                    }
                ]
            },
            'presentation_creation': {
                'name': 'Presentation Creation',
                'description': 'Create a complete presentation',
                'steps': [
                    {
                        'name': 'Research Topic',
                        'agent_id': 'research',
                        'action': 'web_search',
                        'dependencies': []
                    },
                    {
                        'name': 'Generate Outline',
                        'agent_id': 'planning',
                        'action': 'create_outline',
                        'dependencies': ['research_topic']
                    },
                    {
                        'name': 'Create Slides',
                        'agent_id': 'content',
                        'action': 'generate_slides',
                        'dependencies': ['generate_outline']
                    },
                    {
                        'name': 'Generate Images',
                        'agent_id': 'image',
                        'action': 'generate_images',
                        'dependencies': ['create_slides']
                    },
                    {
                        'name': 'Compile Presentation',
                        'agent_id': 'executor',
                        'action': 'create_presentation',
                        'dependencies': ['generate_images']
                    }
                ]
            },
            'web_automation': {
                'name': 'Web Automation',
                'description': 'Automate web-based tasks',
                'steps': [
                    {
                        'name': 'Analyze Task',
                        'agent_id': 'planning',
                        'action': 'analyze_automation_task',
                        'dependencies': []
                    },
                    {
                        'name': 'Create Browser Session',
                        'agent_id': 'executor',
                        'action': 'create_browser_session',
                        'dependencies': ['analyze_task']
                    },
                    {
                        'name': 'Execute Automation',
                        'agent_id': 'executor',
                        'action': 'execute_automation',
                        'dependencies': ['create_browser_session']
                    },
                    {
                        'name': 'Extract Results',
                        'agent_id': 'executor',
                        'action': 'extract_results',
                        'dependencies': ['execute_automation']
                    }
                ]
            },
            'data_analysis': {
                'name': 'Data Analysis',
                'description': 'Analyze data and create insights',
                'steps': [
                    {
                        'name': 'Load Data',
                        'agent_id': 'data',
                        'action': 'load_data',
                        'dependencies': []
                    },
                    {
                        'name': 'Clean Data',
                        'agent_id': 'data',
                        'action': 'clean_data',
                        'dependencies': ['load_data']
                    },
                    {
                        'name': 'Analyze Data',
                        'agent_id': 'data',
                        'action': 'analyze_data',
                        'dependencies': ['clean_data']
                    },
                    {
                        'name': 'Create Visualizations',
                        'agent_id': 'data',
                        'action': 'create_visualizations',
                        'dependencies': ['analyze_data']
                    },
                    {
                        'name': 'Generate Report',
                        'agent_id': 'content',
                        'action': 'generate_report',
                        'dependencies': ['create_visualizations']
                    }
                ]
            }
        }
    
    def start(self):
        """Start the task orchestrator"""
        if not self.is_running:
            self.is_running = True
            self.worker_thread = threading.Thread(target=self._worker_loop, daemon=True)
            self.worker_thread.start()
            logger.info("Task orchestrator started")
    
    def stop(self):
        """Stop the task orchestrator"""
        self.is_running = False
        if self.worker_thread:
            self.worker_thread.join(timeout=5)
        logger.info("Task orchestrator stopped")
    
    def _worker_loop(self):
        """Main worker loop for processing tasks"""
        while self.is_running:
            try:
                self._process_task_queue()
                time.sleep(1)  # Check every second
            except Exception as e:
                logger.error(f"Error in worker loop: {str(e)}")
    
    def _process_task_queue(self):
        """Process pending tasks in the queue"""
        # Remove completed tasks from running_tasks
        completed_task_ids = []
        for task_id, async_task in self.running_tasks.items():
            if async_task.done():
                completed_task_ids.append(task_id)
        
        for task_id in completed_task_ids:
            del self.running_tasks[task_id]
        
        # Start new tasks if we have capacity
        while (len(self.running_tasks) < self.max_concurrent_tasks and 
               self.task_queue):
            
            task_id = self.task_queue.pop(0)
            if task_id in self.tasks:
                task = self.tasks[task_id]
                if task.status == TaskStatus.PENDING:
                    # Start the task
                    loop = asyncio.new_event_loop()
                    asyncio.set_event_loop(loop)
                    async_task = loop.create_task(self._execute_task(task))
                    self.running_tasks[task_id] = async_task
                    
                    # Run the task in a separate thread
                    thread = threading.Thread(
                        target=lambda: loop.run_until_complete(async_task),
                        daemon=True
                    )
                    thread.start()
    
    async def create_task_from_template(self, user_id: str, template_name: str, 
                                      parameters: Dict[str, Any]) -> str:
        """Create a task from a predefined template"""
        if template_name not in self.task_templates:
            raise ValueError(f"Unknown task template: {template_name}")
        
        template = self.task_templates[template_name]
        task_id = str(uuid.uuid4())
        
        # Create task steps from template
        steps = []
        for i, step_template in enumerate(template['steps']):
            step_id = f"{task_id}_step_{i}"
            step = TaskStep(
                id=step_id,
                name=step_template['name'],
                agent_id=step_template['agent_id'],
                action=step_template['action'],
                parameters=parameters.copy(),
                dependencies=step_template['dependencies']
            )
            steps.append(step)
        
        # Create the task
        task = Task(
            id=task_id,
            user_id=user_id,
            title=template['name'],
            description=template['description'],
            task_type=template_name,
            priority=TaskPriority.NORMAL,
            steps=steps,
            metadata=parameters
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        
        # Notify subscribers
        await self._notify_task_update(task)
        
        return task_id
    
    async def create_custom_task(self, user_id: str, title: str, description: str,
                               task_type: str, steps: List[Dict[str, Any]],
                               priority: TaskPriority = TaskPriority.NORMAL) -> str:
        """Create a custom task with specified steps"""
        task_id = str(uuid.uuid4())
        
        # Create task steps
        task_steps = []
        for i, step_data in enumerate(steps):
            step_id = f"{task_id}_step_{i}"
            step = TaskStep(
                id=step_id,
                name=step_data['name'],
                agent_id=step_data['agent_id'],
                action=step_data['action'],
                parameters=step_data.get('parameters', {}),
                dependencies=step_data.get('dependencies', [])
            )
            task_steps.append(step)
        
        # Create the task
        task = Task(
            id=task_id,
            user_id=user_id,
            title=title,
            description=description,
            task_type=task_type,
            priority=priority,
            steps=task_steps
        )
        
        self.tasks[task_id] = task
        self.task_queue.append(task_id)
        
        # Notify subscribers
        await self._notify_task_update(task)
        
        return task_id
    
    async def _execute_task(self, task: Task):
        """Execute a task by running its steps"""
        try:
            task.status = TaskStatus.RUNNING
            task.started_at = datetime.utcnow()
            await self._notify_task_update(task)
            
            # Execute steps in dependency order
            completed_steps = set()
            
            while len(completed_steps) < len(task.steps):
                # Find steps that can be executed (dependencies met)
                ready_steps = []
                for step in task.steps:
                    if (step.status == TaskStatus.PENDING and
                        all(dep in completed_steps for dep in step.dependencies)):
                        ready_steps.append(step)
                
                if not ready_steps:
                    # Check if we're stuck (circular dependencies or missing steps)
                    pending_steps = [s for s in task.steps if s.status == TaskStatus.PENDING]
                    if pending_steps:
                        raise Exception("Circular dependencies or missing steps detected")
                    break
                
                # Execute ready steps (can be done in parallel)
                step_tasks = []
                for step in ready_steps:
                    step_tasks.append(self._execute_step(task, step))
                
                # Wait for all steps to complete
                step_results = await asyncio.gather(*step_tasks, return_exceptions=True)
                
                # Process results
                for step, result in zip(ready_steps, step_results):
                    if isinstance(result, Exception):
                        step.status = TaskStatus.FAILED
                        step.error = str(result)
                        task.status = TaskStatus.FAILED
                        task.error = f"Step '{step.name}' failed: {str(result)}"
                        await self._notify_task_update(task)
                        return
                    else:
                        step.status = TaskStatus.COMPLETED
                        step.result = result
                        completed_steps.add(step.id)
                
                # Update task progress
                task.progress = len(completed_steps) / len(task.steps)
                await self._notify_task_update(task)
            
            # Task completed successfully
            task.status = TaskStatus.COMPLETED
            task.completed_at = datetime.utcnow()
            task.progress = 1.0
            
            if task.started_at:
                task.actual_duration = int((task.completed_at - task.started_at).total_seconds())
            
            # Compile final result
            task.result = self._compile_task_result(task)
            
            await self._notify_task_update(task)
            
        except Exception as e:
            task.status = TaskStatus.FAILED
            task.error = str(e)
            task.completed_at = datetime.utcnow()
            await self._notify_task_update(task)
            logger.error(f"Task {task.id} failed: {str(e)}")
    
    async def _execute_step(self, task: Task, step: TaskStep) -> Dict[str, Any]:
        """Execute a single task step"""
        try:
            step.status = TaskStatus.RUNNING
            step.started_at = datetime.utcnow()
            await self._notify_task_update(task)
            
            # Get the agent for this step
            agents = agent_service.get_agents()
            agent = next((a for a in agents if a['id'] == step.agent_id), None)
            
            if not agent:
                raise Exception(f"Agent '{step.agent_id}' not found")
            
            # Execute the step action
            result = await self._execute_step_action(step.action, step.parameters, agent)
            
            step.status = TaskStatus.COMPLETED
            step.completed_at = datetime.utcnow()
            step.result = result
            step.progress = 1.0
            
            return result
            
        except Exception as e:
            step.status = TaskStatus.FAILED
            step.error = str(e)
            step.completed_at = datetime.utcnow()
            raise e
    
    async def _execute_step_action(self, action: str, parameters: Dict[str, Any], 
                                 agent: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a specific step action"""
        try:
            if action == 'web_search':
                query = parameters.get('query', parameters.get('topic', ''))
                result = await ai_service.web_search(query)
                return {'search_results': result}
            
            elif action == 'generate_text':
                prompt = parameters.get('prompt', '')
                model = parameters.get('model', 'gpt-4')
                result = await ai_service.generate_text(prompt, model=model)
                return {'generated_text': result.get('content', '')}
            
            elif action == 'generate_image':
                prompt = parameters.get('prompt', '')
                style = parameters.get('style', 'realistic')
                result = await ai_service.generate_image(prompt, style)
                return {'generated_image': result}
            
            elif action == 'create_presentation':
                title = parameters.get('title', 'Presentation')
                slides = parameters.get('slides', [])
                result = await media_service.generate_presentation({
                    'title': title,
                    'slides': slides,
                    'theme': parameters.get('theme', 'professional')
                })
                return {'presentation': result}
            
            elif action == 'create_document':
                title = parameters.get('title', 'Document')
                content = parameters.get('content', '')
                result = await media_service.generate_document({
                    'title': title,
                    'body': content,
                    'format': parameters.get('format', 'pdf')
                })
                return {'document': result}
            
            elif action == 'browser_automation':
                session_id = parameters.get('session_id')
                task_description = parameters.get('task_description', '')
                url = parameters.get('url')
                
                if not session_id:
                    # Create new session
                    session_result = await computer_service.create_browser_session(
                        f"task_{uuid.uuid4().hex[:8]}"
                    )
                    session_id = session_result.get('session_id')
                
                result = await computer_service.automate_task_with_ai(
                    session_id, task_description, url
                )
                return {'automation_result': result}
            
            elif action == 'analyze_data':
                data = parameters.get('data', [])
                analysis_type = parameters.get('analysis_type', 'summary')
                
                # Use AI to analyze the data
                prompt = f"""
                Analyze the following data and provide insights:
                
                Data: {json.dumps(data, indent=2)}
                Analysis Type: {analysis_type}
                
                Provide a comprehensive analysis including:
                1. Key findings
                2. Trends and patterns
                3. Recommendations
                4. Statistical summary
                """
                
                result = await ai_service.generate_text(prompt, model="gpt-4")
                return {'analysis': result.get('content', '')}
            
            else:
                # Generic action execution
                prompt = f"""
                Execute the following action for agent {agent['name']}:
                
                Action: {action}
                Parameters: {json.dumps(parameters, indent=2)}
                Agent Capabilities: {', '.join(agent.get('capabilities', []))}
                
                Provide a detailed response with the action results.
                """
                
                result = await ai_service.generate_text(prompt, model="gpt-4")
                return {'action_result': result.get('content', '')}
                
        except Exception as e:
            logger.error(f"Error executing action {action}: {str(e)}")
            raise e
    
    def _compile_task_result(self, task: Task) -> Dict[str, Any]:
        """Compile the final result from all completed steps"""
        result = {
            'task_id': task.id,
            'title': task.title,
            'status': task.status.value,
            'progress': task.progress,
            'steps_completed': len([s for s in task.steps if s.status == TaskStatus.COMPLETED]),
            'total_steps': len(task.steps),
            'duration': task.actual_duration,
            'step_results': []
        }
        
        for step in task.steps:
            step_result = {
                'step_id': step.id,
                'name': step.name,
                'status': step.status.value,
                'result': step.result,
                'error': step.error
            }
            result['step_results'].append(step_result)
        
        return result
    
    async def _notify_task_update(self, task: Task):
        """Notify subscribers about task updates"""
        task_data = asdict(task)
        
        # Convert datetime objects to ISO strings
        for key, value in task_data.items():
            if isinstance(value, datetime):
                task_data[key] = value.isoformat() if value else None
        
        # Convert steps
        if 'steps' in task_data:
            for step in task_data['steps']:
                for key, value in step.items():
                    if isinstance(value, datetime):
                        step[key] = value.isoformat() if value else None
                    elif isinstance(value, TaskStatus):
                        step[key] = value.value
        
        # Convert enums
        if isinstance(task_data.get('status'), TaskStatus):
            task_data['status'] = task_data['status'].value
        if isinstance(task_data.get('priority'), TaskPriority):
            task_data['priority'] = task_data['priority'].value
        
        # Notify task-specific subscribers
        for callback in self.task_subscribers.get(task.id, []):
            try:
                await callback(task_data)
            except Exception as e:
                logger.error(f"Error notifying task subscriber: {str(e)}")
        
        # Notify global subscribers
        for callback in self.global_subscribers:
            try:
                await callback(task_data)
            except Exception as e:
                logger.error(f"Error notifying global subscriber: {str(e)}")
    
    def subscribe_to_task(self, task_id: str, callback: Callable):
        """Subscribe to updates for a specific task"""
        self.task_subscribers[task_id].append(callback)
    
    def subscribe_to_all_tasks(self, callback: Callable):
        """Subscribe to updates for all tasks"""
        self.global_subscribers.append(callback)
    
    def unsubscribe_from_task(self, task_id: str, callback: Callable):
        """Unsubscribe from task updates"""
        if task_id in self.task_subscribers:
            try:
                self.task_subscribers[task_id].remove(callback)
            except ValueError:
                pass
    
    def unsubscribe_from_all_tasks(self, callback: Callable):
        """Unsubscribe from all task updates"""
        try:
            self.global_subscribers.remove(callback)
        except ValueError:
            pass
    
    def get_task(self, task_id: str) -> Optional[Task]:
        """Get a task by ID"""
        return self.tasks.get(task_id)
    
    def get_user_tasks(self, user_id: str) -> List[Task]:
        """Get all tasks for a user"""
        return [task for task in self.tasks.values() if task.user_id == user_id]
    
    def get_task_status(self, task_id: str) -> Optional[Dict[str, Any]]:
        """Get the current status of a task"""
        task = self.get_task(task_id)
        if not task:
            return None
        
        return {
            'id': task.id,
            'status': task.status.value,
            'progress': task.progress,
            'steps_completed': len([s for s in task.steps if s.status == TaskStatus.COMPLETED]),
            'total_steps': len(task.steps),
            'error': task.error,
            'estimated_duration': task.estimated_duration,
            'actual_duration': task.actual_duration
        }
    
    async def cancel_task(self, task_id: str) -> bool:
        """Cancel a running task"""
        task = self.get_task(task_id)
        if not task:
            return False
        
        if task.status in [TaskStatus.PENDING, TaskStatus.RUNNING]:
            task.status = TaskStatus.CANCELLED
            task.completed_at = datetime.utcnow()
            
            # Cancel the async task if it's running
            if task_id in self.running_tasks:
                self.running_tasks[task_id].cancel()
                del self.running_tasks[task_id]
            
            # Remove from queue if pending
            if task_id in self.task_queue:
                self.task_queue.remove(task_id)
            
            await self._notify_task_update(task)
            return True
        
        return False
    
    async def pause_task(self, task_id: str) -> bool:
        """Pause a running task"""
        task = self.get_task(task_id)
        if not task or task.status != TaskStatus.RUNNING:
            return False
        
        task.status = TaskStatus.PAUSED
        await self._notify_task_update(task)
        return True
    
    async def resume_task(self, task_id: str) -> bool:
        """Resume a paused task"""
        task = self.get_task(task_id)
        if not task or task.status != TaskStatus.PAUSED:
            return False
        
        task.status = TaskStatus.RUNNING
        await self._notify_task_update(task)
        return True
    
    def get_queue_status(self) -> Dict[str, Any]:
        """Get the current status of the task queue"""
        return {
            'pending_tasks': len(self.task_queue),
            'running_tasks': len(self.running_tasks),
            'max_concurrent': self.max_concurrent_tasks,
            'is_running': self.is_running
        }
    
    def get_task_templates(self) -> Dict[str, Dict[str, Any]]:
        """Get available task templates"""
        return self.task_templates.copy()

# Global orchestrator instance
orchestrator = TaskOrchestrator()


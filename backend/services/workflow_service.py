
"""
Workflow Service for Enhanced CPAS
Handles workflow creation, execution, and management
"""

import asyncio
import json
from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
from loguru import logger
from motor.motor_asyncio import AsyncIOMotorDatabase

from models.workflow import (
    Workflow, WorkflowExecution, WorkflowTemplate, AgentCollaboration,
    TaskDelegation, WorkflowStatus, TaskStatus, TriggerType, ActionType
)
from services.agent_service import AgentService
from services.integration_service import IntegrationService

class WorkflowService:
    """Service for managing workflows and automation"""
    
    def __init__(self, db: AsyncIOMotorDatabase):
        self.db = db
        self.workflows = db.workflows
        self.executions = db.workflow_executions
        self.templates = db.workflow_templates
        self.collaborations = db.agent_collaborations
        self.delegations = db.task_delegations
        self.agent_service = AgentService(db)
        self.integration_service = IntegrationService(db)
        self.running_executions: Dict[str, asyncio.Task] = {}
    
    async def create_workflow(self, workflow_data: Dict[str, Any]) -> Workflow:
        """Create a new workflow"""
        workflow = Workflow(**workflow_data)
        
        # Validate workflow structure
        await self._validate_workflow(workflow)
        
        # Insert into database
        result = await self.workflows.insert_one(workflow.dict())
        workflow.id = str(result.inserted_id)
        
        logger.info(f"Created workflow: {workflow.name} ({workflow.id})")
        return workflow
    
    async def get_workflow(self, workflow_id: str) -> Optional[Workflow]:
        """Get workflow by ID"""
        doc = await self.workflows.find_one({"_id": workflow_id})
        return Workflow(**doc) if doc else None
    
    async def list_workflows(self, 
                           status: Optional[WorkflowStatus] = None,
                           tags: Optional[List[str]] = None,
                           page: int = 1,
                           page_size: int = 20) -> Dict[str, Any]:
        """List workflows with filtering"""
        query = {}
        if status:
            query["status"] = status
        if tags:
            query["tags"] = {"$in": tags}
        
        skip = (page - 1) * page_size
        cursor = self.workflows.find(query).skip(skip).limit(page_size)
        workflows = [Workflow(**doc) async for doc in cursor]
        total = await self.workflows.count_documents(query)
        
        return {
            "workflows": workflows,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    async def update_workflow(self, workflow_id: str, updates: Dict[str, Any]) -> Optional[Workflow]:
        """Update workflow"""
        updates["updated_at"] = datetime.utcnow()
        
        result = await self.workflows.update_one(
            {"_id": workflow_id},
            {"$set": updates}
        )
        
        if result.modified_count > 0:
            return await self.get_workflow(workflow_id)
        return None
    
    async def delete_workflow(self, workflow_id: str) -> bool:
        """Delete workflow"""
        # Cancel any running executions
        await self._cancel_workflow_executions(workflow_id)
        
        result = await self.workflows.delete_one({"_id": workflow_id})
        return result.deleted_count > 0
    
    async def execute_workflow(self, workflow_id: str, trigger_data: Dict[str, Any] = None) -> WorkflowExecution:
        """Execute a workflow"""
        workflow = await self.get_workflow(workflow_id)
        if not workflow:
            raise ValueError(f"Workflow {workflow_id} not found")
        
        if workflow.status != WorkflowStatus.ACTIVE:
            raise ValueError(f"Workflow {workflow_id} is not active")
        
        # Create execution record
        execution = WorkflowExecution(
            workflow_id=workflow_id,
            trigger_data=trigger_data or {},
            started_at=datetime.utcnow()
        )
        
        result = await self.executions.insert_one(execution.dict())
        execution.id = str(result.inserted_id)
        
        # Start execution in background
        task = asyncio.create_task(self._execute_workflow_async(workflow, execution))
        self.running_executions[execution.id] = task
        
        logger.info(f"Started workflow execution: {execution.id}")
        return execution
    
    async def _execute_workflow_async(self, workflow: Workflow, execution: WorkflowExecution):
        """Execute workflow asynchronously"""
        try:
            execution.status = TaskStatus.RUNNING
            await self._update_execution(execution)
            
            # Build dependency graph
            action_graph = self._build_action_graph(workflow.actions)
            
            # Execute actions in dependency order
            completed_actions = set()
            action_results = {}
            
            while len(completed_actions) < len(workflow.actions):
                # Find actions ready to execute
                ready_actions = []
                for action in workflow.actions:
                    if action.id not in completed_actions:
                        if all(dep in completed_actions for dep in action.dependencies):
                            ready_actions.append(action)
                
                if not ready_actions:
                    raise Exception("Circular dependency detected in workflow")
                
                # Execute ready actions in parallel
                tasks = []
                for action in ready_actions:
                    task = asyncio.create_task(
                        self._execute_action(action, execution, action_results)
                    )
                    tasks.append((action.id, task))
                
                # Wait for completion
                for action_id, task in tasks:
                    try:
                        result = await task
                        action_results[action_id] = result
                        completed_actions.add(action_id)
                    except Exception as e:
                        logger.error(f"Action {action_id} failed: {e}")
                        action_results[action_id] = {"error": str(e)}
                        completed_actions.add(action_id)
            
            # Update execution with results
            execution.status = TaskStatus.COMPLETED
            execution.completed_at = datetime.utcnow()
            execution.action_results = action_results
            
        except Exception as e:
            logger.error(f"Workflow execution failed: {e}")
            execution.status = TaskStatus.FAILED
            execution.error_message = str(e)
            execution.completed_at = datetime.utcnow()
        
        finally:
            await self._update_execution(execution)
            if execution.id in self.running_executions:
                del self.running_executions[execution.id]
    
    async def _execute_action(self, action, execution: WorkflowExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a single workflow action"""
        logger.info(f"Executing action: {action.name} ({action.type})")
        
        try:
            if action.type == ActionType.AGENT_TASK:
                return await self._execute_agent_task(action, execution, context)
            elif action.type == ActionType.EMAIL_SEND:
                return await self._execute_email_send(action, execution, context)
            elif action.type == ActionType.CALENDAR_CREATE:
                return await self._execute_calendar_create(action, execution, context)
            elif action.type == ActionType.FILE_PROCESS:
                return await self._execute_file_process(action, execution, context)
            elif action.type == ActionType.NOTIFICATION:
                return await self._execute_notification(action, execution, context)
            elif action.type == ActionType.API_CALL:
                return await self._execute_api_call(action, execution, context)
            elif action.type == ActionType.CONDITION:
                return await self._execute_condition(action, execution, context)
            elif action.type == ActionType.DELAY:
                return await self._execute_delay(action, execution, context)
            else:
                raise ValueError(f"Unknown action type: {action.type}")
                
        except Exception as e:
            logger.error(f"Action execution failed: {e}")
            raise
    
    async def _execute_agent_task(self, action, execution: WorkflowExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute agent task action"""
        agent_id = action.agent_id
        if not agent_id:
            raise ValueError("Agent ID required for agent task")
        
        # Get agent
        agent = await self.agent_service.get_agent(agent_id)
        if not agent:
            raise ValueError(f"Agent {agent_id} not found")
        
        # Prepare task data
        task_data = {
            "instruction": action.config.get("instruction", ""),
            "context": {**context, **execution.trigger_data},
            "workflow_execution_id": execution.id
        }
        
        # Execute task
        result = await self.agent_service.execute_task(agent_id, task_data)
        return {"agent_result": result}
    
    async def _execute_email_send(self, action, execution: WorkflowExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute email send action"""
        # Use integration service to send email
        email_config = action.config
        
        # Template substitution
        subject = self._substitute_template(email_config.get("subject", ""), context)
        body = self._substitute_template(email_config.get("body", ""), context)
        
        result = await self.integration_service.send_email(
            to=email_config.get("to", []),
            subject=subject,
            body=body,
            cc=email_config.get("cc", []),
            bcc=email_config.get("bcc", [])
        )
        
        return {"email_sent": True, "message_id": result.get("message_id")}
    
    async def _execute_calendar_create(self, action, execution: WorkflowExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute calendar create action"""
        calendar_config = action.config
        
        # Template substitution
        title = self._substitute_template(calendar_config.get("title", ""), context)
        description = self._substitute_template(calendar_config.get("description", ""), context)
        
        result = await self.integration_service.create_calendar_event(
            title=title,
            description=description,
            start_time=calendar_config.get("start_time"),
            end_time=calendar_config.get("end_time"),
            attendees=calendar_config.get("attendees", [])
        )
        
        return {"event_created": True, "event_id": result.get("event_id")}
    
    async def _execute_file_process(self, action, execution: WorkflowExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute file process action"""
        file_config = action.config
        file_path = file_config.get("file_path")
        
        if not file_path:
            raise ValueError("File path required for file process action")
        
        result = await self.integration_service.process_file(
            file_path=file_path,
            processor_type=file_config.get("processor_type", "text_extraction")
        )
        
        return {"file_processed": True, "content": result.get("content")}
    
    async def _execute_notification(self, action, execution: WorkflowExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute notification action"""
        notification_config = action.config
        
        message = self._substitute_template(notification_config.get("message", ""), context)
        
        # Send notification (implementation depends on notification system)
        logger.info(f"Notification: {message}")
        
        return {"notification_sent": True, "message": message}
    
    async def _execute_api_call(self, action, execution: WorkflowExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute API call action"""
        api_config = action.config
        
        # Make API call using integration service
        result = await self.integration_service.make_api_call(
            url=api_config.get("url"),
            method=api_config.get("method", "GET"),
            headers=api_config.get("headers", {}),
            data=api_config.get("data", {})
        )
        
        return {"api_response": result}
    
    async def _execute_condition(self, action, execution: WorkflowExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute condition action"""
        condition_config = action.config
        condition = condition_config.get("condition", "")
        
        # Evaluate condition (simple implementation)
        result = eval(condition, {"context": context, "execution": execution.dict()})
        
        return {"condition_result": result}
    
    async def _execute_delay(self, action, execution: WorkflowExecution, context: Dict[str, Any]) -> Dict[str, Any]:
        """Execute delay action"""
        delay_seconds = action.config.get("delay_seconds", 0)
        await asyncio.sleep(delay_seconds)
        
        return {"delayed": delay_seconds}
    
    def _substitute_template(self, template: str, context: Dict[str, Any]) -> str:
        """Simple template substitution"""
        for key, value in context.items():
            template = template.replace(f"{{{key}}}", str(value))
        return template
    
    def _build_action_graph(self, actions) -> Dict[str, List[str]]:
        """Build action dependency graph"""
        graph = {}
        for action in actions:
            graph[action.id] = action.dependencies
        return graph
    
    async def _validate_workflow(self, workflow: Workflow):
        """Validate workflow structure"""
        # Check for circular dependencies
        action_ids = {action.id for action in workflow.actions}
        
        for action in workflow.actions:
            for dep in action.dependencies:
                if dep not in action_ids:
                    raise ValueError(f"Invalid dependency: {dep}")
        
        # Check for circular dependencies (simple check)
        visited = set()
        rec_stack = set()
        
        def has_cycle(action_id):
            if action_id in rec_stack:
                return True
            if action_id in visited:
                return False
            
            visited.add(action_id)
            rec_stack.add(action_id)
            
            action = next((a for a in workflow.actions if a.id == action_id), None)
            if action:
                for dep in action.dependencies:
                    if has_cycle(dep):
                        return True
            
            rec_stack.remove(action_id)
            return False
        
        for action in workflow.actions:
            if has_cycle(action.id):
                raise ValueError("Circular dependency detected")
    
    async def _update_execution(self, execution: WorkflowExecution):
        """Update execution in database"""
        await self.executions.update_one(
            {"_id": execution.id},
            {"$set": execution.dict()}
        )
    
    async def _cancel_workflow_executions(self, workflow_id: str):
        """Cancel running executions for a workflow"""
        executions = await self.executions.find(
            {"workflow_id": workflow_id, "status": TaskStatus.RUNNING}
        ).to_list(None)
        
        for execution_doc in executions:
            execution_id = execution_doc["_id"]
            if execution_id in self.running_executions:
                self.running_executions[execution_id].cancel()
                del self.running_executions[execution_id]
            
            await self.executions.update_one(
                {"_id": execution_id},
                {"$set": {"status": TaskStatus.CANCELLED, "completed_at": datetime.utcnow()}}
            )
    
    # Template management
    async def create_template(self, template_data: Dict[str, Any]) -> WorkflowTemplate:
        """Create workflow template"""
        template = WorkflowTemplate(**template_data)
        result = await self.templates.insert_one(template.dict())
        template.id = str(result.inserted_id)
        return template
    
    async def get_templates(self, category: Optional[str] = None) -> List[WorkflowTemplate]:
        """Get workflow templates"""
        query = {"category": category} if category else {}
        cursor = self.templates.find(query).sort("usage_count", -1)
        return [WorkflowTemplate(**doc) async for doc in cursor]
    
    # Agent collaboration
    async def create_collaboration(self, collaboration_data: Dict[str, Any]) -> AgentCollaboration:
        """Create agent collaboration"""
        collaboration = AgentCollaboration(**collaboration_data)
        result = await self.collaborations.insert_one(collaboration.dict())
        collaboration.id = str(result.inserted_id)
        return collaboration
    
    async def delegate_task(self, delegation_data: Dict[str, Any]) -> TaskDelegation:
        """Delegate task between agents"""
        delegation = TaskDelegation(**delegation_data)
        result = await self.delegations.insert_one(delegation.dict())
        delegation.id = str(result.inserted_id)
        
        # Notify receiving agent
        await self.agent_service.notify_task_delegation(delegation)
        
        return delegation

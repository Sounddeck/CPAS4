
"""
Reasoning Router for CPAS
API endpoints for hierarchical reasoning functionality
"""

from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from typing import Optional, Dict, Any, List
import logging

from ..services.hrm_adapter import hrm_adapter

router = APIRouter(prefix="/reasoning", tags=["reasoning"])
logger = logging.getLogger(__name__)

# Request/Response Models
class ReasoningRequest(BaseModel):
    problem: str
    context: Optional[Dict[str, Any]] = None
    max_iterations: Optional[int] = 5

class ComplexProblemRequest(BaseModel):
    problem: str
    max_iterations: Optional[int] = 5
    reasoning_depth: Optional[int] = 4

class ReasoningResponse(BaseModel):
    success: bool
    reasoning_chain: Optional[Dict[str, Any]] = None
    error: Optional[str] = None

@router.post("/analyze", response_model=ReasoningResponse)
async def analyze_problem(request: ReasoningRequest):
    """Perform hierarchical reasoning analysis on a problem"""
    try:
        reasoning_chain = hrm_adapter.reason(request.problem, request.context)
        
        return ReasoningResponse(
            success=True,
            reasoning_chain={
                'high_level_plan': reasoning_chain.high_level_plan,
                'low_level_steps': reasoning_chain.low_level_steps,
                'confidence_scores': reasoning_chain.confidence_scores,
                'reasoning_depth': reasoning_chain.reasoning_depth,
                'execution_time': reasoning_chain.execution_time
            }
        )
        
    except Exception as e:
        logger.error(f"Reasoning analysis failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/solve-complex")
async def solve_complex_problem(request: ComplexProblemRequest):
    """Solve complex problems using iterative hierarchical reasoning"""
    try:
        result = hrm_adapter.solve_complex_problem(
            problem=request.problem,
            max_iterations=request.max_iterations
        )
        
        # Convert reasoning chains to serializable format
        reasoning_trace = []
        for chain in result['reasoning_trace']:
            reasoning_trace.append({
                'high_level_plan': chain.high_level_plan,
                'low_level_steps': chain.low_level_steps,
                'confidence_scores': chain.confidence_scores,
                'reasoning_depth': chain.reasoning_depth,
                'execution_time': chain.execution_time
            })
        
        return JSONResponse(content={
            'success': True,
            'solution': result['solution'],
            'reasoning_trace': reasoning_trace,
            'iterations': result['iterations'],
            'final_confidence': result['final_confidence']
        })
        
    except Exception as e:
        logger.error(f"Complex problem solving failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/step-by-step")
async def step_by_step_reasoning(request: ReasoningRequest):
    """Get step-by-step reasoning breakdown"""
    try:
        reasoning_chain = hrm_adapter.reason(request.problem, request.context)
        
        # Create detailed step-by-step breakdown
        steps = []
        for i, (high_step, low_steps, confidence) in enumerate(zip(
            reasoning_chain.high_level_plan,
            reasoning_chain.low_level_steps,
            reasoning_chain.confidence_scores
        )):
            step_data = {
                'step_number': i + 1,
                'high_level_description': high_step,
                'low_level_substeps': [
                    {'substep_number': j + 1, 'description': substep}
                    for j, substep in enumerate(low_steps)
                ],
                'confidence': confidence,
                'reasoning_type': 'hierarchical'
            }
            steps.append(step_data)
        
        return JSONResponse(content={
            'success': True,
            'problem': request.problem,
            'total_steps': len(steps),
            'overall_confidence': sum(reasoning_chain.confidence_scores) / len(reasoning_chain.confidence_scores),
            'reasoning_steps': steps,
            'execution_time': reasoning_chain.execution_time
        })
        
    except Exception as e:
        logger.error(f"Step-by-step reasoning failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/capabilities")
async def get_reasoning_capabilities():
    """Get information about reasoning capabilities"""
    try:
        capabilities = {
            'hierarchical_reasoning': True,
            'iterative_problem_solving': True,
            'confidence_scoring': True,
            'multi_level_decomposition': True,
            'reasoning_types': [
                'analytical',
                'creative',
                'logical',
                'strategic',
                'mathematical'
            ],
            'max_reasoning_depth': 10,
            'max_iterations': 10,
            'hrm_available': hrm_adapter.model is not None
        }
        
        return JSONResponse(content=capabilities)
        
    except Exception as e:
        logger.error(f"Failed to get reasoning capabilities: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.post("/validate-reasoning")
async def validate_reasoning_chain(reasoning_data: Dict[str, Any]):
    """Validate a reasoning chain for logical consistency"""
    try:
        # Simple validation logic
        validation_results = {
            'is_valid': True,
            'issues': [],
            'suggestions': [],
            'confidence': 0.8
        }
        
        # Check for basic structure
        if 'high_level_plan' not in reasoning_data:
            validation_results['is_valid'] = False
            validation_results['issues'].append('Missing high-level plan')
        
        if 'low_level_steps' not in reasoning_data:
            validation_results['is_valid'] = False
            validation_results['issues'].append('Missing low-level steps')
        
        # Check consistency between high and low level
        high_level_plan = reasoning_data.get('high_level_plan', [])
        low_level_steps = reasoning_data.get('low_level_steps', [])
        
        if len(high_level_plan) != len(low_level_steps):
            validation_results['issues'].append('Mismatch between high-level and low-level step counts')
            validation_results['suggestions'].append('Ensure each high-level step has corresponding low-level steps')
        
        # Check confidence scores
        confidence_scores = reasoning_data.get('confidence_scores', [])
        if confidence_scores:
            avg_confidence = sum(confidence_scores) / len(confidence_scores)
            if avg_confidence < 0.5:
                validation_results['suggestions'].append('Low confidence scores suggest reasoning may need refinement')
        
        return JSONResponse(content=validation_results)
        
    except Exception as e:
        logger.error(f"Reasoning validation failed: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@router.get("/health")
async def reasoning_health_check():
    """Health check for reasoning service"""
    try:
        health_status = {
            'hrm_adapter_available': hrm_adapter is not None,
            'hrm_model_loaded': hrm_adapter.model is not None,
            'fallback_reasoning_available': True,
            'reasoning_methods': ['hierarchical', 'fallback']
        }
        
        return JSONResponse(content={
            'status': 'healthy',
            'components': health_status
        })
        
    except Exception as e:
        logger.error(f"Reasoning health check failed: {e}")
        return JSONResponse(
            status_code=500,
            content={'status': 'unhealthy', 'error': str(e)}
        )

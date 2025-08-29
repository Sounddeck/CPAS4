
"""
HRM (Hierarchical Reasoning Model) Adapter for CPAS
Integrates HRM reasoning capabilities with the CPAS architecture
"""

import sys
import os
import torch
import numpy as np
from typing import Dict, List, Optional, Any, Tuple
from dataclasses import dataclass
import logging

# Add HRM to path
sys.path.append('/home/ubuntu/cpas_enhanced/hrm')

try:
    from models.hrm.hrm_act_v1 import HierarchicalReasoningModel_ACTV1Config, HierarchicalReasoningModel_ACTV1
    from models.common import trunc_normal_init_
    HRM_AVAILABLE = True
except ImportError as e:
    logging.warning(f"HRM not available: {e}")
    HRM_AVAILABLE = False

@dataclass
class ReasoningChain:
    """Represents a hierarchical reasoning chain"""
    high_level_plan: List[str]
    low_level_steps: List[List[str]]
    confidence_scores: List[float]
    reasoning_depth: int
    execution_time: float

class HRMAdapter:
    """Adapter class to integrate HRM with CPAS architecture"""
    
    def __init__(self, config: Optional[Dict] = None):
        self.config = config or self._default_config()
        self.model = None
        self.device = torch.device('cuda' if torch.cuda.is_available() else 'cpu')
        self.logger = logging.getLogger(__name__)
        
        if HRM_AVAILABLE:
            self._initialize_model()
        else:
            self.logger.warning("HRM not available, using fallback reasoning")
    
    def _default_config(self) -> Dict:
        """Default configuration for HRM"""
        return {
            'batch_size': 1,
            'seq_len': 512,
            'puzzle_emb_ndim': 64,
            'num_puzzle_identifiers': 1000,
            'vocab_size': 32000,
            'H_cycles': 4,
            'L_cycles': 8,
            'H_layers': 6,
            'L_layers': 12,
            'hidden_size': 512,
            'expansion': 2.0,
            'num_heads': 8,
            'pos_encodings': 'learned',
            'rms_norm_eps': 1e-5
        }
    
    def _initialize_model(self):
        """Initialize the HRM model"""
        try:
            if HRM_AVAILABLE:
                hrm_config = HierarchicalReasoningModel_ACTV1Config(**self.config)
                self.model = HierarchicalReasoningModel_ACTV1(hrm_config)
                self.model.to(self.device)
                self.model.eval()
                self.logger.info("HRM model initialized successfully")
            else:
                self.logger.warning("HRM not available, using fallback")
        except Exception as e:
            self.logger.error(f"Failed to initialize HRM: {e}")
            self.model = None
    
    def reason(self, problem: str, context: Optional[Dict] = None) -> ReasoningChain:
        """
        Perform hierarchical reasoning on a given problem
        
        Args:
            problem: The problem statement to reason about
            context: Additional context information
            
        Returns:
            ReasoningChain: The reasoning chain with hierarchical steps
        """
        if self.model is None or not HRM_AVAILABLE:
            return self._fallback_reasoning(problem, context)
        
        try:
            # Tokenize and prepare input
            input_tokens = self._tokenize_problem(problem)
            
            # Run HRM inference
            with torch.no_grad():
                reasoning_output = self._run_hrm_inference(input_tokens)
            
            # Parse reasoning chain
            chain = self._parse_reasoning_output(reasoning_output, problem)
            
            return chain
            
        except Exception as e:
            self.logger.error(f"HRM reasoning failed: {e}")
            return self._fallback_reasoning(problem, context)
    
    def _tokenize_problem(self, problem: str) -> torch.Tensor:
        """Tokenize problem for HRM input"""
        # Simple tokenization - in practice, use proper tokenizer
        tokens = [ord(c) % self.config['vocab_size'] for c in problem[:self.config['seq_len']]]
        tokens += [0] * (self.config['seq_len'] - len(tokens))  # Pad
        return torch.tensor([tokens], device=self.device)
    
    def _run_hrm_inference(self, input_tokens: torch.Tensor) -> Dict:
        """Run HRM model inference"""
        # This is a simplified version - actual implementation would depend on HRM's interface
        batch_size, seq_len = input_tokens.shape
        
        # Create dummy puzzle embeddings
        puzzle_ids = torch.zeros(batch_size, dtype=torch.long, device=self.device)
        
        # Run model (simplified)
        output = {
            'high_level_reasoning': torch.randn(batch_size, 4, self.config['hidden_size'], device=self.device),
            'low_level_steps': torch.randn(batch_size, 8, self.config['hidden_size'], device=self.device),
            'confidence': torch.sigmoid(torch.randn(batch_size, device=self.device))
        }
        
        return output
    
    def _parse_reasoning_output(self, output: Dict, problem: str) -> ReasoningChain:
        """Parse HRM output into reasoning chain"""
        # Extract high-level plan
        high_level_plan = [
            f"High-level step {i+1}: Analyze {problem[:20]}..." 
            for i in range(output['high_level_reasoning'].shape[1])
        ]
        
        # Extract low-level steps
        low_level_steps = [
            [f"Low-level substep {j+1} for step {i+1}" for j in range(2)]
            for i in range(len(high_level_plan))
        ]
        
        # Extract confidence scores
        confidence_scores = [float(output['confidence'][0])] * len(high_level_plan)
        
        return ReasoningChain(
            high_level_plan=high_level_plan,
            low_level_steps=low_level_steps,
            confidence_scores=confidence_scores,
            reasoning_depth=len(high_level_plan),
            execution_time=0.1  # Placeholder
        )
    
    def _fallback_reasoning(self, problem: str, context: Optional[Dict] = None) -> ReasoningChain:
        """Fallback reasoning when HRM is not available"""
        self.logger.info("Using fallback reasoning")
        
        # Simple rule-based reasoning
        high_level_plan = [
            "Understand the problem",
            "Identify key components",
            "Develop solution strategy",
            "Execute solution"
        ]
        
        low_level_steps = [
            ["Parse problem statement", "Identify constraints"],
            ["List known variables", "Identify unknowns"],
            ["Choose appropriate method", "Plan execution steps"],
            ["Apply method", "Verify solution"]
        ]
        
        confidence_scores = [0.7, 0.8, 0.6, 0.7]
        
        return ReasoningChain(
            high_level_plan=high_level_plan,
            low_level_steps=low_level_steps,
            confidence_scores=confidence_scores,
            reasoning_depth=4,
            execution_time=0.05
        )
    
    def solve_complex_problem(self, problem: str, max_iterations: int = 5) -> Dict[str, Any]:
        """
        Solve complex problems using iterative hierarchical reasoning
        
        Args:
            problem: Complex problem to solve
            max_iterations: Maximum reasoning iterations
            
        Returns:
            Dict containing solution and reasoning trace
        """
        reasoning_trace = []
        current_problem = problem
        
        for iteration in range(max_iterations):
            chain = self.reason(current_problem)
            reasoning_trace.append(chain)
            
            # Check if solution is satisfactory
            avg_confidence = np.mean(chain.confidence_scores)
            if avg_confidence > 0.9:
                break
            
            # Refine problem based on reasoning
            current_problem = self._refine_problem(current_problem, chain)
        
        return {
            'solution': self._extract_solution(reasoning_trace),
            'reasoning_trace': reasoning_trace,
            'iterations': len(reasoning_trace),
            'final_confidence': avg_confidence
        }
    
    def _refine_problem(self, problem: str, chain: ReasoningChain) -> str:
        """Refine problem based on reasoning chain"""
        # Simple refinement - focus on low-confidence areas
        low_conf_steps = [i for i, conf in enumerate(chain.confidence_scores) if conf < 0.8]
        if low_conf_steps:
            return f"{problem} [Focus on: {', '.join([chain.high_level_plan[i] for i in low_conf_steps])}]"
        return problem
    
    def _extract_solution(self, reasoning_trace: List[ReasoningChain]) -> str:
        """Extract final solution from reasoning trace"""
        if not reasoning_trace:
            return "No solution found"
        
        final_chain = reasoning_trace[-1]
        solution_steps = []
        
        for i, (high_step, low_steps) in enumerate(zip(final_chain.high_level_plan, final_chain.low_level_steps)):
            solution_steps.append(f"{i+1}. {high_step}")
            for j, low_step in enumerate(low_steps):
                solution_steps.append(f"   {chr(97+j)}. {low_step}")
        
        return "\n".join(solution_steps)

# Global HRM adapter instance
hrm_adapter = HRMAdapter()


"""
Technical Agent - Specialized agent for technical tasks and problem-solving
"""

import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime
from loguru import logger

from models.agent import Agent, AgentCapability, AgentPersonality
from services.agent_core import AgentCore

class TechnicalAgent(AgentCore):
    """Specialized agent for technical problem-solving, code analysis, and system design"""
    
    def __init__(self, agent_id: str, db):
        super().__init__(agent_id, db)
        self.agent_type = "technical_agent"
        self.capabilities = [
            AgentCapability(
                name="code_analysis",
                description="Analyze and review code for quality and issues",
                confidence=0.92
            ),
            AgentCapability(
                name="system_design",
                description="Design scalable and efficient system architectures",
                confidence=0.88
            ),
            AgentCapability(
                name="debugging",
                description="Identify and resolve technical issues",
                confidence=0.90
            ),
            AgentCapability(
                name="performance_optimization",
                description="Optimize system and code performance",
                confidence=0.85
            ),
            AgentCapability(
                name="security_analysis",
                description="Identify security vulnerabilities and solutions",
                confidence=0.87
            ),
            AgentCapability(
                name="documentation",
                description="Create comprehensive technical documentation",
                confidence=0.89
            )
        ]
        
        self.personality = AgentPersonality(
            traits={
                "analytical": 0.95,
                "precise": 0.92,
                "logical": 0.90,
                "methodical": 0.88,
                "detail_oriented": 0.85
            },
            communication_style="technical_precise",
            decision_making="logical_systematic"
        )
    
    async def process_task(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Process technical requests"""
        task_type = task_data.get("type", "general_technical")
        
        if task_type == "code_review":
            return await self._review_code(task_data)
        elif task_type == "system_design":
            return await self._design_system(task_data)
        elif task_type == "debug_issue":
            return await self._debug_issue(task_data)
        elif task_type == "performance_analysis":
            return await self._analyze_performance(task_data)
        elif task_type == "security_audit":
            return await self._conduct_security_audit(task_data)
        elif task_type == "architecture_review":
            return await self._review_architecture(task_data)
        elif task_type == "technical_documentation":
            return await self._create_technical_documentation(task_data)
        else:
            return await self._general_technical_assistance(task_data)
    
    async def _review_code(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive code review"""
        code = task_data.get("code", "")
        language = task_data.get("language", "python")
        review_focus = task_data.get("focus", ["quality", "security", "performance"])
        
        # Analyze code structure
        structure_analysis = await self._analyze_code_structure(code, language)
        
        # Check code quality
        quality_issues = await self._identify_quality_issues(code, language)
        
        # Security analysis
        security_issues = await self._identify_security_issues(code, language)
        
        # Performance analysis
        performance_issues = await self._identify_performance_issues(code, language)
        
        # Best practices check
        best_practices = await self._check_best_practices(code, language)
        
        # Generate improvement suggestions
        improvements = await self._generate_improvement_suggestions(
            code, quality_issues, security_issues, performance_issues
        )
        
        code_review = {
            "code_analyzed": len(code.split('\n')),
            "language": language,
            "review_focus": review_focus,
            "structure_analysis": structure_analysis,
            "quality_issues": quality_issues,
            "security_issues": security_issues,
            "performance_issues": performance_issues,
            "best_practices_compliance": best_practices,
            "improvement_suggestions": improvements,
            "overall_score": await self._calculate_code_score(
                quality_issues, security_issues, performance_issues
            ),
            "refactored_code": await self._suggest_refactored_code(code, improvements),
            "generated_at": datetime.utcnow()
        }
        
        # Store review in memory
        await self.store_memory({
            "type": "code_review_completed",
            "language": language,
            "review": code_review
        })
        
        return {
            "success": True,
            "code_review": code_review
        }
    
    async def _design_system(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Design system architecture"""
        requirements = task_data.get("requirements", {})
        constraints = task_data.get("constraints", {})
        scale = task_data.get("scale", "medium")
        technology_preferences = task_data.get("technology_preferences", [])
        
        # Analyze requirements
        requirements_analysis = await self._analyze_requirements(requirements, constraints)
        
        # Design architecture
        architecture = await self._design_architecture(requirements_analysis, scale)
        
        # Select technologies
        technology_stack = await self._recommend_technology_stack(
            architecture, technology_preferences, constraints
        )
        
        # Design data model
        data_model = await self._design_data_model(requirements_analysis)
        
        # Create API design
        api_design = await self._design_api_structure(architecture, requirements_analysis)
        
        # Identify potential challenges
        challenges = await self._identify_design_challenges(architecture, scale)
        
        # Generate implementation plan
        implementation_plan = await self._create_implementation_plan(
            architecture, technology_stack, challenges
        )
        
        system_design = {
            "requirements": requirements,
            "constraints": constraints,
            "scale": scale,
            "requirements_analysis": requirements_analysis,
            "architecture": architecture,
            "technology_stack": technology_stack,
            "data_model": data_model,
            "api_design": api_design,
            "scalability_considerations": await self._analyze_scalability(architecture, scale),
            "security_considerations": await self._analyze_security_requirements(architecture),
            "challenges": challenges,
            "implementation_plan": implementation_plan,
            "cost_estimation": await self._estimate_implementation_cost(technology_stack, scale),
            "generated_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "system_design": system_design
        }
    
    async def _debug_issue(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Debug technical issues"""
        issue_description = task_data.get("issue_description", "")
        error_logs = task_data.get("error_logs", "")
        code_context = task_data.get("code_context", "")
        environment = task_data.get("environment", {})
        
        # Analyze error patterns
        error_analysis = await self._analyze_error_patterns(error_logs, issue_description)
        
        # Identify root causes
        root_causes = await self._identify_root_causes(
            error_analysis, code_context, environment
        )
        
        # Generate debugging steps
        debugging_steps = await self._generate_debugging_steps(root_causes, environment)
        
        # Suggest solutions
        solutions = await self._suggest_solutions(root_causes, code_context)
        
        # Create prevention strategies
        prevention = await self._suggest_prevention_strategies(root_causes, solutions)
        
        debug_report = {
            "issue_description": issue_description,
            "error_analysis": error_analysis,
            "root_causes": root_causes,
            "debugging_steps": debugging_steps,
            "solutions": solutions,
            "prevention_strategies": prevention,
            "testing_recommendations": await self._recommend_testing_approach(solutions),
            "monitoring_suggestions": await self._suggest_monitoring_improvements(root_causes),
            "generated_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "debug_report": debug_report
        }
    
    async def _analyze_performance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze system or code performance"""
        performance_data = task_data.get("performance_data", {})
        code = task_data.get("code", "")
        system_metrics = task_data.get("system_metrics", {})
        benchmarks = task_data.get("benchmarks", {})
        
        # Analyze performance metrics
        metrics_analysis = await self._analyze_performance_metrics(
            performance_data, system_metrics, benchmarks
        )
        
        # Identify bottlenecks
        bottlenecks = await self._identify_bottlenecks(metrics_analysis, code)
        
        # Generate optimization recommendations
        optimizations = await self._generate_optimization_recommendations(
            bottlenecks, code, system_metrics
        )
        
        # Estimate improvement potential
        improvement_estimates = await self._estimate_performance_improvements(
            optimizations, metrics_analysis
        )
        
        # Create optimization plan
        optimization_plan = await self._create_optimization_plan(
            optimizations, improvement_estimates
        )
        
        performance_analysis = {
            "performance_data": performance_data,
            "metrics_analysis": metrics_analysis,
            "bottlenecks": bottlenecks,
            "optimizations": optimizations,
            "improvement_estimates": improvement_estimates,
            "optimization_plan": optimization_plan,
            "monitoring_recommendations": await self._recommend_performance_monitoring(bottlenecks),
            "generated_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "performance_analysis": performance_analysis
        }
    
    async def _conduct_security_audit(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Conduct comprehensive security audit"""
        code = task_data.get("code", "")
        system_config = task_data.get("system_config", {})
        dependencies = task_data.get("dependencies", [])
        audit_scope = task_data.get("scope", ["code", "config", "dependencies"])
        
        security_findings = {}
        
        if "code" in audit_scope:
            security_findings["code_vulnerabilities"] = await self._scan_code_vulnerabilities(code)
        
        if "config" in audit_scope:
            security_findings["config_issues"] = await self._audit_system_config(system_config)
        
        if "dependencies" in audit_scope:
            security_findings["dependency_vulnerabilities"] = await self._audit_dependencies(dependencies)
        
        # Risk assessment
        risk_assessment = await self._assess_security_risks(security_findings)
        
        # Generate remediation plan
        remediation_plan = await self._create_remediation_plan(security_findings, risk_assessment)
        
        # Security best practices
        best_practices = await self._recommend_security_best_practices(security_findings)
        
        security_audit = {
            "audit_scope": audit_scope,
            "security_findings": security_findings,
            "risk_assessment": risk_assessment,
            "remediation_plan": remediation_plan,
            "best_practices": best_practices,
            "compliance_check": await self._check_compliance_standards(security_findings),
            "security_score": await self._calculate_security_score(security_findings),
            "generated_at": datetime.utcnow()
        }
        
        return {
            "success": True,
            "security_audit": security_audit
        }
    
    async def _analyze_code_structure(self, code: str, language: str) -> Dict[str, Any]:
        """Analyze code structure and organization"""
        lines = code.split('\n')
        
        structure = {
            "total_lines": len(lines),
            "code_lines": len([line for line in lines if line.strip() and not line.strip().startswith('#')]),
            "comment_lines": len([line for line in lines if line.strip().startswith('#')]),
            "blank_lines": len([line for line in lines if not line.strip()]),
            "functions_count": len([line for line in lines if 'def ' in line]),
            "classes_count": len([line for line in lines if 'class ' in line]),
            "complexity_estimate": await self._estimate_complexity(code),
            "maintainability_score": await self._calculate_maintainability(code)
        }
        
        return structure
    
    async def _identify_quality_issues(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Identify code quality issues"""
        issues = []
        
        # Check for common quality issues
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            # Long lines
            if len(line) > 100:
                issues.append({
                    "type": "style",
                    "severity": "low",
                    "line": i,
                    "message": "Line too long (>100 characters)",
                    "suggestion": "Break long line into multiple lines"
                })
            
            # TODO comments
            if "TODO" in line.upper():
                issues.append({
                    "type": "maintenance",
                    "severity": "medium",
                    "line": i,
                    "message": "TODO comment found",
                    "suggestion": "Address TODO or create proper issue"
                })
        
        # Check for duplicated code patterns
        duplicates = await self._find_duplicate_code(code)
        for duplicate in duplicates:
            issues.append({
                "type": "duplication",
                "severity": "medium",
                "message": "Duplicated code detected",
                "suggestion": "Extract common functionality into function"
            })
        
        return issues
    
    async def _identify_security_issues(self, code: str, language: str) -> List[Dict[str, Any]]:
        """Identify potential security vulnerabilities"""
        security_issues = []
        
        # Common security patterns to check
        security_patterns = {
            "sql_injection": ["execute(", "query(", "SELECT", "INSERT", "UPDATE", "DELETE"],
            "xss": ["innerHTML", "document.write", "eval("],
            "hardcoded_secrets": ["password", "api_key", "secret", "token"],
            "unsafe_deserialization": ["pickle.loads", "eval(", "exec("]
        }
        
        lines = code.split('\n')
        
        for i, line in enumerate(lines, 1):
            for vulnerability_type, patterns in security_patterns.items():
                for pattern in patterns:
                    if pattern.lower() in line.lower():
                        security_issues.append({
                            "type": vulnerability_type,
                            "severity": "high" if vulnerability_type in ["sql_injection", "xss"] else "medium",
                            "line": i,
                            "message": f"Potential {vulnerability_type.replace('_', ' ')} vulnerability",
                            "suggestion": await self._get_security_suggestion(vulnerability_type)
                        })
        
        return security_issues
    
    async def _get_security_suggestion(self, vulnerability_type: str) -> str:
        """Get security improvement suggestion"""
        suggestions = {
            "sql_injection": "Use parameterized queries or ORM",
            "xss": "Sanitize user input and use safe DOM manipulation",
            "hardcoded_secrets": "Use environment variables or secure key management",
            "unsafe_deserialization": "Validate input and use safe serialization methods"
        }
        return suggestions.get(vulnerability_type, "Review for security best practices")
    
    async def _general_technical_assistance(self, task_data: Dict[str, Any]) -> Dict[str, Any]:
        """Handle general technical queries"""
        query = task_data.get("query", "")
        context = task_data.get("context", {})
        
        prompt = f"""
        As a technical expert, provide detailed assistance for this query:
        
        Query: {query}
        Context: {context}
        
        Provide:
        1. Technical analysis
        2. Best practices
        3. Implementation suggestions
        4. Potential challenges
        5. Alternative approaches
        """
        
        response = await self.llm_service.generate(
            prompt=prompt,
            model="deepseek-r1:7b",  # Use reasoning model for technical analysis
            max_tokens=800
        )
        
        return {
            "success": True,
            "technical_response": response.get("response", ""),
            "additional_resources": [
                "Official documentation",
                "Best practice guides",
                "Community forums",
                "Code examples",
                "Performance benchmarks"
            ],
            "follow_up_questions": await self._generate_follow_up_questions(query)
        }
    
    async def _generate_follow_up_questions(self, query: str) -> List[str]:
        """Generate relevant follow-up questions"""
        return [
            "What specific constraints or requirements do you have?",
            "What is your current technical stack?",
            "What performance requirements need to be met?",
            "Are there any security considerations?",
            "What is the expected scale or load?"
        ]

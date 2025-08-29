
"""
Base OSINT Module
Common functionality for all OSINT modules
"""

import asyncio
import time
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from abc import ABC, abstractmethod

import aiohttp
from loguru import logger


class RateLimiter:
    """Rate limiting for API calls"""
    
    def __init__(self, max_requests: int, time_window: int):
        self.max_requests = max_requests
        self.time_window = time_window
        self.requests = []
    
    async def acquire(self):
        """Acquire permission to make a request"""
        now = time.time()
        
        # Remove old requests outside the time window
        self.requests = [req_time for req_time in self.requests if now - req_time < self.time_window]
        
        # Check if we can make a request
        if len(self.requests) >= self.max_requests:
            # Calculate wait time
            oldest_request = min(self.requests)
            wait_time = self.time_window - (now - oldest_request)
            
            if wait_time > 0:
                logger.info(f"Rate limit reached, waiting {wait_time:.2f} seconds")
                await asyncio.sleep(wait_time)
        
        # Record this request
        self.requests.append(now)


class OSINTBase(ABC):
    """
    Base class for all OSINT modules
    Provides common functionality and ethical guidelines
    """
    
    def __init__(self):
        self.session: Optional[aiohttp.ClientSession] = None
        self.rate_limiters: Dict[str, RateLimiter] = {}
        
        # Ethical guidelines
        self.ethical_guidelines = {
            "respect_robots_txt": True,
            "respect_rate_limits": True,
            "no_personal_data_storage": True,
            "educational_use_only": True,
            "respect_privacy": True
        }
        
        # Common headers for web requests
        self.default_headers = {
            "User-Agent": "CPAS-OSINT/1.0 (Educational Research Tool)",
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.5",
            "Accept-Encoding": "gzip, deflate",
            "Connection": "keep-alive",
            "Upgrade-Insecure-Requests": "1"
        }
    
    async def __aenter__(self):
        """Async context manager entry"""
        self.session = aiohttp.ClientSession(
            headers=self.default_headers,
            timeout=aiohttp.ClientTimeout(total=30)
        )
        return self
    
    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """Async context manager exit"""
        if self.session:
            await self.session.close()
    
    def get_rate_limiter(self, service: str, max_requests: int, time_window: int) -> RateLimiter:
        """Get or create rate limiter for a service"""
        if service not in self.rate_limiters:
            self.rate_limiters[service] = RateLimiter(max_requests, time_window)
        return self.rate_limiters[service]
    
    async def make_request(
        self, 
        url: str, 
        method: str = "GET", 
        headers: Optional[Dict[str, str]] = None,
        params: Optional[Dict[str, Any]] = None,
        data: Optional[Dict[str, Any]] = None,
        rate_limit_service: Optional[str] = None
    ) -> Optional[aiohttp.ClientResponse]:
        """
        Make an HTTP request with rate limiting and error handling
        """
        try:
            # Apply rate limiting if specified
            if rate_limit_service and rate_limit_service in self.rate_limiters:
                await self.rate_limiters[rate_limit_service].acquire()
            
            # Merge headers
            request_headers = self.default_headers.copy()
            if headers:
                request_headers.update(headers)
            
            # Make request
            if not self.session:
                self.session = aiohttp.ClientSession(
                    headers=self.default_headers,
                    timeout=aiohttp.ClientTimeout(total=30)
                )
            
            async with self.session.request(
                method=method,
                url=url,
                headers=request_headers,
                params=params,
                json=data
            ) as response:
                return response
                
        except Exception as e:
            logger.error(f"Request error for {url}: {e}")
            return None
    
    def validate_input(self, input_data: Any, input_type: str) -> bool:
        """Validate input data for security and format"""
        
        if input_type == "email":
            import re
            email_pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(email_pattern, str(input_data)))
        
        elif input_type == "username":
            # Basic username validation
            if not isinstance(input_data, str):
                return False
            if len(input_data) < 1 or len(input_data) > 50:
                return False
            # Allow alphanumeric, underscore, hyphen
            import re
            return bool(re.match(r'^[a-zA-Z0-9_-]+$', input_data))
        
        elif input_type == "domain":
            import re
            domain_pattern = r'^[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
            return bool(re.match(domain_pattern, str(input_data)))
        
        elif input_type == "ip":
            import ipaddress
            try:
                ipaddress.ip_address(str(input_data))
                return True
            except ValueError:
                return False
        
        return True
    
    def sanitize_output(self, data: Any) -> Any:
        """Sanitize output data to remove sensitive information"""
        
        if isinstance(data, dict):
            sanitized = {}
            for key, value in data.items():
                # Skip potentially sensitive keys
                if key.lower() in ['password', 'token', 'key', 'secret', 'private']:
                    sanitized[key] = "[REDACTED]"
                else:
                    sanitized[key] = self.sanitize_output(value)
            return sanitized
        
        elif isinstance(data, list):
            return [self.sanitize_output(item) for item in data]
        
        elif isinstance(data, str):
            # Basic email obfuscation
            import re
            email_pattern = r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'
            return re.sub(email_pattern, '[EMAIL_REDACTED]', data)
        
        return data
    
    def log_osint_activity(self, activity: str, target: str, result: str):
        """Log OSINT activity for audit purposes"""
        
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "activity": activity,
            "target": target,
            "result": result,
            "module": self.__class__.__name__
        }
        
        logger.info(f"OSINT Activity: {log_entry}")
    
    @abstractmethod
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """Abstract method for search functionality"""
        pass
    
    @abstractmethod
    async def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Abstract method for analysis functionality"""
        pass

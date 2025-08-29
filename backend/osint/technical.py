
"""
Technical Intelligence (TECHINT)
Domain analysis, IP investigation, SSL certificates, and technical reconnaissance
"""

import asyncio
import json
import socket
import ssl
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from dataclasses import dataclass
from ipaddress import ip_address, ip_network

import aiohttp
import dns.resolver
from loguru import logger

from .base import OSINTBase


@dataclass
class DomainInfo:
    """Domain information structure"""
    domain: str
    registrar: Optional[str]
    creation_date: Optional[datetime]
    expiration_date: Optional[datetime]
    name_servers: List[str]
    dns_records: Dict[str, List[str]]
    whois_data: Optional[Dict[str, Any]]
    ssl_info: Optional[Dict[str, Any]]
    subdomains: List[str]
    technologies: List[str]


@dataclass
class IPInfo:
    """IP address information structure"""
    ip: str
    hostname: Optional[str]
    organization: Optional[str]
    country: Optional[str]
    city: Optional[str]
    isp: Optional[str]
    asn: Optional[str]
    ports: List[int]
    services: Dict[int, str]
    geolocation: Optional[Dict[str, float]]
    reputation: Optional[str]


class TechnicalIntelligence(OSINTBase):
    """
    Technical Intelligence gathering
    Domain analysis, IP investigation, and infrastructure reconnaissance
    """
    
    def __init__(self):
        super().__init__()
        
        # DNS record types to query
        self.dns_record_types = [
            'A', 'AAAA', 'CNAME', 'MX', 'NS', 'TXT', 'SOA', 'PTR'
        ]
        
        # Common ports to scan
        self.common_ports = [
            21, 22, 23, 25, 53, 80, 110, 143, 443, 993, 995, 
            1433, 3306, 3389, 5432, 5900, 8080, 8443
        ]
        
        # Rate limiting for external services
        self.setup_rate_limiters()
    
    def setup_rate_limiters(self):
        """Setup rate limiters for various services"""
        self.get_rate_limiter("dns", 100, 60)  # 100 DNS queries per minute
        self.get_rate_limiter("whois", 10, 60)  # 10 WHOIS queries per minute
        self.get_rate_limiter("ssl", 50, 60)    # 50 SSL checks per minute
        self.get_rate_limiter("geolocation", 1000, 3600)  # 1000 geo queries per hour
    
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Main search method for technical intelligence
        Automatically detects if query is domain or IP
        """
        try:
            # Validate and determine query type
            if self.validate_input(query, "domain"):
                return await self.analyze_domain(query)
            elif self.validate_input(query, "ip"):
                return await self.analyze_ip(query)
            else:
                return {
                    "success": False,
                    "error": "Invalid input: must be a valid domain or IP address",
                    "query": query
                }
                
        except Exception as e:
            logger.error(f"Technical intelligence search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Analyze technical data for patterns and insights"""
        try:
            analysis_type = kwargs.get("type", "general")
            
            if analysis_type == "domain":
                return await self._analyze_domain_data(data)
            elif analysis_type == "ip":
                return await self._analyze_ip_data(data)
            elif analysis_type == "infrastructure":
                return await self._analyze_infrastructure(data)
            else:
                return await self._general_technical_analysis(data)
                
        except Exception as e:
            logger.error(f"Technical analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def analyze_domain(self, domain: str) -> Dict[str, Any]:
        """Comprehensive domain analysis"""
        try:
            logger.info(f"Analyzing domain: {domain}")
            
            # Parallel execution of different analysis tasks
            tasks = [
                self._get_dns_records(domain),
                self._get_whois_info(domain),
                self._get_ssl_info(domain),
                self._find_subdomains(domain),
                self._detect_technologies(domain)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            dns_records = results[0] if not isinstance(results[0], Exception) else {}
            whois_data = results[1] if not isinstance(results[1], Exception) else {}
            ssl_info = results[2] if not isinstance(results[2], Exception) else {}
            subdomains = results[3] if not isinstance(results[3], Exception) else []
            technologies = results[4] if not isinstance(results[4], Exception) else []
            
            # Create domain info object
            domain_info = DomainInfo(
                domain=domain,
                registrar=whois_data.get("registrar"),
                creation_date=whois_data.get("creation_date"),
                expiration_date=whois_data.get("expiration_date"),
                name_servers=whois_data.get("name_servers", []),
                dns_records=dns_records,
                whois_data=whois_data,
                ssl_info=ssl_info,
                subdomains=subdomains,
                technologies=technologies
            )
            
            # Perform analysis
            analysis = await self._analyze_domain_data(domain_info)
            
            self.log_osint_activity("domain_analysis", domain, "completed")
            
            return {
                "success": True,
                "domain": domain,
                "domain_info": domain_info.__dict__,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Domain analysis error for {domain}: {e}")
            return {
                "success": False,
                "error": str(e),
                "domain": domain
            }
    
    async def analyze_ip(self, ip: str) -> Dict[str, Any]:
        """Comprehensive IP address analysis"""
        try:
            logger.info(f"Analyzing IP: {ip}")
            
            # Parallel execution of different analysis tasks
            tasks = [
                self._get_ip_geolocation(ip),
                self._get_ip_whois(ip),
                self._scan_ports(ip),
                self._get_reverse_dns(ip),
                self._check_ip_reputation(ip)
            ]
            
            results = await asyncio.gather(*tasks, return_exceptions=True)
            
            # Process results
            geolocation = results[0] if not isinstance(results[0], Exception) else {}
            whois_data = results[1] if not isinstance(results[1], Exception) else {}
            port_scan = results[2] if not isinstance(results[2], Exception) else {}
            reverse_dns = results[3] if not isinstance(results[3], Exception) else None
            reputation = results[4] if not isinstance(results[4], Exception) else None
            
            # Create IP info object
            ip_info = IPInfo(
                ip=ip,
                hostname=reverse_dns,
                organization=whois_data.get("org"),
                country=geolocation.get("country"),
                city=geolocation.get("city"),
                isp=geolocation.get("isp"),
                asn=whois_data.get("asn"),
                ports=port_scan.get("open_ports", []),
                services=port_scan.get("services", {}),
                geolocation=geolocation.get("coordinates"),
                reputation=reputation
            )
            
            # Perform analysis
            analysis = await self._analyze_ip_data(ip_info)
            
            self.log_osint_activity("ip_analysis", ip, "completed")
            
            return {
                "success": True,
                "ip": ip,
                "ip_info": ip_info.__dict__,
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"IP analysis error for {ip}: {e}")
            return {
                "success": False,
                "error": str(e),
                "ip": ip
            }
    
    async def _get_dns_records(self, domain: str) -> Dict[str, List[str]]:
        """Get DNS records for domain"""
        try:
            await self.rate_limiters["dns"].acquire()
            
            records = {}
            
            for record_type in self.dns_record_types:
                try:
                    answers = dns.resolver.resolve(domain, record_type)
                    records[record_type] = [str(answer) for answer in answers]
                except (dns.resolver.NXDOMAIN, dns.resolver.NoAnswer):
                    records[record_type] = []
                except Exception as e:
                    logger.warning(f"DNS query error for {domain} {record_type}: {e}")
                    records[record_type] = []
            
            return records
            
        except Exception as e:
            logger.error(f"DNS records error for {domain}: {e}")
            return {}
    
    async def _get_whois_info(self, domain: str) -> Dict[str, Any]:
        """Get WHOIS information for domain"""
        try:
            await self.rate_limiters["whois"].acquire()
            
            # Use python-whois library
            try:
                import whois
                w = whois.whois(domain)
                
                return {
                    "registrar": w.registrar,
                    "creation_date": w.creation_date[0] if isinstance(w.creation_date, list) else w.creation_date,
                    "expiration_date": w.expiration_date[0] if isinstance(w.expiration_date, list) else w.expiration_date,
                    "name_servers": w.name_servers if w.name_servers else [],
                    "status": w.status,
                    "emails": w.emails if w.emails else [],
                    "org": w.org,
                    "country": w.country
                }
                
            except ImportError:
                # Fallback to basic implementation
                return await self._basic_whois_lookup(domain)
                
        except Exception as e:
            logger.error(f"WHOIS error for {domain}: {e}")
            return {}
    
    async def _basic_whois_lookup(self, domain: str) -> Dict[str, Any]:
        """Basic WHOIS lookup using socket"""
        try:
            # Simple WHOIS implementation
            whois_server = "whois.internic.net"
            port = 43
            
            # Connect to WHOIS server
            sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
            sock.settimeout(10)
            sock.connect((whois_server, port))
            
            # Send query
            sock.send(f"{domain}\r\n".encode())
            
            # Receive response
            response = b""
            while True:
                data = sock.recv(4096)
                if not data:
                    break
                response += data
            
            sock.close()
            
            # Parse basic information from response
            response_text = response.decode('utf-8', errors='ignore')
            
            return {
                "raw_response": response_text,
                "registrar": None,  # Would need parsing
                "creation_date": None,
                "expiration_date": None,
                "name_servers": [],
                "status": None
            }
            
        except Exception as e:
            logger.error(f"Basic WHOIS lookup error for {domain}: {e}")
            return {}
    
    async def _get_ssl_info(self, domain: str) -> Dict[str, Any]:
        """Get SSL certificate information"""
        try:
            await self.rate_limiters["ssl"].acquire()
            
            # Create SSL context
            context = ssl.create_default_context()
            
            # Connect and get certificate
            with socket.create_connection((domain, 443), timeout=10) as sock:
                with context.wrap_socket(sock, server_hostname=domain) as ssock:
                    cert = ssock.getpeercert()
                    
                    return {
                        "subject": dict(x[0] for x in cert.get('subject', [])),
                        "issuer": dict(x[0] for x in cert.get('issuer', [])),
                        "version": cert.get('version'),
                        "serial_number": cert.get('serialNumber'),
                        "not_before": cert.get('notBefore'),
                        "not_after": cert.get('notAfter'),
                        "san": cert.get('subjectAltName', []),
                        "signature_algorithm": cert.get('signatureAlgorithm')
                    }
                    
        except Exception as e:
            logger.error(f"SSL info error for {domain}: {e}")
            return {}
    
    async def _find_subdomains(self, domain: str) -> List[str]:
        """Find subdomains using various techniques"""
        try:
            subdomains = set()
            
            # Common subdomain prefixes
            common_prefixes = [
                'www', 'mail', 'ftp', 'admin', 'api', 'blog', 'dev', 'test',
                'staging', 'cdn', 'static', 'assets', 'img', 'images',
                'shop', 'store', 'support', 'help', 'docs', 'wiki'
            ]
            
            # Test common subdomains
            for prefix in common_prefixes:
                subdomain = f"{prefix}.{domain}"
                try:
                    dns.resolver.resolve(subdomain, 'A')
                    subdomains.add(subdomain)
                except:
                    pass
            
            # Certificate Transparency logs (simplified)
            # In a full implementation, you would query CT logs
            
            return list(subdomains)
            
        except Exception as e:
            logger.error(f"Subdomain enumeration error for {domain}: {e}")
            return []
    
    async def _detect_technologies(self, domain: str) -> List[str]:
        """Detect technologies used by the website"""
        try:
            technologies = []
            
            # Make HTTP request to analyze headers and content
            url = f"https://{domain}"
            
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get(url, timeout=10) as response:
                        headers = response.headers
                        content = await response.text()
                        
                        # Analyze server header
                        server = headers.get('Server', '')
                        if 'nginx' in server.lower():
                            technologies.append('Nginx')
                        elif 'apache' in server.lower():
                            technologies.append('Apache')
                        elif 'cloudflare' in server.lower():
                            technologies.append('Cloudflare')
                        
                        # Analyze X-Powered-By header
                        powered_by = headers.get('X-Powered-By', '')
                        if powered_by:
                            technologies.append(powered_by)
                        
                        # Analyze content for common frameworks
                        content_lower = content.lower()
                        if 'wordpress' in content_lower:
                            technologies.append('WordPress')
                        elif 'drupal' in content_lower:
                            technologies.append('Drupal')
                        elif 'joomla' in content_lower:
                            technologies.append('Joomla')
                        
                        # Check for JavaScript frameworks
                        if 'react' in content_lower:
                            technologies.append('React')
                        elif 'angular' in content_lower:
                            technologies.append('Angular')
                        elif 'vue' in content_lower:
                            technologies.append('Vue.js')
                        
                except:
                    pass
            
            return technologies
            
        except Exception as e:
            logger.error(f"Technology detection error for {domain}: {e}")
            return []
    
    async def _get_ip_geolocation(self, ip: str) -> Dict[str, Any]:
        """Get IP geolocation information"""
        try:
            await self.rate_limiters["geolocation"].acquire()
            
            # Use free IP geolocation service
            url = f"http://ip-api.com/json/{ip}"
            
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        data = await response.json()
                        
                        return {
                            "country": data.get("country"),
                            "country_code": data.get("countryCode"),
                            "region": data.get("regionName"),
                            "city": data.get("city"),
                            "zip": data.get("zip"),
                            "lat": data.get("lat"),
                            "lon": data.get("lon"),
                            "timezone": data.get("timezone"),
                            "isp": data.get("isp"),
                            "org": data.get("org"),
                            "as": data.get("as"),
                            "coordinates": {
                                "latitude": data.get("lat"),
                                "longitude": data.get("lon")
                            }
                        }
            
            return {}
            
        except Exception as e:
            logger.error(f"IP geolocation error for {ip}: {e}")
            return {}
    
    async def _get_ip_whois(self, ip: str) -> Dict[str, Any]:
        """Get WHOIS information for IP address"""
        try:
            await self.rate_limiters["whois"].acquire()
            
            # Use ipwhois library if available
            try:
                from ipwhois import IPWhois
                obj = IPWhois(ip)
                result = obj.lookup_rdap()
                
                return {
                    "asn": result.get("asn"),
                    "asn_description": result.get("asn_description"),
                    "network": result.get("network", {}).get("cidr"),
                    "country": result.get("network", {}).get("country"),
                    "org": result.get("network", {}).get("name")
                }
                
            except ImportError:
                # Fallback implementation
                return {}
                
        except Exception as e:
            logger.error(f"IP WHOIS error for {ip}: {e}")
            return {}
    
    async def _scan_ports(self, ip: str) -> Dict[str, Any]:
        """Basic port scan for common ports"""
        try:
            open_ports = []
            services = {}
            
            # Scan common ports
            for port in self.common_ports:
                try:
                    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                    sock.settimeout(2)
                    result = sock.connect_ex((ip, port))
                    
                    if result == 0:
                        open_ports.append(port)
                        
                        # Try to identify service
                        service = self._identify_service(port)
                        if service:
                            services[port] = service
                    
                    sock.close()
                    
                except Exception:
                    pass
            
            return {
                "open_ports": open_ports,
                "services": services,
                "total_scanned": len(self.common_ports)
            }
            
        except Exception as e:
            logger.error(f"Port scan error for {ip}: {e}")
            return {}
    
    def _identify_service(self, port: int) -> Optional[str]:
        """Identify service running on port"""
        
        service_map = {
            21: "FTP",
            22: "SSH",
            23: "Telnet",
            25: "SMTP",
            53: "DNS",
            80: "HTTP",
            110: "POP3",
            143: "IMAP",
            443: "HTTPS",
            993: "IMAPS",
            995: "POP3S",
            1433: "MSSQL",
            3306: "MySQL",
            3389: "RDP",
            5432: "PostgreSQL",
            5900: "VNC",
            8080: "HTTP-Alt",
            8443: "HTTPS-Alt"
        }
        
        return service_map.get(port)
    
    async def _get_reverse_dns(self, ip: str) -> Optional[str]:
        """Get reverse DNS for IP address"""
        try:
            hostname = socket.gethostbyaddr(ip)[0]
            return hostname
        except Exception:
            return None
    
    async def _check_ip_reputation(self, ip: str) -> Optional[str]:
        """Check IP reputation (placeholder)"""
        # This would integrate with reputation services
        # For now, return neutral
        return "neutral"
    
    async def _analyze_domain_data(self, domain_info: DomainInfo) -> Dict[str, Any]:
        """Analyze domain data for insights"""
        
        analysis = {
            "security_score": 0.0,
            "trust_indicators": [],
            "risk_factors": [],
            "recommendations": [],
            "infrastructure_analysis": {}
        }
        
        # SSL analysis
        if domain_info.ssl_info:
            analysis["trust_indicators"].append("SSL certificate present")
            analysis["security_score"] += 0.3
        else:
            analysis["risk_factors"].append("No SSL certificate")
        
        # Age analysis
        if domain_info.creation_date:
            age = datetime.now() - domain_info.creation_date
            if age.days > 365:
                analysis["trust_indicators"].append("Domain older than 1 year")
                analysis["security_score"] += 0.2
        
        # Technology analysis
        if domain_info.technologies:
            analysis["infrastructure_analysis"]["technologies"] = domain_info.technologies
        
        # Subdomain analysis
        if len(domain_info.subdomains) > 5:
            analysis["infrastructure_analysis"]["subdomain_count"] = "high"
        
        return analysis
    
    async def _analyze_ip_data(self, ip_info: IPInfo) -> Dict[str, Any]:
        """Analyze IP data for insights"""
        
        analysis = {
            "risk_score": 0.0,
            "geographic_analysis": {},
            "network_analysis": {},
            "service_analysis": {},
            "recommendations": []
        }
        
        # Geographic analysis
        if ip_info.country:
            analysis["geographic_analysis"]["country"] = ip_info.country
            analysis["geographic_analysis"]["city"] = ip_info.city
        
        # Service analysis
        if ip_info.ports:
            analysis["service_analysis"]["open_ports"] = len(ip_info.ports)
            analysis["service_analysis"]["services"] = list(ip_info.services.values())
            
            # Check for risky services
            risky_ports = [21, 23, 135, 139, 445]
            if any(port in ip_info.ports for port in risky_ports):
                analysis["risk_score"] += 0.3
                analysis["recommendations"].append("Review open ports for security risks")
        
        # Reputation analysis
        if ip_info.reputation == "malicious":
            analysis["risk_score"] += 0.5
        
        return analysis
    
    async def _analyze_infrastructure(self, data: Any) -> Dict[str, Any]:
        """Analyze infrastructure data"""
        return {
            "infrastructure_type": "unknown",
            "complexity": "medium",
            "security_posture": "unknown"
        }
    
    async def _general_technical_analysis(self, data: Any) -> Dict[str, Any]:
        """General technical analysis"""
        return {
            "analysis_type": "general",
            "data_type": type(data).__name__,
            "insights": []
        }

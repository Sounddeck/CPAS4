
"""
Media Intelligence (MEDIAINT)
Reverse image search, metadata extraction, and media analysis
"""

import asyncio
import json
import hashlib
import base64
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
from dataclasses import dataclass
from pathlib import Path
import tempfile
import os

import aiohttp
from loguru import logger
from PIL import Image
from PIL.ExifTags import TAGS

from .base import OSINTBase


@dataclass
class ImageMetadata:
    """Image metadata structure"""
    filename: str
    file_size: int
    dimensions: Tuple[int, int]
    format: str
    mode: str
    exif_data: Dict[str, Any]
    creation_date: Optional[datetime]
    gps_coordinates: Optional[Tuple[float, float]]
    camera_info: Optional[Dict[str, str]]
    hash_md5: str
    hash_sha256: str


@dataclass
class ReverseImageResult:
    """Reverse image search result"""
    source: str
    url: str
    title: Optional[str]
    description: Optional[str]
    similarity: Optional[float]
    dimensions: Optional[Tuple[int, int]]
    first_seen: Optional[datetime]


class MediaIntelligence(OSINTBase):
    """
    Media Intelligence gathering
    Reverse image search, metadata extraction, and media analysis
    """
    
    def __init__(self):
        super().__init__()
        
        # Supported image formats
        self.supported_formats = ['.jpg', '.jpeg', '.png', '.gif', '.bmp', '.tiff', '.webp']
        
        # Reverse image search engines
        self.search_engines = {
            "google": "https://www.google.com/searchbyimage",
            "yandex": "https://yandex.com/images/search",
            "tineye": "https://tineye.com/search",
            "bing": "https://www.bing.com/images/search"
        }
        
        # Rate limiting
        self.setup_rate_limiters()
    
    def setup_rate_limiters(self):
        """Setup rate limiters for media services"""
        self.get_rate_limiter("google", 10, 60)    # 10 requests per minute
        self.get_rate_limiter("yandex", 20, 60)    # 20 requests per minute
        self.get_rate_limiter("tineye", 150, 3600) # 150 requests per hour
        self.get_rate_limiter("bing", 15, 60)      # 15 requests per minute
    
    async def search(self, query: str, **kwargs) -> Dict[str, Any]:
        """
        Main search method for media intelligence
        Supports image URLs and file paths
        """
        try:
            search_type = kwargs.get("type", "reverse_image")
            
            if search_type == "reverse_image":
                return await self.reverse_image_search(query)
            elif search_type == "metadata":
                return await self.extract_metadata(query)
            elif search_type == "similarity":
                return await self.find_similar_images(query)
            else:
                return {
                    "success": False,
                    "error": "Invalid search type",
                    "query": query
                }
                
        except Exception as e:
            logger.error(f"Media intelligence search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "query": query
            }
    
    async def analyze(self, data: Any, **kwargs) -> Dict[str, Any]:
        """Analyze media data for patterns and insights"""
        try:
            analysis_type = kwargs.get("type", "general")
            
            if analysis_type == "metadata":
                return await self._analyze_metadata(data)
            elif analysis_type == "reverse_search":
                return await self._analyze_reverse_search_results(data)
            elif analysis_type == "forensic":
                return await self._forensic_analysis(data)
            else:
                return await self._general_media_analysis(data)
                
        except Exception as e:
            logger.error(f"Media analysis error: {e}")
            return {
                "success": False,
                "error": str(e)
            }
    
    async def reverse_image_search(self, image_source: str) -> Dict[str, Any]:
        """
        Perform reverse image search across multiple engines
        """
        try:
            logger.info(f"Performing reverse image search: {image_source}")
            
            # Download or load image
            image_path = await self._prepare_image(image_source)
            if not image_path:
                return {
                    "success": False,
                    "error": "Could not load image",
                    "source": image_source
                }
            
            # Extract metadata first
            metadata = await self.extract_metadata(image_path)
            
            # Perform reverse search on multiple engines
            search_tasks = [
                self._search_google_images(image_path),
                self._search_yandex_images(image_path),
                self._search_tineye(image_path),
                self._search_bing_images(image_path)
            ]
            
            results = await asyncio.gather(*search_tasks, return_exceptions=True)
            
            # Process results
            all_results = []
            for i, result in enumerate(results):
                if not isinstance(result, Exception) and result:
                    all_results.extend(result)
            
            # Analyze results
            analysis = await self._analyze_reverse_search_results(all_results)
            
            # Clean up temporary file
            if image_path != image_source and os.path.exists(image_path):
                os.unlink(image_path)
            
            self.log_osint_activity("reverse_image_search", image_source, f"found {len(all_results)} results")
            
            return {
                "success": True,
                "image_source": image_source,
                "metadata": metadata.get("metadata") if metadata.get("success") else {},
                "results": all_results,
                "total_results": len(all_results),
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Reverse image search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_source": image_source
            }
    
    async def extract_metadata(self, image_source: str) -> Dict[str, Any]:
        """
        Extract comprehensive metadata from image
        """
        try:
            logger.info(f"Extracting metadata from: {image_source}")
            
            # Prepare image
            image_path = await self._prepare_image(image_source)
            if not image_path:
                return {
                    "success": False,
                    "error": "Could not load image",
                    "source": image_source
                }
            
            # Extract metadata
            metadata = await self._extract_image_metadata(image_path)
            
            # Perform additional analysis
            analysis = await self._analyze_metadata(metadata)
            
            # Clean up temporary file
            if image_path != image_source and os.path.exists(image_path):
                os.unlink(image_path)
            
            self.log_osint_activity("metadata_extraction", image_source, "completed")
            
            return {
                "success": True,
                "image_source": image_source,
                "metadata": metadata.__dict__ if metadata else {},
                "analysis": analysis,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_source": image_source
            }
    
    async def find_similar_images(self, image_source: str) -> Dict[str, Any]:
        """
        Find similar images using various techniques
        """
        try:
            logger.info(f"Finding similar images for: {image_source}")
            
            # This would implement perceptual hashing and similarity search
            # For now, return placeholder
            
            return {
                "success": True,
                "image_source": image_source,
                "similar_images": [],
                "similarity_threshold": 0.8,
                "timestamp": datetime.now().isoformat()
            }
            
        except Exception as e:
            logger.error(f"Similar image search error: {e}")
            return {
                "success": False,
                "error": str(e),
                "image_source": image_source
            }
    
    async def _prepare_image(self, image_source: str) -> Optional[str]:
        """
        Prepare image for analysis (download if URL, validate if file)
        """
        try:
            if image_source.startswith(('https://upload.wikimedia.org/wikipedia/commons/thumb/e/eb/Crime_scene_shoeprint_oblique.jpg/250px-Crime_scene_shoeprint_oblique.jpg', 'https://upload.wikimedia.org/wikipedia/commons/d/d0/Major_topics_of_pathology_informatics.png')):
                # Download image from URL
                return await self._download_image(image_source)
            elif os.path.exists(image_source):
                # Local file
                return image_source
            else:
                logger.error(f"Invalid image source: {image_source}")
                return None
                
        except Exception as e:
            logger.error(f"Image preparation error: {e}")
            return None
    
    async def _download_image(self, url: str) -> Optional[str]:
        """Download image from URL to temporary file"""
        try:
            async with aiohttp.ClientSession() as session:
                async with session.get(url) as response:
                    if response.status == 200:
                        # Create temporary file
                        suffix = Path(url).suffix or '.jpg'
                        with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp_file:
                            content = await response.read()
                            tmp_file.write(content)
                            return tmp_file.name
            
            return None
            
        except Exception as e:
            logger.error(f"Image download error: {e}")
            return None
    
    async def _extract_image_metadata(self, image_path: str) -> Optional[ImageMetadata]:
        """Extract comprehensive metadata from image file"""
        try:
            with Image.open(image_path) as img:
                # Basic image info
                file_size = os.path.getsize(image_path)
                dimensions = img.size
                format = img.format
                mode = img.mode
                
                # Extract EXIF data
                exif_data = {}
                if hasattr(img, '_getexif') and img._getexif():
                    exif = img._getexif()
                    for tag_id, value in exif.items():
                        tag = TAGS.get(tag_id, tag_id)
                        exif_data[tag] = value
                
                # Parse specific EXIF fields
                creation_date = self._parse_creation_date(exif_data)
                gps_coordinates = self._parse_gps_coordinates(exif_data)
                camera_info = self._parse_camera_info(exif_data)
                
                # Calculate hashes
                with open(image_path, 'rb') as f:
                    content = f.read()
                    hash_md5 = hashlib.md5(content).hexdigest()
                    hash_sha256 = hashlib.sha256(content).hexdigest()
                
                return ImageMetadata(
                    filename=os.path.basename(image_path),
                    file_size=file_size,
                    dimensions=dimensions,
                    format=format,
                    mode=mode,
                    exif_data=exif_data,
                    creation_date=creation_date,
                    gps_coordinates=gps_coordinates,
                    camera_info=camera_info,
                    hash_md5=hash_md5,
                    hash_sha256=hash_sha256
                )
                
        except Exception as e:
            logger.error(f"Metadata extraction error: {e}")
            return None
    
    def _parse_creation_date(self, exif_data: Dict[str, Any]) -> Optional[datetime]:
        """Parse creation date from EXIF data"""
        try:
            date_fields = ['DateTime', 'DateTimeOriginal', 'DateTimeDigitized']
            
            for field in date_fields:
                if field in exif_data:
                    date_str = str(exif_data[field])
                    return datetime.strptime(date_str, '%Y:%m:%d %H:%M:%S')
            
            return None
            
        except Exception:
            return None
    
    def _parse_gps_coordinates(self, exif_data: Dict[str, Any]) -> Optional[Tuple[float, float]]:
        """Parse GPS coordinates from EXIF data"""
        try:
            if 'GPSInfo' not in exif_data:
                return None
            
            gps_info = exif_data['GPSInfo']
            
            # Extract latitude
            if 2 in gps_info and 1 in gps_info:
                lat_ref = gps_info[1]
                lat_data = gps_info[2]
                latitude = self._convert_gps_coordinate(lat_data)
                if lat_ref == 'S':
                    latitude = -latitude
            else:
                return None
            
            # Extract longitude
            if 4 in gps_info and 3 in gps_info:
                lon_ref = gps_info[3]
                lon_data = gps_info[4]
                longitude = self._convert_gps_coordinate(lon_data)
                if lon_ref == 'W':
                    longitude = -longitude
            else:
                return None
            
            return (latitude, longitude)
            
        except Exception:
            return None
    
    def _convert_gps_coordinate(self, coord_data) -> float:
        """Convert GPS coordinate from EXIF format to decimal degrees"""
        degrees = float(coord_data[0])
        minutes = float(coord_data[1])
        seconds = float(coord_data[2])
        
        return degrees + (minutes / 60.0) + (seconds / 3600.0)
    
    def _parse_camera_info(self, exif_data: Dict[str, Any]) -> Optional[Dict[str, str]]:
        """Parse camera information from EXIF data"""
        try:
            camera_info = {}
            
            camera_fields = {
                'Make': 'make',
                'Model': 'model',
                'Software': 'software',
                'LensModel': 'lens_model',
                'FocalLength': 'focal_length',
                'FNumber': 'f_number',
                'ExposureTime': 'exposure_time',
                'ISOSpeedRatings': 'iso'
            }
            
            for exif_key, info_key in camera_fields.items():
                if exif_key in exif_data:
                    camera_info[info_key] = str(exif_data[exif_key])
            
            return camera_info if camera_info else None
            
        except Exception:
            return None
    
    async def _search_google_images(self, image_path: str) -> List[ReverseImageResult]:
        """Search Google Images (requires implementation)"""
        try:
            await self.rate_limiters["google"].acquire()
            
            # Google reverse image search would require complex implementation
            # involving uploading image and parsing results
            # For now, return mock data
            
            return [
                ReverseImageResult(
                    source="google",
                    url="https://i.ytimg.com/vi/Sh1vpbzSDJU/maxresdefault.jpg",
                    title="Similar Image Found",
                    description="A similar image found on Google",
                    similarity=0.85,
                    dimensions=(800, 600),
                    first_seen=datetime.now()
                )
            ]
            
        except Exception as e:
            logger.error(f"Google image search error: {e}")
            return []
    
    async def _search_yandex_images(self, image_path: str) -> List[ReverseImageResult]:
        """Search Yandex Images"""
        try:
            await self.rate_limiters["yandex"].acquire()
            
            # Yandex reverse image search implementation
            # Mock data for now
            
            return []
            
        except Exception as e:
            logger.error(f"Yandex image search error: {e}")
            return []
    
    async def _search_tineye(self, image_path: str) -> List[ReverseImageResult]:
        """Search TinEye (requires API key)"""
        try:
            await self.rate_limiters["tineye"].acquire()
            
            # TinEye API implementation would go here
            # Mock data for now
            
            return []
            
        except Exception as e:
            logger.error(f"TinEye search error: {e}")
            return []
    
    async def _search_bing_images(self, image_path: str) -> List[ReverseImageResult]:
        """Search Bing Images"""
        try:
            await self.rate_limiters["bing"].acquire()
            
            # Bing reverse image search implementation
            # Mock data for now
            
            return []
            
        except Exception as e:
            logger.error(f"Bing image search error: {e}")
            return []
    
    async def _analyze_metadata(self, metadata: ImageMetadata) -> Dict[str, Any]:
        """Analyze image metadata for insights"""
        
        analysis = {
            "privacy_risks": [],
            "authenticity_indicators": [],
            "technical_analysis": {},
            "recommendations": []
        }
        
        if not metadata:
            return analysis
        
        # GPS location analysis
        if metadata.gps_coordinates:
            analysis["privacy_risks"].append("GPS coordinates embedded in image")
            analysis["recommendations"].append("Remove location data before sharing")
        
        # Camera information analysis
        if metadata.camera_info:
            analysis["technical_analysis"]["camera_detected"] = True
            analysis["technical_analysis"]["camera_info"] = metadata.camera_info
            
            # Check for professional equipment
            if metadata.camera_info.get("make") in ["Canon", "Nikon", "Sony"]:
                analysis["authenticity_indicators"].append("Professional camera equipment detected")
        
        # Creation date analysis
        if metadata.creation_date:
            age_days = (datetime.now() - metadata.creation_date).days
            analysis["technical_analysis"]["image_age_days"] = age_days
            
            if age_days < 1:
                analysis["authenticity_indicators"].append("Recently created image")
            elif age_days > 365:
                analysis["authenticity_indicators"].append("Older image (>1 year)")
        
        # File size and quality analysis
        if metadata.file_size > 5 * 1024 * 1024:  # 5MB
            analysis["technical_analysis"]["high_quality"] = True
        
        # Dimension analysis
        width, height = metadata.dimensions
        if width > 3000 or height > 3000:
            analysis["technical_analysis"]["high_resolution"] = True
        
        return analysis
    
    async def _analyze_reverse_search_results(self, results: List[ReverseImageResult]) -> Dict[str, Any]:
        """Analyze reverse search results for patterns"""
        
        analysis = {
            "total_matches": len(results),
            "sources": list(set(result.source for result in results)),
            "earliest_appearance": None,
            "most_similar": None,
            "distribution_analysis": {},
            "authenticity_assessment": "unknown"
        }
        
        if not results:
            return analysis
        
        # Find earliest appearance
        dates = [result.first_seen for result in results if result.first_seen]
        if dates:
            analysis["earliest_appearance"] = min(dates).isoformat()
        
        # Find most similar result
        similarities = [result.similarity for result in results if result.similarity]
        if similarities:
            max_similarity = max(similarities)
            most_similar = next(result for result in results if result.similarity == max_similarity)
            analysis["most_similar"] = {
                "url": most_similar.url,
                "similarity": max_similarity,
                "source": most_similar.source
            }
        
        # Source distribution
        source_counts = {}
        for result in results:
            source_counts[result.source] = source_counts.get(result.source, 0) + 1
        analysis["distribution_analysis"] = source_counts
        
        # Authenticity assessment
        if len(results) == 0:
            analysis["authenticity_assessment"] = "unique"
        elif len(results) < 5:
            analysis["authenticity_assessment"] = "rare"
        elif len(results) < 20:
            analysis["authenticity_assessment"] = "common"
        else:
            analysis["authenticity_assessment"] = "widespread"
        
        return analysis
    
    async def _forensic_analysis(self, data: Any) -> Dict[str, Any]:
        """Perform forensic analysis on media data"""
        
        return {
            "analysis_type": "forensic",
            "tampering_indicators": [],
            "compression_analysis": {},
            "noise_analysis": {},
            "authenticity_score": 0.5,
            "recommendations": [
                "Verify source authenticity",
                "Cross-reference with other sources",
                "Check for digital manipulation signs"
            ]
        }
    
    async def _general_media_analysis(self, data: Any) -> Dict[str, Any]:
        """General media analysis"""
        
        return {
            "analysis_type": "general",
            "data_type": type(data).__name__,
            "insights": [],
            "recommendations": []
        }

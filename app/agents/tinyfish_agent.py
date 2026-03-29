"""
TinyFish Data Agent
Fetches article content, images, and metadata via TinyFish API
"""
import httpx
from typing import Dict, Any, List, Optional
from .base_agent import BaseAgent


class TinyFishDataAgent(BaseAgent):
    """Agent responsible for fetching article data via TinyFish API"""
    
    def __init__(self, api_key: Optional[str] = None, base_url: str = "https://api.tinyfish.io/v1"):
        super().__init__("TinyFishDataAgent")
        self.api_key = api_key
        self.base_url = base_url
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Fetch article content and metadata from TinyFish API
        
        Expected context:
            - article_url: URL of the article to process
            OR
            - topic: Topic to search for articles
        
        Returns:
            - article_data: Complete article data from TinyFish
            - extracted_images: List of image URLs from article
            - key_points: Extracted key points
            - entities: Detected entities
        """
        self.log_start("Fetching article data from TinyFish API")
        
        try:
            article_url = context.get('article_url')
            topic = context.get('topic')
            
            if article_url:
                # Fetch specific article
                article_data = await self._fetch_article(article_url)
            elif topic:
                # Search for articles and use the first one
                search_results = await self._search_articles(topic)
                if not search_results:
                    # If no articles found, create synthetic data from topic
                    self.log_progress(f"No articles found for '{topic}', creating synthetic data")
                    article_data = self._create_synthetic_article(topic, context)
                else:
                    article_data = search_results[0]
            else:
                raise ValueError("Either 'article_url' or 'topic' must be provided")
            
            # Extract relevant data
            result = {
                'article_data': article_data,
                'title': article_data.get('title', topic),
                'summary': article_data.get('summary', ''),
                'key_points': article_data.get('key_points', []),
                'entities': article_data.get('entities', {}),
                'topics': article_data.get('topics', []),
                'extracted_images': self._extract_images(article_data),
                'content_sections': article_data.get('content_sections', []),
                'metadata': article_data.get('metadata', {})
            }
            
            self.log_complete(f"Fetched article: {result['title']}")
            self.log_progress(f"Found {len(result['extracted_images'])} images")
            self.log_progress(f"Extracted {len(result['key_points'])} key points")
            
            return result
            
        except Exception as e:
            self.log_error(f"Failed to fetch TinyFish data: {str(e)}")
            # Fallback to synthetic data
            return self._create_synthetic_article(context.get('topic', 'Unknown Topic'), context)
    
    async def _fetch_article(self, url: str) -> Dict[str, Any]:
        """Fetch article from TinyFish API"""
        # TODO: Replace with actual TinyFish API call when available
        # For now, simulate the API response
        self.log_progress(f"Fetching article from URL: {url}")
        
        async with httpx.AsyncClient() as client:
            try:
                # Simulated TinyFish API endpoint
                response = await client.post(
                    f"{self.base_url}/extract",
                    json={"url": url},
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json()
            except Exception as e:
                self.log_error(f"TinyFish API call failed: {str(e)}")
                # Return mock data structure
                return self._create_mock_article_data(url)
    
    async def _search_articles(self, query: str) -> List[Dict[str, Any]]:
        """Search for articles via TinyFish API"""
        # TODO: Replace with actual TinyFish search API
        self.log_progress(f"Searching for articles about: {query}")
        
        async with httpx.AsyncClient() as client:
            try:
                response = await client.get(
                    f"{self.base_url}/search",
                    params={"q": query, "limit": 5},
                    headers={"Authorization": f"Bearer {self.api_key}"} if self.api_key else {},
                    timeout=30.0
                )
                response.raise_for_status()
                return response.json().get('results', [])
            except Exception as e:
                self.log_error(f"TinyFish search failed: {str(e)}")
                return []
    
    def _extract_images(self, article_data: Dict[str, Any]) -> List[Dict[str, str]]:
        """Extract image URLs and metadata from article data"""
        images = article_data.get('images', [])
        
        extracted = []
        for img in images:
            extracted.append({
                'url': img.get('url', ''),
                'caption': img.get('caption', ''),
                'position': img.get('position', 0),
                'type': img.get('type', 'inline')
            })
        
        return extracted
    
    def _create_synthetic_article(self, topic: str, context: Dict[str, Any]) -> Dict[str, Any]:
        """Create synthetic article data when TinyFish is unavailable"""
        self.log_progress(f"Creating synthetic article data for: {topic}")
        
        key_points = context.get('key_points', [])
        duration = context.get('duration', 60)
        
        return {
            'article_data': {
                'article_id': f"synthetic_{topic.replace(' ', '_')}",
                'title': topic,
                'summary': f"An educational video about {topic}",
                'topics': [topic],
                'key_points': key_points if key_points else [
                    f"Introduction to {topic}",
                    f"Key concepts of {topic}",
                    f"Applications of {topic}"
                ],
                'entities': {
                    'people': [],
                    'organizations': [],
                    'locations': []
                },
                'content_sections': [],
                'images': [],
                'metadata': {
                    'word_count': duration * 3,  # Approximate
                    'reading_time': duration // 60,
                    'language': 'en'
                }
            },
            'title': topic,
            'summary': f"An educational video about {topic}",
            'key_points': key_points if key_points else [
                f"Introduction to {topic}",
                f"Key concepts of {topic}",
                f"Applications of {topic}"
            ],
            'entities': {},
            'topics': [topic],
            'extracted_images': [],
            'content_sections': [],
            'metadata': {}
        }
    
    def _create_mock_article_data(self, url: str) -> Dict[str, Any]:
        """Create mock article data structure"""
        return {
            'article_id': 'mock_article',
            'title': 'Sample Article',
            'url': url,
            'summary': 'This is a sample article for testing',
            'topics': ['technology', 'AI'],
            'key_points': [
                'First key point',
                'Second key point',
                'Third key point'
            ],
            'entities': {
                'people': [],
                'organizations': [],
                'locations': []
            },
            'content_sections': [],
            'images': [],
            'metadata': {
                'word_count': 500,
                'reading_time': 3,
                'language': 'en'
            }
        }

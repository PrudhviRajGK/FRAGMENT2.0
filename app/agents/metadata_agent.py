"""
AI Metadata Generator Agent
Generates titles, descriptions, and hashtags for social media
"""
import json
import openai
from typing import Dict, Any, List
from .base_agent import BaseAgent


class MetadataAgent(BaseAgent):
    """Generates optimized metadata for video publishing"""
    
    def __init__(self, api_key: str):
        super().__init__("MetadataAgent")
        self.client = openai.OpenAI(api_key=api_key)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate metadata for video
        
        Expected context:
            - title: Article title
            - script: Video script
            - category: Content category
        
        Returns:
            - metadata: Generated metadata for all platforms
        """
        self.log_start("Generating video metadata")
        
        try:
            title = context.get('title', '')
            script = context.get('script', {})
            category = context.get('category', 'business')
            
            # Generate metadata
            metadata = self._generate_metadata(title, script, category)
            
            self.log_complete("Metadata generated for all platforms")
            
            return {'metadata': metadata}
            
        except Exception as e:
            self.log_error(f"Metadata generation failed: {str(e)}")
            raise
    
    def _generate_metadata(
        self,
        title: str,
        script: Dict[str, Any],
        category: str
    ) -> Dict[str, Any]:
        """Generate metadata using GPT-4"""
        
        script_text = self._extract_script_text(script)
        
        prompt = f"""Generate viral social media metadata for this business news video:

Original Title: {title}
Script: {script_text}
Category: {category}

Generate:

1. YouTube Title (max 100 chars)
   - Include emoji
   - Make it clickable
   - Include key number/fact
   Example: "This AI Startup Just Raised $200M 😳"

2. YouTube Description (200-300 chars)
   - Brief summary
   - Include call to action
   - Mention source (Economic Times)

3. Hashtags (10-15 relevant hashtags)
   - Mix of trending and specific
   - Include #Shorts #BusinessNews #EconomicTimes

4. Instagram Caption (shorter, more casual)
   - Include emojis
   - 2-3 lines max

5. LinkedIn Post (professional tone)
   - 3-4 lines
   - Professional hashtags

Output as JSON:
{{
  "youtube": {{
    "title": "...",
    "description": "...",
    "tags": ["tag1", "tag2", ...]
  }},
  "instagram": {{
    "caption": "...",
    "hashtags": ["#tag1", "#tag2", ...]
  }},
  "linkedin": {{
    "post": "...",
    "hashtags": ["#tag1", "#tag2", ...]
  }}
}}"""
        
        system_prompt = """You are a social media expert specializing in viral business content.
Create metadata that maximizes engagement and reach.
Use emojis strategically.
Include trending hashtags.
Make titles clickable but not clickbait.
Output valid JSON only."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.7,
            max_tokens=1000
        )
        
        metadata_text = response.choices[0].message.content
        
        # Extract JSON
        try:
            metadata = json.loads(metadata_text)
        except:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', metadata_text, re.DOTALL)
            if json_match:
                metadata = json.loads(json_match.group(1))
            else:
                metadata = self._create_fallback_metadata(title)
        
        return metadata
    
    def _extract_script_text(self, script: Dict[str, Any]) -> str:
        """Extract text from script"""
        if 'segments' in script:
            return ' '.join([seg.get('text', '') for seg in script['segments']])
        
        parts = []
        for key in ['hook', 'news', 'why_matters', 'key_fact', 'ending']:
            if key in script:
                parts.append(script[key])
        
        return ' '.join(parts)
    
    def _create_fallback_metadata(self, title: str) -> Dict[str, Any]:
        """Create fallback metadata if AI generation fails"""
        return {
            "youtube": {
                "title": f"{title} 📈",
                "description": f"Latest business news from Economic Times. {title}\n\n#Shorts #BusinessNews #EconomicTimes",
                "tags": ["business", "news", "economic times", "india", "startup", "tech"]
            },
            "instagram": {
                "caption": f"📊 {title}\n\nFollow for daily business updates! 🚀",
                "hashtags": ["#business", "#news", "#startup", "#tech", "#india"]
            },
            "linkedin": {
                "post": f"{title}\n\nStay updated with the latest business developments.\n\nSource: Economic Times",
                "hashtags": ["#Business", "#News", "#India", "#Technology"]
            }
        }

"""
Viral Script Generator Agent
Converts news articles into viral short-form video scripts
"""
import json
import openai
from typing import Dict, Any
from .base_agent import BaseAgent


class ViralScriptAgent(BaseAgent):
    """Generates viral scripts optimized for YouTube Shorts, Instagram Reels"""
    
    def __init__(self, api_key: str):
        super().__init__("ViralScriptAgent")
        self.client = openai.OpenAI(api_key=api_key)
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate viral script from article
        
        Expected context:
            - title: Article title
            - content: Article content
            - summary: Article summary
            - category: Article category
        
        Returns:
            - script: Viral video script with segments
        """
        self.log_start("Generating viral script from article")
        
        try:
            title = context.get('title', '')
            content = context.get('content', '')
            summary = context.get('summary', '')
            category = context.get('category', 'business')
            
            # Generate viral script
            script = self._generate_viral_script(
                title=title,
                content=content,
                summary=summary,
                category=category
            )
            
            self.log_complete(f"Generated viral script with {len(script['segments'])} segments")
            
            return {'script': script}
            
        except Exception as e:
            self.log_error(f"Viral script generation failed: {str(e)}")
            raise
    
    def _generate_viral_script(
        self,
        title: str,
        content: str,
        summary: str,
        category: str
    ) -> Dict[str, Any]:
        """Generate viral script using GPT-4"""
        
        prompt = f"""Convert this Economic Times article into a viral 30-45 second video script.

Article Title: {title}
Summary: {summary}
Content: {content[:1000]}
Category: {category}

Create a script with this EXACT structure:

1. HOOK (3 seconds) - Start with something shocking/attention-grabbing
2. THE NEWS (10 seconds) - What happened
3. WHY IT MATTERS (10 seconds) - Impact and significance
4. KEY FACT (8 seconds) - Most important data point or insight
5. ENDING (5 seconds) - Call to action

Requirements:
- Use conversational, energetic language
- Include specific numbers and data
- Make it feel urgent and important
- End with "Follow for more business news"
- Total duration: 30-45 seconds

Output as JSON with BOTH formats:
{{
  "topic": "title",
  "audio_script": [
    {{
      "timestamp": "00:00",
      "text": "narration text for hook",
      "speaker": "narrator_male",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "informative"
    }},
    {{
      "timestamp": "00:03",
      "text": "narration text for news",
      "speaker": "narrator_male",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "informative"
    }},
    {{
      "timestamp": "00:13",
      "text": "narration text for why it matters",
      "speaker": "narrator_male",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "informative"
    }},
    {{
      "timestamp": "00:23",
      "text": "narration text for key fact",
      "speaker": "narrator_male",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "informative"
    }},
    {{
      "timestamp": "00:31",
      "text": "Follow for more business news!",
      "speaker": "narrator_male",
      "speed": 1.0,
      "pitch": 1.0,
      "emotion": "informative"
    }}
  ],
  "visual_script": [
    {{
      "timestamp_start": "00:00",
      "timestamp_end": "00:03",
      "prompt": "Bold text with news headline",
      "negative_prompt": "Avoid abstract"
    }},
    {{
      "timestamp_start": "00:03",
      "timestamp_end": "00:13",
      "prompt": "Article image or related visual",
      "negative_prompt": "Avoid abstract"
    }},
    {{
      "timestamp_start": "00:13",
      "timestamp_end": "00:23",
      "prompt": "Impact visualization",
      "negative_prompt": "Avoid abstract"
    }},
    {{
      "timestamp_start": "00:23",
      "timestamp_end": "00:31",
      "prompt": "Data visualization",
      "negative_prompt": "Avoid abstract"
    }},
    {{
      "timestamp_start": "00:31",
      "timestamp_end": "00:36",
      "prompt": "Call to action screen",
      "negative_prompt": "Avoid abstract"
    }}
  ],
  "segments": [
    {{
      "timestamp_start": "00:00",
      "timestamp_end": "00:03",
      "text": "narration text",
      "visual_description": "what to show",
      "segment_type": "hook"
    }}
  ]
}}"""
        
        system_prompt = """You are a viral content creator specializing in business news shorts.
Your scripts are energetic, data-driven, and optimized for YouTube Shorts and Instagram Reels.
Always start with a hook that makes people stop scrolling.
Use numbers, statistics, and concrete facts.
Keep language simple but impactful.
Output valid JSON only with BOTH audio_script and visual_script arrays."""
        
        response = self.client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": prompt}
            ],
            temperature=0.8,  # Higher for creativity
            max_tokens=1500
        )
        
        script_text = response.choices[0].message.content
        
        # Extract JSON
        try:
            script = json.loads(script_text)
        except:
            import re
            json_match = re.search(r'```json\n(.*?)\n```', script_text, re.DOTALL)
            if json_match:
                script = json.loads(json_match.group(1))
            else:
                # Fallback: create basic structure
                script = self._create_fallback_script(title, summary)
        
        # Ensure all required fields
        if 'audio_script' not in script:
            script['audio_script'] = self._create_audio_script_from_segments(script.get('segments', []))
        
        if 'visual_script' not in script:
            script['visual_script'] = self._create_visual_script_from_segments(script.get('segments', []))
        
        if 'segments' not in script:
            script['segments'] = self._create_segments_from_text(script)
        
        return script
    
    def _create_fallback_script(self, title: str, summary: str) -> Dict[str, Any]:
        """Create fallback script if AI generation fails"""
        audio_script = [
            {
                "timestamp": "00:00",
                "text": f"Breaking: {title[:100]}",
                "speaker": "narrator_male",
                "speed": 1.0,
                "pitch": 1.0,
                "emotion": "informative"
            },
            {
                "timestamp": "00:03",
                "text": summary[:200] if summary else "Here's what you need to know.",
                "speaker": "narrator_male",
                "speed": 1.0,
                "pitch": 1.0,
                "emotion": "informative"
            },
            {
                "timestamp": "00:15",
                "text": "This could change everything in the business world.",
                "speaker": "narrator_male",
                "speed": 1.0,
                "pitch": 1.0,
                "emotion": "informative"
            },
            {
                "timestamp": "00:25",
                "text": "Follow for more business news!",
                "speaker": "narrator_male",
                "speed": 1.0,
                "pitch": 1.0,
                "emotion": "informative"
            }
        ]
        
        visual_script = [
            {
                "timestamp_start": "00:00",
                "timestamp_end": "00:03",
                "prompt": "Bold text with news headline",
                "negative_prompt": "Avoid abstract"
            },
            {
                "timestamp_start": "00:03",
                "timestamp_end": "00:15",
                "prompt": "Article image or related visual",
                "negative_prompt": "Avoid abstract"
            },
            {
                "timestamp_start": "00:15",
                "timestamp_end": "00:25",
                "prompt": "Impact visualization",
                "negative_prompt": "Avoid abstract"
            },
            {
                "timestamp_start": "00:25",
                "timestamp_end": "00:30",
                "prompt": "Call to action screen",
                "negative_prompt": "Avoid abstract"
            }
        ]
        
        segments = [
            {
                "timestamp_start": "00:00",
                "timestamp_end": "00:03",
                "text": f"Breaking: {title[:100]}",
                "visual_description": "Bold text with news headline",
                "segment_type": "hook"
            },
            {
                "timestamp_start": "00:03",
                "timestamp_end": "00:15",
                "text": summary[:200] if summary else "Here's what you need to know.",
                "visual_description": "Article image or related visual",
                "segment_type": "news"
            },
            {
                "timestamp_start": "00:15",
                "timestamp_end": "00:25",
                "text": "This could change everything in the business world.",
                "visual_description": "Impact visualization",
                "segment_type": "why_matters"
            },
            {
                "timestamp_start": "00:25",
                "timestamp_end": "00:30",
                "text": "Follow for more business news!",
                "visual_description": "Call to action screen",
                "segment_type": "ending"
            }
        ]
        
        return {
            "topic": title,
            "audio_script": audio_script,
            "visual_script": visual_script,
            "segments": segments
        }
    
    def _create_audio_script_from_segments(self, segments: list) -> list:
        """Create audio_script from segments"""
        audio_script = []
        for seg in segments:
            audio_script.append({
                "timestamp": seg.get('timestamp_start', '00:00'),
                "text": seg.get('text', ''),
                "speaker": "narrator_male",
                "speed": 1.0,
                "pitch": 1.0,
                "emotion": "informative"
            })
        return audio_script
    
    def _create_visual_script_from_segments(self, segments: list) -> list:
        """Create visual_script from segments"""
        visual_script = []
        for seg in segments:
            visual_script.append({
                "timestamp_start": seg.get('timestamp_start', '00:00'),
                "timestamp_end": seg.get('timestamp_end', '00:05'),
                "prompt": seg.get('visual_description', 'Visual for segment'),
                "negative_prompt": "Avoid abstract or complex designs"
            })
        return visual_script
    
    def _create_segments_from_text(self, script: Dict[str, Any]) -> list:
        """Create segments from script text fields"""
        segments = []
        current_time = 0
        
        segment_map = [
            ('hook', 3, 'hook'),
            ('news', 12, 'news'),
            ('why_matters', 10, 'why_matters'),
            ('key_fact', 8, 'key_fact'),
            ('ending', 5, 'ending'),
        ]
        
        for field, duration, seg_type in segment_map:
            if field in script:
                end_time = current_time + duration
                segments.append({
                    "timestamp_start": f"00:{current_time:02d}",
                    "timestamp_end": f"00:{end_time:02d}",
                    "text": script[field],
                    "visual_description": f"Visual for {seg_type}",
                    "segment_type": seg_type
                })
                current_time = end_time
        
        return segments

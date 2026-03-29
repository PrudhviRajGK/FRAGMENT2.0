"""
Image Generator Agent
Handles hybrid image sourcing: article images + AI generation
"""
from typing import Dict, Any, List
from pathlib import Path
import httpx
from .base_agent import BaseAgent
from imagegen.gen_img_openai_refactored import generate_openai_image, download_image


class ImageGeneratorAgent(BaseAgent):
    """Agent responsible for sourcing and generating images"""
    
    def __init__(self, api_key: str):
        super().__init__("ImageGeneratorAgent")
        self.api_key = api_key
    
    async def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate or source images for video
        
        Expected context:
            - script: Video script with visual_script
            - extracted_images: Images from article
            - images_dir: Output directory
        
        Returns:
            - image_paths: List of generated image paths
        """
        self.log_start("Generating/sourcing images for video")
        
        try:
            script = context['script']
            extracted_images = context.get('extracted_images', [])
            images_dir = Path(context['images_dir'])
            
            visual_script = script.get('visual_script', [])
            image_paths = []
            
            for idx, scene in enumerate(visual_script):
                # Try to use article image first
                if idx < len(extracted_images) and extracted_images[idx]['url']:
                    self.log_progress(f"Using article image for scene {idx}")
                    image_path = await self._download_article_image(
                        extracted_images[idx]['url'],
                        images_dir,
                        idx
                    )
                else:
                    # Generate with DALL-E
                    self.log_progress(f"Generating AI image for scene {idx}")
                    prompt = scene.get('prompt', '')
                    image_path = await self._generate_ai_image(
                        prompt,
                        images_dir,
                        idx
                    )
                
                image_paths.append(image_path)
            
            self.log_complete(f"Processed {len(image_paths)} images")
            return {'image_paths': image_paths}
            
        except Exception as e:
            self.log_error(f"Image generation failed: {str(e)}")
            raise

    
    async def _download_article_image(
        self,
        url: str,
        output_dir: Path,
        index: int
    ) -> Path:
        """Download image from article"""
        output_path = output_dir / f"scene_{index:03d}.jpg"
        
        async with httpx.AsyncClient() as client:
            response = await client.get(url, timeout=30.0)
            response.raise_for_status()
            
            with open(output_path, 'wb') as f:
                f.write(response.content)
        
        return output_path
    
    async def _generate_ai_image(
        self,
        prompt: str,
        output_dir: Path,
        index: int
    ) -> Path:
        """Generate image using DALL-E"""
        output_path = output_dir / f"scene_{index:03d}.jpg"
        
        # Generate image
        image_urls = generate_openai_image(
            prompt=prompt,
            api_key=self.api_key,
            model="dall-e-3",
            size="1024x1024"
        )
        
        # Download
        download_image(image_urls[0], output_path)
        
        return output_path

"""
News Automation Service
Fully automated Economic Times news-to-video pipeline
"""
import logging
import asyncio
import shutil
from pathlib import Path
from typing import Dict, Any, List
from datetime import datetime

from app.core.config import settings
from content_sources.economic_times_fetcher import EconomicTimesFetcher
from content_sources.trend_analyzer import TrendAnalyzer
from app.agents.viral_script_agent import ViralScriptAgent
from app.agents.image_agent import ImageGeneratorAgent
from app.agents.audio_agent import AudioGeneratorAgent
from app.agents.assembly_agent import VideoAssemblyAgent
from app.agents.thumbnail_agent import ThumbnailAgent
from app.agents.metadata_agent import MetadataAgent
from app.agents.publishing_agent import PublishingAgent

logger = logging.getLogger(__name__)


class NewsAutomationService:
    """Fully automated news-to-video pipeline"""
    
    def __init__(self):
        self.fetcher = EconomicTimesFetcher()
        self.trend_analyzer = TrendAnalyzer()
        self.viral_script_agent = ViralScriptAgent(api_key=settings.OPENAI_API_KEY)
        self.image_agent = ImageGeneratorAgent(api_key=settings.OPENAI_API_KEY)
        self.audio_agent = AudioGeneratorAgent()
        self.assembly_agent = VideoAssemblyAgent()
        self.thumbnail_agent = ThumbnailAgent()
        self.metadata_agent = MetadataAgent(api_key=settings.OPENAI_API_KEY)
        self.publishing_agent = PublishingAgent(
            openai_api_key=settings.OPENAI_API_KEY,
            youtube_credentials={
                'api_key': settings.YOUTUBE_API_KEY,
                'access_token': settings.YOUTUBE_ACCESS_TOKEN
            }
        )
    
    async def run_automation(self, top_n: int = 3, auto_publish: bool = False, article_urls: List[str] = None) -> List[Dict[str, Any]]:
        """
        Run full automation pipeline
        
        Args:
            top_n: Number of top articles to process (if article_urls not provided)
            auto_publish: Whether to automatically publish videos
            article_urls: Specific article URLs to process (overrides top_n)
        
        Returns:
            List of generated video results
        """
        logger.info("=" * 60)
        logger.info("STARTING AUTOMATED NEWS-TO-VIDEO PIPELINE")
        logger.info("=" * 60)
        
        results = []
        
        try:
            # Step 1: Get articles to process
            if article_urls:
                logger.info(f"\n[STEP 1] Processing {len(article_urls)} specific articles...")
                articles = []
                for url in article_urls:
                    try:
                        article = self.fetcher.get_article_by_url(url)
                        articles.append(article)
                    except Exception as e:
                        logger.error(f"Failed to fetch article {url}: {e}")
                logger.info(f"✓ Fetched {len(articles)} articles")
                top_articles = articles
            else:
                # Original flow: fetch and rank
                logger.info("\n[STEP 1] Fetching latest Economic Times articles...")
                articles = self.fetcher.fetch_latest_articles(limit=20)
                logger.info(f"✓ Fetched {len(articles)} articles")
                
                # Step 2: Rank by trend score
                logger.info("\n[STEP 2] Analyzing trends and ranking articles...")
                top_articles = self.trend_analyzer.select_top_articles(articles, count=top_n)
                logger.info(f"✓ Selected top {len(top_articles)} trending articles")
            
            # Step 3: Process each article
            for i, article in enumerate(top_articles, 1):
                logger.info(f"\n{'=' * 60}")
                logger.info(f"PROCESSING ARTICLE {i}/{len(top_articles)}")
                logger.info(f"Title: {article['title']}")
                if 'trend_score' in article:
                    logger.info(f"Trend Score: {article['trend_score']:.2f}")
                logger.info(f"{'=' * 60}")
                
                try:
                    result = await self._process_article(article, auto_publish)
                    results.append(result)
                    logger.info(f"✓ Article {i} processed successfully")
                except Exception as e:
                    logger.error(f"✗ Failed to process article {i}: {e}")
                    results.append({
                        'success': False,
                        'article': article['title'],
                        'error': str(e)
                    })
            
            # Summary
            logger.info("\n" + "=" * 60)
            logger.info("AUTOMATION COMPLETE")
            logger.info("=" * 60)
            successful = sum(1 for r in results if r.get('success'))
            logger.info(f"✓ Successfully processed: {successful}/{len(results)}")
            logger.info(f"✗ Failed: {len(results) - successful}/{len(results)}")
            
            return results
            
        except Exception as e:
            logger.error(f"Automation pipeline failed: {e}", exc_info=True)
            raise
    
    async def _process_article(self, article: Dict[str, Any], auto_publish: bool) -> Dict[str, Any]:
        """Process a single article through the pipeline"""
        
        # Update global state
        from app.api.v1.automation import automation_state
        automation_state["current_article"] = article['title']
        
        # Create unique identifier
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        video_id = f"et_{timestamp}"
        
        # Clean up old temporary files before starting
        self._cleanup_temp_files()
        
        # Prepare context
        context = {
            'article': article,
            'title': article['title'],
            'content': article['content'],
            'summary': article['summary'],
            'category': article['category'],
            'images': article['images'],
            'video_id': video_id,
            'trend_score': article['trend_score']
        }
        
        # Step 1: Generate viral script
        automation_state["progress"] = "Generating viral script..."
        logger.info("  [1/7] Generating viral script...")
        script_result = await self.viral_script_agent.execute(context)
        context.update(script_result)
        logger.info("  ✓ Viral script generated")
        
        # Step 2: Generate/source images
        automation_state["progress"] = "Generating visuals..."
        logger.info("  [2/7] Generating visuals...")
        context['script_path'] = self._save_script(context['script'], video_id)
        context['image_folder'] = settings.IMAGES_DIR  # Assembly agent expects 'image_folder'
        context['images_dir'] = settings.IMAGES_DIR    # Keep for compatibility
        image_result = await self.image_agent.execute(context)
        context.update(image_result)
        logger.info("  ✓ Visuals ready")
        
        # Step 3: Generate audio narration
        automation_state["progress"] = "Generating audio narration..."
        logger.info("  [3/7] Generating audio narration...")
        context['audio_folder'] = settings.AUDIO_DIR   # Assembly agent expects 'audio_folder'
        context['audio_dir'] = settings.AUDIO_DIR      # Keep for compatibility
        audio_result = await self.audio_agent.execute(context)
        context.update(audio_result)
        logger.info("  ✓ Audio generated")
        
        # Step 4: Assemble video
        automation_state["progress"] = "Assembling video..."
        logger.info("  [4/7] Assembling video...")
        context['output_file'] = settings.VIDEO_OUTPUT_DIR / f"{video_id}.mp4"
        context['font_path'] = settings.FONT_PATH
        context['intro_image_path'] = settings.INTRO_IMAGE_PATH
        context['subtitle_path'] = settings.SUBTITLE_OUTPUT_DIR / f"{video_id}.srt"
        context['with_subtitles'] = True
        context['fps'] = 24
        assembly_result = await self.assembly_agent.execute(context)
        context.update(assembly_result)
        logger.info("  ✓ Video assembled")
        
        # Copy video to static directory for frontend access
        static_video_dir = settings.STATIC_DIR / "videos"
        static_video_dir.mkdir(parents=True, exist_ok=True)
        static_video_path = static_video_dir / f"{video_id}.mp4"
        if context['video_path'].exists():
            shutil.copy2(context['video_path'], static_video_path)
            logger.info(f"  ✓ Video copied to static directory: {static_video_path}")
        
        # Step 5: Generate thumbnail
        automation_state["progress"] = "Generating thumbnail..."
        logger.info("  [5/7] Generating thumbnail...")
        context['key_visual_path'] = context['image_paths'][0] if context.get('image_paths') else None
        context['output_path'] = settings.VIDEO_OUTPUT_DIR / f"{video_id}_thumbnail.jpg"
        thumbnail_result = await self.thumbnail_agent.execute(context)
        context.update(thumbnail_result)
        logger.info("  ✓ Thumbnail generated")
        
        # Copy thumbnail to static directory
        static_thumbnail_path = settings.STATIC_DIR / "videos" / f"{video_id}_thumbnail.jpg"
        if context['thumbnail_path'].exists():
            shutil.copy2(context['thumbnail_path'], static_thumbnail_path)
            logger.info(f"  ✓ Thumbnail copied to static directory: {static_thumbnail_path}")
        
        # Step 6: Generate metadata
        automation_state["progress"] = "Generating metadata..."
        logger.info("  [6/7] Generating metadata...")
        metadata_result = await self.metadata_agent.execute(context)
        context.update(metadata_result)
        logger.info("  ✓ Metadata generated")
        
        # Step 7: Publish (if enabled)
        if auto_publish:
            automation_state["progress"] = "Publishing to platforms..."
            logger.info("  [7/7] Publishing to platforms...")
            # Pass video_path as Path object and pre-generated metadata
            context['platforms'] = ['youtube']
            context['pregenerated_metadata'] = context.get('metadata')
            publish_result = await self.publishing_agent.execute(context)
            context.update(publish_result)
            logger.info("  ✓ Published successfully")
        else:
            logger.info("  [7/7] Skipping publish (auto_publish=False)")
        
        return {
            'success': True,
            'article_title': article['title'],
            'video_id': video_id,
            'video_path': str(context['video_path']),
            'thumbnail_path': str(context['thumbnail_path']),
            'metadata': context['metadata'],
            'trend_score': article['trend_score'],
            'published': auto_publish,
            'publish_results': context.get('published', {}) if auto_publish else None
        }
    
    def _save_script(self, script: Dict[str, Any], video_id: str) -> Path:
        """Save script to file"""
        import json
        script_path = settings.SCRIPT_DIR / f"{video_id}_script.json"
        script_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(script_path, 'w') as f:
            json.dump(script, f, indent=2)
        
        return script_path
    
    def _cleanup_temp_files(self):
        """Clean up temporary files from previous generations"""
        logger.info("Cleaning up temporary files...")
        
        cleanup_dirs = [
            settings.IMAGES_DIR,
            settings.AUDIO_DIR,
            settings.SCRIPT_DIR,
            settings.SUBTITLE_OUTPUT_DIR,
        ]
        
        files_removed = 0
        
        for directory in cleanup_dirs:
            if not directory.exists():
                continue
            
            try:
                for file_path in directory.iterdir():
                    if file_path.is_file():
                        try:
                            file_path.unlink()
                            files_removed += 1
                        except Exception as e:
                            logger.warning(f"Failed to delete {file_path}: {e}")
            except Exception as e:
                logger.warning(f"Failed to clean directory {directory}: {e}")
        
        logger.info(f"✓ Cleaned up {files_removed} temporary files")
    
    def cleanup_old_videos(self, keep_latest: int = 10):
        """
        Clean up old videos, keeping only the most recent ones
        
        Args:
            keep_latest: Number of latest videos to keep (default: 10)
        """
        logger.info(f"Cleaning up old videos (keeping latest {keep_latest})...")
        
        video_dirs = [
            settings.VIDEO_OUTPUT_DIR,
            settings.STATIC_DIR / "videos",
        ]
        
        for directory in video_dirs:
            if not directory.exists():
                continue
            
            try:
                # Get all video files with their modification times
                video_files = []
                for file_path in directory.iterdir():
                    if file_path.is_file() and file_path.suffix.lower() in ['.mp4', '.webm', '.mov', '.avi']:
                        video_files.append((file_path, file_path.stat().st_mtime))
                
                # Sort by modification time (newest first)
                video_files.sort(key=lambda x: x[1], reverse=True)
                
                # Delete old videos
                for file_path, _ in video_files[keep_latest:]:
                    try:
                        file_path.unlink()
                        # Also delete associated thumbnail if exists
                        thumbnail_path = file_path.with_name(file_path.stem + '_thumbnail.jpg')
                        if thumbnail_path.exists():
                            thumbnail_path.unlink()
                        logger.info(f"Deleted old video: {file_path.name}")
                    except Exception as e:
                        logger.warning(f"Failed to delete {file_path}: {e}")
                
            except Exception as e:
                logger.warning(f"Failed to clean video directory {directory}: {e}")
        
        logger.info("✓ Old videos cleaned up")

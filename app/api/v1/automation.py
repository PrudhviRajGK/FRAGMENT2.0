"""
News Automation API Endpoints
Endpoints for Economic Times news-to-video automation
"""
import logging
from typing import List, Optional
from fastapi import APIRouter, HTTPException, BackgroundTasks
from pydantic import BaseModel, Field

from app.services.news_automation_service import NewsAutomationService
from content_sources.economic_times_fetcher import EconomicTimesFetcher
from content_sources.trend_analyzer import TrendAnalyzer

logger = logging.getLogger(__name__)
router = APIRouter()

# Initialize services
automation_service = NewsAutomationService()
fetcher = EconomicTimesFetcher()
trend_analyzer = TrendAnalyzer()


class AutomationRequest(BaseModel):
    """Request model for automation"""
    top_n: int = Field(default=3, ge=1, le=10, description="Number of top articles to process")
    auto_publish: bool = Field(default=False, description="Whether to automatically publish videos")
    article_urls: Optional[List[str]] = Field(default=None, description="Specific article URLs to process (overrides top_n)")


class AutomationResponse(BaseModel):
    """Response model for automation"""
    status: str
    message: str
    job_id: Optional[str] = None


class ArticleResponse(BaseModel):
    """Response model for article data"""
    title: str
    summary: str
    url: str
    category: str
    trend_score: Optional[float] = None
    matched_keywords: Optional[List[str]] = None
    published_time: str


class AutomationStatusResponse(BaseModel):
    """Response model for automation status"""
    is_running: bool
    current_article: Optional[str] = None
    progress: Optional[str] = None


# Global state for tracking automation
automation_state = {
    "is_running": False,
    "current_article": None,
    "progress": None
}


@router.post("/run", response_model=AutomationResponse)
async def run_automation(
    request: AutomationRequest,
    background_tasks: BackgroundTasks
):
    """
    Run the full Economic Times news-to-video automation pipeline
    
    This endpoint:
    1. Fetches latest Economic Times articles (or uses provided URLs)
    2. Ranks them by trend score
    3. Selects top N articles
    4. Generates viral scripts
    5. Creates visuals
    6. Generates audio narration
    7. Assembles videos
    8. Generates thumbnails and metadata
    9. Optionally publishes to social media
    """
    try:
        if automation_state["is_running"]:
            raise HTTPException(
                status_code=409,
                detail="Automation is already running. Please wait for it to complete."
            )
        
        logger.info(f"Starting automation: top_n={request.top_n}, auto_publish={request.auto_publish}, article_urls={request.article_urls}")
        
        # Run automation in background
        background_tasks.add_task(
            run_automation_task,
            request.top_n,
            request.auto_publish,
            request.article_urls
        )
        
        return AutomationResponse(
            status="started",
            message=f"Automation started. Processing {len(request.article_urls) if request.article_urls else request.top_n} articles.",
            job_id=None
        )
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to start automation: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to start automation: {str(e)}")


async def run_automation_task(top_n: int, auto_publish: bool, article_urls: Optional[List[str]] = None):
    """Background task for running automation"""
    try:
        automation_state["is_running"] = True
        automation_state["progress"] = "Starting..."
        
        results = await automation_service.run_automation(
            top_n=top_n,
            auto_publish=auto_publish,
            article_urls=article_urls
        )
        
        logger.info(f"Automation completed. Processed {len(results)} articles.")
        
    except Exception as e:
        logger.error(f"Automation task failed: {e}", exc_info=True)
    finally:
        automation_state["is_running"] = False
        automation_state["current_article"] = None
        automation_state["progress"] = None


@router.get("/status", response_model=AutomationStatusResponse)
async def get_automation_status():
    """
    Get current automation status
    """
    return AutomationStatusResponse(
        is_running=automation_state["is_running"],
        current_article=automation_state["current_article"],
        progress=automation_state["progress"]
    )


@router.get("/articles", response_model=List[ArticleResponse])
async def fetch_articles(limit: int = 20):
    """
    Fetch latest Economic Times articles without processing
    
    Args:
        limit: Maximum number of articles to fetch (default: 20)
    """
    try:
        logger.info(f"Fetching {limit} articles from Economic Times")
        
        articles = fetcher.fetch_latest_articles(limit=limit)
        
        # Convert to response model
        response = [
            ArticleResponse(
                title=article['title'],
                summary=article['summary'],
                url=article['url'],
                category=article['category'],
                published_time=article['published_time'].isoformat()
            )
            for article in articles
        ]
        
        logger.info(f"Fetched {len(response)} articles")
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to fetch articles: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to fetch articles: {str(e)}")


@router.get("/trending", response_model=List[ArticleResponse])
async def get_trending_articles(top_n: int = 10):
    """
    Get top trending Economic Times articles
    
    Args:
        top_n: Number of top articles to return (default: 10)
    """
    try:
        logger.info(f"Fetching top {top_n} trending articles")
        
        # Fetch articles WITHOUT full content (fast)
        articles = fetcher.fetch_latest_articles(limit=50, fetch_full_content=False)
        
        # Rank by trend score (uses only metadata)
        ranked_articles = trend_analyzer.rank_articles(articles)
        
        # Select top N
        top_articles = ranked_articles[:top_n]
        
        # NOW fetch full content only for top articles
        top_articles = fetcher.fetch_full_content_for_articles(top_articles)
        
        # Convert to response model
        response = [
            ArticleResponse(
                title=article['title'],
                summary=article['summary'],
                url=article['url'],
                category=article['category'],
                trend_score=article.get('trend_score'),
                matched_keywords=article.get('matched_keywords', []),
                published_time=article['published_time'].isoformat()
            )
            for article in top_articles
        ]
        
        logger.info(f"Returning {len(response)} trending articles")
        
        return response
        
    except Exception as e:
        logger.error(f"Failed to get trending articles: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Failed to get trending articles: {str(e)}")


@router.post("/test")
async def test_automation():
    """
    Test automation with a single article (for debugging)
    """
    try:
        logger.info("Running test automation with 1 article")
        
        results = await automation_service.run_automation(top_n=1, auto_publish=False)
        
        return {
            "status": "success",
            "message": "Test automation completed",
            "results": results
        }
        
    except Exception as e:
        logger.error(f"Test automation failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Test automation failed: {str(e)}")


@router.post("/cleanup")
async def cleanup_resources(keep_videos: int = 10):
    """
    Clean up old videos and temporary files
    
    Args:
        keep_videos: Number of latest videos to keep (default: 10)
    """
    try:
        logger.info(f"Cleaning up resources (keeping {keep_videos} latest videos)")
        
        automation_service.cleanup_old_videos(keep_latest=keep_videos)
        
        return {
            "status": "success",
            "message": f"Cleanup completed. Kept {keep_videos} latest videos."
        }
        
    except Exception as e:
        logger.error(f"Cleanup failed: {str(e)}", exc_info=True)
        raise HTTPException(status_code=500, detail=f"Cleanup failed: {str(e)}")

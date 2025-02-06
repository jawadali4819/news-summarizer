from fastapi import FastAPI, HTTPException, status, Depends
from pydantic import BaseModel, HttpUrl
from pymongo.errors import PyMongoError
from typing import List, Optional
from db import db
import logging
from news import NewsSummarizer
from fastapi.middleware.cors import CORSMiddleware
from datetime import datetime
import os

# Configure logging
logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

# FastAPI app initialization
app = FastAPI()
# Setup CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allows all origins
    allow_credentials=True,
    allow_methods=["*"],  # Allows all methods
    allow_headers=["*"],  # Allows all headers
)

def get_db():
    """Dependency to access the MongoDB collection."""
    return db.articles  # Assuming db is already set up and connected

class ArticleModel(BaseModel):
    url: HttpUrl
    summary: str
    image: Optional[str] = None  # Optional field
    link: str

class URLInput(BaseModel):
    url: HttpUrl







@app.get("/articles", response_model=List[ArticleModel])
async def get_articles(db=Depends(get_db)):
    """Endpoint to retrieve all articles."""
    try:
        articles = await db.find({}).to_list(None)
        return [ArticleModel(**article) for article in articles]
    except PyMongoError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve articles."
        )







@app.post("/articles", status_code=status.HTTP_201_CREATED, response_model=ArticleModel)
async def save_article(input_data: URLInput, db=Depends(get_db)):
    """Endpoint to fetch, summarize, and save a new article."""
    try:
        url_str = str(input_data.url)
        logger.info(f"Starting processing for URL: {url_str}")

        # Check if article exists
        existing_article = await db.find_one({"url": url_str})
        if existing_article:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Article with this URL already exists."
            )

        # Initialize summarizer with proper API key
        try:
            summarizer = NewsSummarizer(api_key=os.getenv("GROK_API_KEY"))
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to initialize summarizer: {str(e)}"
            )

        # Process article
        try:
            result = summarizer.process_article(url_str)
        except (TimeoutError, ConnectionError) as e:
            raise HTTPException(
                status_code=status.HTTP_504_GATEWAY_TIMEOUT,
                detail=str(e)
            )
        except ValueError as e:
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=str(e)
            )

        # Validate result
        if not result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Failed to process article: empty result from summarizer"
            )

        if "error" in result:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail=f"Error processing article: {result['error']}"
            )

        # Create document
        document = {
            "url": url_str,
            "summary": result.get("summary", ""),
            "image": result.get("image", ""),
            "link": url_str,
        }

        # Save to database
        try:
            await db.insert_one(document)
        except PyMongoError as e:
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Database error: {str(e)}"
            )

        return ArticleModel(
            url=input_data.url,
            summary=result.get("summary", ""),
            image=result.get("image", ""),
            link=url_str
        )

    except HTTPException:
        raise
    except Exception as e:
        logger.exception("Unexpected error occurred")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=f"An unexpected error occurred: {str(e)}"
        )









@app.delete("/articles", status_code=status.HTTP_200_OK)
async def delete_article(url: HttpUrl, db=Depends(get_db)):
    """Endpoint to delete an article by URL."""
    try:
        result = await db.delete_one({"url": str(url)})
        if result.deleted_count == 0:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Article not found."
            )

        return {"message": "Article deleted successfully."}
    except PyMongoError as e:
        logger.error(f"Database error: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete article."
        )
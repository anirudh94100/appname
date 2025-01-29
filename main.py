from fastapi import APIRouter, HTTPException
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone
from google_play_scraper import search
from database import get_review_pool
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

app = FastAPI()

class AppSearchResult(BaseModel):
    id: int
    title: str
    developer: str
    appId: str
    icon: str


@app.get("/search/{app_name}", response_model=List[AppSearchResult])
async def search_apps(app_name: str):
    """
    Search for apps in the Google Play Store
    """
    try:
        results = search(app_name, lang='en', country='IN')
        return [AppSearchResult(
            id=i,
            title=app["title"],
            developer=app["developer"],
            appId=app["appId"],
            icon=app["icon"]
        ) for i, app in enumerate(results)]
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

class AppInfo(BaseModel):
    title: str
    developer: str
    icon: str

@app.get("/appinfo/{app_id}", response_model=AppInfo)  
async def fetch_app_info(app_id: str):  
    try:
        db = await get_review_pool()
        app_info = await db.fetchrow(
            "SELECT DISTINCT title, developer, icon FROM public.apps WHERE app_id = $1",
            app_id
        )

        if app_info:
            return AppInfo(
                title=app_info["title"],
                developer=app_info["developer"],
                icon=app_info["icon"]
            )
        else:
            raise HTTPException(status_code=404, detail="App not found")

    except Exception as e:
        logger.error(f"Error fetching app info: {str(e)}")
        raise HTTPException(status_code=500, detail="Error fetching app info/app not found")

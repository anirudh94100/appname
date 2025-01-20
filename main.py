from fastapi import APIRouter, HTTPException
from fastapi import FastAPI
from pydantic import BaseModel
from typing import List
from datetime import datetime, timezone
from google_play_scraper import search

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


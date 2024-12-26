from typing import Optional

import uvicorn
from fastapi import FastAPI, Depends, HTTPException, Query
from pydantic import BaseModel, EmailStr

from scraper import get_emails_by_subject

app = FastAPI(title="Gmail Scraper",
              description="API to scrape emails from Gmail based on subject substring",
              version="0.1.0", )

class ScrapeRequest(BaseModel):
    email_id: EmailStr
    subject_substring: str

@app.get("/scrape/", summary="Scrape Gmail for emails matching subject substring",
         description="Retrieves emails from a given Gmail address that contain a specific substring in their subject.")
async def scrape_emails(
        email_id: EmailStr = Query(..., description="The Gmail address to scrape"),
        subject_substring: str = Query(..., description="Substring to search for in email subjects"),
        max_results: Optional[int] = Query(10, description="Maximum number of emails to retrieve", ge=1, le=100)
):
    """
        Scrapes Gmail for emails matching a subject substring.

        Args:
            email_id: The Gmail address to scrape.
            subject_substring: Substring to search for in email subjects.
            max_results: Maximum number of emails to retrieve (default: 10).

        Returns:
            A list of emails matching the criteria, or an error message.
        """
    try:
        emails = get_emails_by_subject(email_id, subject_substring, max_results)
        return {"email_id": email_id, "subject_substring": subject_substring, "results": emails}
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"An error occurred: {e}")

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
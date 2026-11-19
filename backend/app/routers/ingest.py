"""Gmail ingestion.

Week 1, Day 2-3: OAuth2 connect, sync new messages + attachments since the
last sync, store attachments, create one documents row per attachment
(source='gmail', message_id set). Stub until then — honest 501.
"""
from fastapi import APIRouter, HTTPException

router = APIRouter(prefix="/ingest", tags=["ingest"])


@router.post("/gmail/sync")
def gmail_sync():
    raise HTTPException(
        status_code=501,
        detail="Gmail OAuth + sync lands in Week 1 (Day 2-3). Use POST /documents/upload meanwhile.",
    )

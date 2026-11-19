"""Document endpoints — the review queue's API.

Working today (Day 1): upload, list (review queue), detail, reject, correct
(corrections are logged to review_actions; extractions stay immutable).
Approve posts to QuickBooks Online sandbox in Week 3 — until then it is an
honest stub that says so, instead of pretending to post.
"""
import shutil
from pathlib import Path

from fastapi import APIRouter, Depends, File, HTTPException, UploadFile
from sqlalchemy.orm import Session

from ..config import settings
from ..db import get_db
from ..models import Document, ReviewAction
from ..schemas import CorrectionIn, DocumentDetailOut, DocumentOut

router = APIRouter(prefix="/documents", tags=["documents"])


@router.post("/upload", response_model=DocumentOut, status_code=201)
def upload_document(file: UploadFile = File(...), db: Session = Depends(get_db)):
    """Manual intake: store the file, create the document row.

    Classification + extraction get triggered here once the Week 1 pipeline
    lands (Day 4 classifier, Day 5-7 extraction chain).
    """
    upload_dir = Path(settings.upload_dir)
    upload_dir.mkdir(parents=True, exist_ok=True)
    dest = upload_dir / file.filename
    with dest.open("wb") as out:
        shutil.copyfileobj(file.file, out)

    doc = Document(source="upload", file_path=str(dest), status="received")
    db.add(doc)
    db.commit()
    db.refresh(doc)
    return doc


@router.get("", response_model=list[DocumentOut])
def list_documents(status: str | None = None, db: Session = Depends(get_db)):
    """The review queue is GET /documents?status=review."""
    q = db.query(Document)
    if status:
        q = q.filter(Document.status == status)
    return q.order_by(Document.created_at.desc()).all()


@router.get("/{document_id}", response_model=DocumentDetailOut)
def get_document(document_id: int, db: Session = Depends(get_db)):
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    return doc


@router.post("/{document_id}/correct", status_code=201)
def correct_document(document_id: int, correction: CorrectionIn, db: Session = Depends(get_db)):
    """Save a field correction — logged, never edited in place."""
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    action = ReviewAction(
        document_id=doc.id,
        user_action="correct",
        field=correction.field,
        old_value=correction.old_value,
        new_value=correction.new_value,
    )
    db.add(action)
    db.commit()
    db.refresh(action)
    return {"review_action_id": action.id, "document_id": doc.id}


@router.post("/{document_id}/reject", response_model=DocumentOut)
def reject_document(document_id: int, db: Session = Depends(get_db)):
    """Not an invoice / unusable."""
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    doc.status = "rejected"
    db.add(ReviewAction(document_id=doc.id, user_action="reject"))
    db.commit()
    db.refresh(doc)
    return doc


@router.post("/{document_id}/approve")
def approve_document(document_id: int, db: Session = Depends(get_db)):
    """Post the bill to QuickBooks Online sandbox (idempotent).

    Week 3, Day 18-19. Until the QBO integration lands this returns 501 on
    purpose: an approve that silently does nothing would be worse than an
    honest 'not built yet'.
    """
    doc = db.get(Document, document_id)
    if doc is None:
        raise HTTPException(status_code=404, detail="document not found")
    raise HTTPException(
        status_code=501,
        detail="QuickBooks posting lands in Week 3 (Day 18-19); CSV export is the interim sink.",
    )

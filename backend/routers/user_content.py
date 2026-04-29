from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, delete
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.other import UserContent
from schemas.main import UserContentOut, UserContentCreate
import uuid
import os
from pathlib import Path
from typing import Optional

router = APIRouter(prefix="/user-content", tags=["User Content"])

UPLOAD_DIR = Path("./uploads")
UPLOAD_DIR.mkdir(exist_ok=True)

ALLOWED_VIDEO_TYPES = {"video/mp4", "video/avi", "video/mov", "video/wmv"}
ALLOWED_IMAGE_TYPES = {"image/jpeg", "image/png", "image/gif", "image/webp"}
MAX_FILE_SIZE = 50 * 1024 * 1024  # 50MB

@router.get("/", response_model=list[UserContentOut])
async def list_user_content(
    content_type: Optional[str] = None,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    query = select(UserContent).where(UserContent.is_active == True)
    if content_type:
        query = query.where(UserContent.content_type == content_type)
    query = query.order_by(UserContent.created_at.desc())

    result = await db.execute(query)
    return [UserContentOut.model_validate(c) for c in result.scalars().all()]


@router.get("/my", response_model=list[UserContentOut])
async def list_my_content(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(UserContent)
        .where(UserContent.user_id == current_user.id, UserContent.is_active == True)
        .order_by(UserContent.created_at.desc())
    )
    return [UserContentOut.model_validate(c) for c in result.scalars().all()]


@router.post("/", response_model=UserContentOut, status_code=201)
async def create_content(
    title: str = Form(...),
    content_type: str = Form(...),
    description: str = Form(None),
    content_text: str = Form(None),
    tags: str = Form(None),  # JSON string of array
    file: UploadFile = File(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    if content_type not in ["video", "photo", "article"]:
        raise HTTPException(status_code=400, detail="Invalid content type")

    content_url = None
    thumbnail_url = None

    if content_type in ["video", "photo"]:
        if not file:
            raise HTTPException(status_code=400, detail="File required for video/photo content")

        if file.size > MAX_FILE_SIZE:
            raise HTTPException(status_code=400, detail="File too large (max 50MB)")

        if content_type == "video" and file.content_type not in ALLOWED_VIDEO_TYPES:
            raise HTTPException(status_code=400, detail="Invalid video format")
        elif content_type == "photo" and file.content_type not in ALLOWED_IMAGE_TYPES:
            raise HTTPException(status_code=400, detail="Invalid image format")

        # Save file
        file_ext = Path(file.filename).suffix
        file_id = str(uuid.uuid4())
        filename = f"{file_id}{file_ext}"
        file_path = UPLOAD_DIR / filename

        with open(file_path, "wb") as f:
            content = await file.read()
            f.write(content)

        content_url = f"/uploads/{filename}"

        # For videos, create a thumbnail (placeholder for now)
        if content_type == "video":
            thumbnail_url = f"/uploads/{file_id}_thumb.jpg"  # Would need ffmpeg to generate

    elif content_type == "article":
        if not content_text:
            raise HTTPException(status_code=400, detail="Content text required for articles")

    # Parse tags
    tag_list = []
    if tags:
        try:
            import json
            tag_list = json.loads(tags)
        except:
            pass

    content = UserContent(
        user_id=current_user.id,
        title=title,
        content_type=content_type,
        description=description,
        content_url=content_url,
        content_text=content_text,
        thumbnail_url=thumbnail_url,
        tags=tag_list,
    )

    db.add(content)
    await db.commit()
    await db.refresh(content)
    return UserContentOut.model_validate(content)


@router.get("/{content_id}", response_model=UserContentOut)
async def get_content(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await db.get(UserContent, content_id)
    if not content or not content.is_active:
        raise HTTPException(status_code=404, detail="Content not found")

    # Increment view count
    content.view_count = (content.view_count or 0) + 1
    await db.commit()

    return UserContentOut.model_validate(content)


@router.put("/{content_id}", response_model=UserContentOut)
async def update_content(
    content_id: uuid.UUID,
    title: str = Form(None),
    description: str = Form(None),
    content_text: str = Form(None),
    tags: str = Form(None),
    is_public: bool = Form(None),
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await db.get(UserContent, content_id)
    if not content or content.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Content not found")

    update_data = {}
    if title is not None:
        update_data["title"] = title
    if description is not None:
        update_data["description"] = description
    if content_text is not None:
        update_data["content_text"] = content_text
    if is_public is not None:
        update_data["is_public"] = is_public

    if tags:
        try:
            import json
            update_data["tags"] = json.loads(tags)
        except:
            pass

    if update_data:
        await db.execute(
            update(UserContent)
            .where(UserContent.id == content_id)
            .values(**update_data)
        )
        await db.commit()
        await db.refresh(content)

    return UserContentOut.model_validate(content)


@router.delete("/{content_id}")
async def delete_content(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await db.get(UserContent, content_id)
    if not content or content.user_id != current_user.id:
        raise HTTPException(status_code=404, detail="Content not found")

    # Soft delete
    content.is_active = False
    await db.commit()

    # Optionally delete file
    if content.content_url:
        file_path = Path(f"./{content.content_url}")
        if file_path.exists():
            file_path.unlink()

    return {"message": "Content deleted"}


@router.post("/{content_id}/like")
async def like_content(
    content_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    content = await db.get(UserContent, content_id)
    if not content:
        raise HTTPException(status_code=404, detail="Content not found")

    content.like_count = (content.like_count or 0) + 1
    await db.commit()
    return {"like_count": content.like_count}
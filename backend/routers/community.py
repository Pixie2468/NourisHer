from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, update, func
from core.database import get_db
from core.security import get_current_user
from models.user import User
from models.other import CommunityGroup, GroupMember, Post, Comment
from schemas.main import PostCreate, PostOut, CommentCreate, CommentOut, GroupOut
import uuid

router = APIRouter(prefix="/community", tags=["Community"])


# ── GROUPS ───────────────────────────────────────────────────
@router.get("/groups", response_model=list[GroupOut])
async def list_groups(
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(CommunityGroup).where(CommunityGroup.is_active == True).order_by(CommunityGroup.member_count.desc())
    )
    return [GroupOut.model_validate(g) for g in result.scalars().all()]


@router.post("/groups/{group_id}/join", status_code=201)
async def join_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    grp = await db.get(CommunityGroup, group_id)
    if not grp:
        raise HTTPException(status_code=404, detail="Group not found")

    existing = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
    )
    if existing.scalar_one_or_none():
        raise HTTPException(status_code=400, detail="Already a member")

    db.add(GroupMember(group_id=group_id, user_id=current_user.id))
    grp.member_count = (grp.member_count or 0) + 1
    await db.commit()
    return {"message": "Joined successfully"}


@router.delete("/groups/{group_id}/leave", status_code=204)
async def leave_group(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(GroupMember).where(GroupMember.group_id == group_id, GroupMember.user_id == current_user.id)
    )
    member = result.scalar_one_or_none()
    if not member:
        raise HTTPException(status_code=404, detail="Not a member")

    grp = await db.get(CommunityGroup, group_id)
    if grp:
        grp.member_count = max(0, (grp.member_count or 1) - 1)

    await db.delete(member)
    await db.commit()


# ── POSTS ────────────────────────────────────────────────────
@router.get("/groups/{group_id}/posts", response_model=list[PostOut])
async def list_posts(
    group_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
    skip: int = 0,
    limit: int = 20,
):
    result = await db.execute(
        select(Post)
        .where(Post.group_id == group_id, Post.is_active == True)
        .order_by(Post.is_pinned.desc(), Post.created_at.desc())
        .offset(skip).limit(limit)
    )
    return [PostOut.model_validate(p) for p in result.scalars().all()]


@router.post("/posts", response_model=PostOut, status_code=201)
async def create_post(
    data: PostCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    grp = await db.get(CommunityGroup, data.group_id)
    if not grp:
        raise HTTPException(status_code=404, detail="Group not found")

    post = Post(
        id=uuid.uuid4(),
        group_id=data.group_id,
        author_id=current_user.id,
        content=data.content,
        image_url=data.image_url,
    )
    db.add(post)
    await db.commit()
    await db.refresh(post)
    return PostOut.model_validate(post)


@router.post("/posts/{post_id}/like")
async def like_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    post.like_count = (post.like_count or 0) + 1
    await db.commit()
    return {"like_count": post.like_count}


@router.delete("/posts/{post_id}", status_code=204)
async def delete_post(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")
    if post.author_id != current_user.id:
        raise HTTPException(status_code=403, detail="Not your post")
    post.is_active = False
    await db.commit()


# ── COMMENTS ─────────────────────────────────────────────────
@router.get("/posts/{post_id}/comments", response_model=list[CommentOut])
async def list_comments(
    post_id: uuid.UUID,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    result = await db.execute(
        select(Comment).where(Comment.post_id == post_id).order_by(Comment.created_at.asc())
    )
    return [CommentOut.model_validate(c) for c in result.scalars().all()]


@router.post("/posts/{post_id}/comments", response_model=CommentOut, status_code=201)
async def add_comment(
    post_id: uuid.UUID,
    data: CommentCreate,
    current_user: User = Depends(get_current_user),
    db: AsyncSession = Depends(get_db),
):
    post = await db.get(Post, post_id)
    if not post:
        raise HTTPException(status_code=404, detail="Post not found")

    comment = Comment(
        id=uuid.uuid4(),
        post_id=post_id,
        author_id=current_user.id,
        content=data.content,
    )
    db.add(comment)
    post.comment_count = (post.comment_count or 0) + 1
    await db.commit()
    await db.refresh(comment)
    return CommentOut.model_validate(comment)

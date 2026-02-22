from fastapi import Depends, Header, HTTPException
from sqlalchemy.orm import Session

from app.db.session import get_db
from app.models.user import User


def get_current_user(
    x_user_id: int = Header(None),
    db: Session = Depends(get_db)
):

    if not x_user_id:
        raise HTTPException(
            status_code=400,
            detail="X-User-Id header required"
        )

    user = db.query(User).filter(
        User.id == x_user_id,
        User.active == True
    ).first()

    if not user:
        raise HTTPException(
            status_code=404,
            detail="User not found"
        )

    return user

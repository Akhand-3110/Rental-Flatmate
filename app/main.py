import uuid
from fastapi import FastAPI, WebSocket, WebSocketDisconnect, Query, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.orm import Session

from app.config import settings
from app.database import Base, engine, get_db
from app import models
from app.routers import auth, listings, tenants, interests
from app.websocket_manager import manager
from jose import jwt

Base.metadata.create_all(bind=engine)

app = FastAPI(title=settings.PROJECT_NAME, version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(auth.router)
app.include_router(listings.router)
app.include_router(tenants.router)
app.include_router(interests.router)

@app.get("/")
def health_status():
    return {"status": "online", "platform": settings.PROJECT_NAME}

@app.websocket("/ws/chat")
async def real_time_chat_endpoint(
    websocket: WebSocket,
    token: str = Query(...),
    listing_id: str = Query(...),
    tenant_id: str = Query(...),
    db: Session = Depends(get_db)
):
    """
    Stateful chat router handling access gates via active interest verification[cite: 1].
    """
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        user_id: str = payload.get("sub")
    except Exception:
        await websocket.close(code=1008) 
        return

    interest = db.query(models.InterestMatch).filter(
        models.InterestMatch.listing_id == listing_id,
        models.InterestMatch.tenant_id == tenant_id
    ).first()

    if not interest or interest.status != models.RequestStatus.ACCEPTED:
        await websocket.close(code=1008) 
        return

    room_key = f"{listing_id}_{tenant_id}"
    await manager.connect(websocket, room_key)

    try:
        while True:
            data = await websocket.receive_text()
            
            chat_msg = models.ChatMessage(
                id=str(uuid.uuid4()),
                room_key=room_key,
                sender_id=user_id,
                message=data
            )
            db.add(chat_msg)
            db.commit()

            await manager.broadcast_to_room(room_key, {
                "id": chat_msg.id,
                "sender_id": user_id,
                "message": data,
                "created_at": chat_msg.created_at.isoformat()
            })
    except WebSocketDisconnect:
        manager.disconnect(websocket, room_key)
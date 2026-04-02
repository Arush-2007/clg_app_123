"""
WebSocket endpoint for real-time chat.

Authentication: Firebase ID token passed as a ?token= query parameter.
WebSocket connections cannot set arbitrary HTTP headers after the initial
handshake in most browser/Flutter implementations, so the token is passed
in the query string instead of the Authorization header.

Close codes used:
  4001 — invalid or expired Firebase token
  4003 — authenticated but not a member of the conversation
  4000 — unexpected server error during the session
"""

import logging

from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from firebase_admin import auth as firebase_auth
from sqlalchemy.orm import Session

from src.core.connection_manager import manager
from src.core.database import get_db
from src.core.security import _init_firebase
from src.models.chat import SendMessageRequest
from src.services.chat_service import ChatService

logger = logging.getLogger(__name__)

router = APIRouter(tags=["websocket"])
_svc = ChatService()


@router.websocket("/ws/chat/{conversation_id}")
async def websocket_chat(
    websocket: WebSocket,
    conversation_id: int,
    token: str = Query(..., description="Firebase ID token"),
    db: Session = Depends(get_db),
) -> None:
    """
    WebSocket endpoint for a single chat conversation room.

    Flow:
      1. Verify Firebase token from ?token= query param.
      2. Check the caller is a member of conversation_id.
      3. Accept and join the room.
      4. Send a "joined" system message to the caller only.
      5. Listen for incoming JSON messages; persist and broadcast each one.
      6. On disconnect or error, cleanly leave the room.

    Expected client message format:
      { "content": "hello", "message_type": "text" }

    Broadcast format (same as MessageResponse.model_dump):
      { "id": 1, "conversation_id": 2, "sender_uid": "...", ... }
    """

    # ── Step 1: Verify Firebase token ─────────────────────────────────────────
    if not _init_firebase():
        logger.error("ws_chat: Firebase not initialised, refusing connection")
        await websocket.close(code=4001)
        return

    try:
        decoded = firebase_auth.verify_id_token(token, check_revoked=False)
    except Exception as exc:
        logger.warning(
            "ws_chat: token verification failed for conversation %d: %s: %s",
            conversation_id, type(exc).__name__, exc,
        )
        await websocket.close(code=4001)
        return

    firebase_uid: str = decoded["uid"]

    # ── Step 2: Check membership ───────────────────────────────────────────────
    if not _svc._is_member(db, conversation_id, firebase_uid):
        logger.warning(
            "ws_chat: uid %s is not a member of conversation %d",
            firebase_uid, conversation_id,
        )
        await websocket.close(code=4003)
        return

    # ── Step 3: Accept and join the room ──────────────────────────────────────
    await manager.connect(websocket, conversation_id)
    logger.info(
        "ws_chat: uid %s joined conversation %d (room size now %d)",
        firebase_uid, conversation_id, manager.room_size(conversation_id),
    )

    try:
        # ── Step 4: Greet the joining client (not broadcast) ──────────────────
        await websocket.send_json({
            "type": "system",
            "message": f"Connected to conversation {conversation_id}",
        })

        # ── Step 5: Message receive loop ──────────────────────────────────────
        while True:
            raw = await websocket.receive_json()

            # Validate incoming payload via Pydantic
            try:
                payload = SendMessageRequest(**raw)
            except Exception as exc:
                # Send a validation error back to this client only, keep loop alive
                await websocket.send_json({
                    "type": "error",
                    "message": f"Invalid message format: {exc}",
                })
                continue

            # Persist the message
            msg = _svc.send_message(
                db,
                conversation_id=conversation_id,
                sender_uid=firebase_uid,
                payload=payload,
            )

            # Build the broadcast payload (mirrors MessageResponse)
            display_name = _svc._get_display_name(db, firebase_uid)
            broadcast_payload = {
                "type": "message",
                "id": msg.id,
                "conversation_id": msg.conversation_id,
                "sender_uid": msg.sender_uid,
                "display_name": display_name,
                # TODO (migration 0011): include is_anonymous_sender when column exists
                "is_anonymous_sender": False,
                "content": msg.content,
                "message_type": msg.message_type,
                "is_deleted": msg.is_deleted,
                "created_at": msg.created_at.isoformat(),
            }

            # Broadcast to all room members (including sender for confirmation)
            await manager.broadcast(conversation_id, broadcast_payload)

    except WebSocketDisconnect:
        logger.info(
            "ws_chat: uid %s disconnected from conversation %d",
            firebase_uid, conversation_id,
        )
    except Exception as exc:
        logger.exception(
            "ws_chat: unexpected error for uid %s in conversation %d: %s",
            firebase_uid, conversation_id, exc,
        )
        try:
            await websocket.close(code=4000)
        except Exception:
            pass

    finally:
        # ── Step 6: Leave the room ─────────────────────────────────────────────
        manager.disconnect(websocket, conversation_id)
        logger.info(
            "ws_chat: uid %s left conversation %d (room size now %d)",
            firebase_uid, conversation_id, manager.room_size(conversation_id),
        )

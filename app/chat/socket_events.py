from flask import request
from flask_socketio import emit
from flask_login import current_user
from app import socketio, db
from app.models import Message

# Track active users and their session IDs
user_rooms = {}  # Maps username -> set of session IDs (sids)


@socketio.on('connect')
def handle_connect():
    if current_user.is_authenticated:
        sid = request.sid
        user_rooms.setdefault(current_user.username, set()).add(sid)
        print(f"{current_user.username} connected with SID {sid}")


@socketio.on('disconnect')
def handle_disconnect():
    if current_user.is_authenticated:
        sid = request.sid
        user_set = user_rooms.get(current_user.username)
        if user_set:
            user_set.discard(sid)
            if not user_set:
                del user_rooms[current_user.username]
        print(f"{current_user.username} disconnected from SID {sid}")


@socketio.on('send_message')
def handle_send_message(data):
    message_text = data.get('message')
    sender = data.get('sender') or (current_user.username if current_user.is_authenticated else 'Guest')
    role = data.get('role') or (current_user.role if current_user.is_authenticated else 'guest')
    recipient = data.get('to', 'Everyone')

    if not message_text:
        emit('error', {'error': 'Empty message'})
        return

    sender_id = current_user.id if current_user.is_authenticated else None

    # Save to DB
    try:
        new_message = Message(
            sender=sender,
            sender_id=sender_id,
            message=message_text,
            role=role
        )
        db.session.add(new_message)
        db.session.commit()
    except Exception as e:
        db.session.rollback()
        print(f"Failed to save message: {e}")
        emit('error', {'error': 'Message saving failed'})
        return

    # Payload to send to clients
    message_payload = {
        'username': sender,
        'message': message_text,
        'to': recipient,
        'role': role
    }

    # Emit message
    if recipient == 'Everyone':
        emit('receive_message', message_payload, broadcast=True)
    else:
        recipient_sids = user_rooms.get(recipient, [])
        sender_sids = user_rooms.get(sender, [])

        for sid in recipient_sids:
            emit('receive_message', message_payload, room=sid)

        for sid in sender_sids:
            emit('receive_message', message_payload, room=sid)

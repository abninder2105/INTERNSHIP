from flask import Blueprint, render_template, jsonify
from flask_login import login_required, current_user
from app.models import User  # ✅ Ensure User is imported

chat_bp = Blueprint('chat', __name__)

@chat_bp.route('/chat')
@login_required
def chat():
    return render_template('chat.html', user=current_user)

# ✅ Route to get the list of users (excluding the current user)
@chat_bp.route('/chat/users')
@login_required
def users():
    users = [user.username for user in User.query.all() if user.username != current_user.username]
    return jsonify(users)

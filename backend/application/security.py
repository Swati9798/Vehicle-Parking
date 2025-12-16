from flask_jwt_extended import JWTManager, create_access_token, create_refresh_token, jwt_required, get_jwt_identity, get_jwt
from functools import wraps
from flask import jsonify
from application.models import User

# Initialize JWT
jwt = JWTManager()

# Store for blacklisted tokens (in production, use Redis)
blacklisted_tokens = set()

@jwt.token_in_blocklist_loader
def check_if_token_revoked(jwt_header, jwt_payload):
    """Check if token is in blacklist"""
    return jwt_payload['jti'] in blacklisted_tokens

@jwt.expired_token_loader
def expired_token_callback(jwt_header, jwt_payload):
    """Handle expired token"""
    return jsonify({'message': 'Token has expired'}), 401

@jwt.invalid_token_loader
def invalid_token_callback(error):
    """Handle invalid token"""
    return jsonify({'message': 'Invalid token'}), 401

@jwt.unauthorized_loader
def missing_token_callback(error):
    """Handle missing token"""
    return jsonify({'message': 'Authorization token is required'}), 401

def admin_required(f):
    """Decorator to require admin role"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())  # Convert back to int
        user = User.query.get(current_user_id)
        if not user or not user.is_admin():
            return jsonify({'message': 'Admin access required'}), 403
        return f(*args, **kwargs)
    return decorated_function

def user_required(f):
    """Decorator to require user role (admin or regular user)"""
    @wraps(f)
    @jwt_required()
    def decorated_function(*args, **kwargs):
        current_user_id = int(get_jwt_identity())  # Convert back to int
        user = User.query.get(current_user_id)
        if not user or not user.is_active:
            return jsonify({'message': 'Access denied'}), 403
        return f(*args, **kwargs)
    return decorated_function

def generate_tokens(user):
    """Generate access and refresh tokens for user"""
    access_token = create_access_token(identity=str(user.id))  # Convert to string
    refresh_token = create_refresh_token(identity=str(user.id))  # Convert to string
    return {
        'access_token': access_token,
        'refresh_token': refresh_token,
        'user': user.to_dict()
    }

def revoke_token():
    """Add current token to blacklist"""
    jti = get_jwt()['jti']
    blacklisted_tokens.add(jti)
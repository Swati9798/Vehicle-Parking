from flask import Flask
from flask_cors import CORS
from application.config import DevelopmentConfig
from application.database import db
from application.routes import create_routes
from application.security import jwt
from application.mail import mail
import os
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()

def create_app():
    app = Flask(__name__)
    
    # Configuration
    app.config.from_object(DevelopmentConfig)
    
    # Initialize extensions
    db.init_app(app)
    jwt.init_app(app)
    mail.init_app(app)
    
    # Configure CORS to allow frontend requests
    CORS(app, 
         origins=['*'], 
         supports_credentials=True,
         allow_headers=['Content-Type', 'Authorization'],
         methods=['GET', 'POST', 'PUT', 'DELETE', 'OPTIONS'])
    
    # Register routes
    create_routes(app)
    
    # Create database tables
    with app.app_context():
        # Ensure instance directory exists
        instance_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'instance')
        os.makedirs(instance_dir, exist_ok=True)
        
        db.create_all()
        
        # Create admin user if not exists
        from application.models import User
        admin_user = User.query.filter_by(username='admin').first()
        if not admin_user:
            admin_user = User(
                username='admin',
                email='admin@parking.com',
                password='admin123',  # Will be hashed in model
                role='admin'
            )
            db.session.add(admin_user)
            db.session.commit()
            print("Admin user created successfully!")
        else:
            print("Admin user already exists!")
        
        print("Database initialized successfully!")
    
    return app

app = create_app()

if __name__ == '__main__':
    app.run(debug=True, host='0.0.0.0', port=5000)
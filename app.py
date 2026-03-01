from flask import Flask
from config import SECRET_KEY
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.transaction_routes import transaction_bp
from routes.recurring_routes import recurring_bp
from routes.prediction_routes import prediction_bp
import os

def create_app():
    # Initialize database on startup
    from database.db_init import init_database
    init_database()
    
    # Train category model if it doesn't exist
    from ml.train_category_model import train_model
    model_path = "ml/model.pkl"
    if not os.path.exists(model_path):
        train_model()
    
    # Process recurring expenses
    from models.recurring_model import process_recurring_expenses
    process_recurring_expenses()
    
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Register blueprints
    app.register_blueprint(auth_bp)

    # Landing page route
    @app.route('/')
    def home():
        from flask import session, redirect, url_for, render_template
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))
        return render_template('landing.html')
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(recurring_bp)
    app.register_blueprint(prediction_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

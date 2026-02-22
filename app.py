from flask import Flask
from config import SECRET_KEY
from routes.auth_routes import auth_bp
from routes.dashboard_routes import dashboard_bp
from routes.transaction_routes import transaction_bp
from routes.recurring_routes import recurring_bp
from routes.prediction_routes import prediction_bp

def create_app():
    app = Flask(__name__)
    app.secret_key = SECRET_KEY

    # Register blueprints
    app.register_blueprint(auth_bp)

    # Simple home route to test login redirect
    @app.route('/')
    def home():
        from flask import session, redirect, url_for
        if 'user_id' in session:
            return redirect(url_for('dashboard.index'))  # Dashboard not implemented yet
        return redirect(url_for('auth.login'))
    
    app.register_blueprint(dashboard_bp)
    app.register_blueprint(transaction_bp)
    app.register_blueprint(recurring_bp)
    app.register_blueprint(prediction_bp)
    return app

if __name__ == "__main__":
    app = create_app()
    app.run(debug=True)

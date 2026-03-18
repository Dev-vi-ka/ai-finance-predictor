# 🤖 AI Finance Predictor

A sophisticated, Flask-based personal finance management system empowered by Machine Learning. This application goes beyond simple expense tracking by providing AI-powered spending predictions, automated transaction classification, and a comprehensive administrative suite for platform monitoring.

## 🚀 Key Features

### 💎 Personal Finance Suite
- **Interactive Dashboard**: Get an instant health check of your finances with a custom **AI Health Score** and real-time budget status.
- **Smart Budgeting**: Set monthly budget limits across categories like Food, Travel, Bills, and Shopping. Receive automated alerts when you approach or exceed your limits.
- **Transaction Management**: Securely track income and expenses with an intuitive interface.
- **Recurring Expenses**: Automate your regularly occurring bills and subscriptions.

### 🧠 AI & Machine Learning Features
- **Spending Predictions**: Uses `scikit-learn` to analyze historical data and predict your total spending for the upcoming month.
- **Auto-Categorization**: Automatically classifies new transactions based on your past behavior using a random forest classifier.
- **Trend Analysis**: Identify spending patterns, category growth rates, and seasonal fluctuations.
- **Anomaly Detection**: Flags unusual spending spikes or irregular transaction patterns.

### 👑 Advanced Admin Panel
- **360° Platform Metrics**: Monitor total users, active engagement rates, and aggregated financial health across the platform.
- **Trend Dashboard**: Analyze growth trends and seasonal patterns across the entire user base.
- **ML Model Performance**: Real-time monitoring of classification accuracy, user correction rates, and model drift.
- **Interactive Reports**: Generate and export detailed analytics on user behavior and financial trends.

## 🛠️ Tech Stack

- **Backend**: Python 3.x, [Flask](https://flask.palletsprojects.com/)
- **Database**: SQLite3
- **Machine Learning**: `scikit-learn`, `pandas`, `numpy`
- **Visualization**: `matplotlib` (for trend analysis and admin metrics)
- **Frontend**: HTML5, Jinja2 Templates, Vanilla CSS (Modern, Responsive Design)
- **Utilities**: `python-dateutil`, `bleach` (for sanitization)

## ⚙️ Installation & Setup

### 1. Prerequisites
- Python 3.8 or higher installed on your system.
- `pip` package manager.

### 2. Clone & Prepare
```bash
# Clone the repository
git clone <repository-url>
cd ai-finance-predictor

# Create and activate virtual environment
python -m venv venv
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Running the Application
```bash
python app.py
```
*The system will automatically initialize the database, process recurring expenses, and train initial ML models on startup.*

### 4. Admin Access
By default, the user with `ID = 1` has administrative privileges. Navigate to `/admin/dashboard` or use the **👑 Admin** dropdown in the navigation bar.

## 📂 Project Structure

- `app.py`: Main entry point and Flask configuration.
- `routes/`: Blueprint-based modular routing (Admin, Auth, Budgets, Dashboard, Transactions).
- `models/`: Interface for database operations and data modeling.
- `ml/`: Core machine learning logic, training scripts, and predictors.
- `database/`: Persistence layer and initialization scripts.
- `static/`: Modern CSS styles, custom icons, and client-side scripts.
- `templates/`: Structured Jinja2 layouts and functional views.

## 🛡️ Security & Notes
- Ensure your `SECRET_KEY` in `config.py` is kept private.
- The `finance.db` file and `venv` directory are ignored by Git for security and cleanliness.
- Admin authentication currently relies on session-based user ID verification.

---
*Built with ❤️ for better financial clarity.*

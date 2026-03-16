# AI Finance Predictor

A Flask-based web application that helps users manage their personal finances, track expenses and budgets, and provides AI-powered predictions for future spending and categories. 

## Features

- **User Authentication**: Secure signup and login for users.
- **Dashboard**: Overview of your financial health, including recent transactions and budget status.
- **Transactions Management**: Add, edit, and view income and expense transactions.
- **Budgeting**: Set and monitor budgets across different categories.
- **Recurring Expenses**: Manage repeated expenses automatically.
- **AI Predictions**: Uses Machine Learning (`scikit-learn`) to predict future spending and automatically classify transaction categories.
- **Admin Panel**: Dedicated dashboard for administrators to monitor user activity and platform metrics.

## Tech Stack

- **Backend**: Python, Flask
- **Database**: SQLite
- **Machine Learning**: `scikit-learn`, `pandas`, `numpy`
- **Frontend**: HTML5, Jinja2 Templates, CSS 

## Installation

1. **Clone the repository** (if you haven't already):
   ```bash
   git clone <repository-url>
   cd ai-finance-predictor
   ```

2. **Create a virtual environment**:
   ```bash
   python -m venv venv
   ```

3. **Activate the virtual environment**:
   - On Windows:
     ```bash
     venv\Scripts\activate
     ```
   - On macOS/Linux:
     ```bash
     source venv/bin/activate
     ```

4. **Install the dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

## Usage

1. **Start the application**:
   ```bash
   python app.py
   ```
   *Note: Taking this step will automatically initialize the SQLite database if it doesn't exist, process any recurring expenses, and train the Machine Learning category model if it is missing.*

2. **Access the application**:
   Open your web browser and go to `http://127.0.0.1:5000`

## Project Structure

- `app.py`: Main entry point for the Flask application.
- `config.py`: Configuration settings and constants.
- `database/`: Contains the SQLite database file and initialization scripts.
- `ml/`: Machine Learning models and scripts for training and prediction.
- `models/`: Database models and wrappers.
- `routes/`: Flask blueprints for different sections of the application.
- `static/`: Static files (CSS, JS, Images).
- `templates/`: Jinja2 HTML templates.
- `utils/`: Utility and helper functions.

## Note
Ensure you keep sensitive information like `SECRET_KEY` secure and do not commit the `finance.db` database or `venv` to version control.

from flask import Blueprint, jsonify, session
from ml.expense_predictor import predict_next_month_spending

prediction_bp = Blueprint('prediction', __name__)

@prediction_bp.route('/api/prediction', methods=['GET'])
def get_prediction():
    if 'user_id' not in session:
        return jsonify({"error": "Unauthorized"}), 401
    
    user_id = session['user_id']
    
    # Get ML prediction
    prediction_data = predict_next_month_spending(user_id)
    
    return jsonify(prediction_data)

from flask import Flask, request, jsonify
import joblib
import threading
import time

app = Flask(__name__)

# Global variables
recommender = None
model_ready = False
model_loading_error = None

def load_model():
    global recommender, model_ready, model_loading_error
    try:
        print("Starting model loading...")
        with open("model_question_recommender_optimized.pkl", "rb") as model_file:
            recommender = joblib.load(model_file)
        model_ready = True
        print("Model loaded successfully!")
    except Exception as e:
        model_loading_error = str(e)
        print(f"Error loading model: {str(e)}")

# Start model loading in a separate thread
loading_thread = threading.Thread(target=load_model)
loading_thread.start()

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint that immediately returns success"""
    return jsonify({'status': 'healthy'}), 200

@app.route('/model-status', methods=['GET'])
def model_status():
    """Endpoint to check model loading status"""
    if model_ready:
        return jsonify({'status': 'ready'})
    elif model_loading_error:
        return jsonify({'status': 'error', 'error': model_loading_error}), 500
    else:
        return jsonify({'status': 'loading'}), 202

@app.route('/recommend', methods=['POST'])
def recommend_questions():
    global recommender, model_ready
    
    if not model_ready:
        return jsonify({
            'error': 'Model is still loading. Please check /model-status endpoint for status.'
        }), 503
    
    try:
        # Get data from request
        data = request.get_json()
        
        if not data or 'questions' not in data:
            return jsonify({
                'error': 'Please provide questions in the request body'
            }), 400
            
        input_questions = data['questions']
        num_recommendations = data.get('num_recommendations', 8)
        
        # Validate input
        if not isinstance(input_questions, list):
            return jsonify({
                'error': 'Questions should be provided as a list'
            }), 400
            
        # Make predictions
        predictions = recommender.recommend_questions(input_questions, num_recommendations)
        
        return jsonify({
            'recommended_questions': predictions,
            'input_questions': input_questions,
            'num_recommendations': num_recommendations
        })
        
    except Exception as e:
        return jsonify({
            'error': str(e)
        }), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)

# from flask import Flask, request, jsonify
# from recommender import QuestionRecommender
# import joblib

# app = Flask(__name__)

# # Load the model when the application starts
# try:
#     with open("model_question_recommender_optimized.pkl", "rb") as model_file:
#         recommender = joblib.load(model_file) 
# except Exception as e:
#     print(f"Error loading model: {str(e)}")
#     recommender = None

# @app.route('/recommend', methods=['POST'])
# def recommend_questions():
#     try:
#         # Get data from request
#         data = request.get_json()
        
#         if not data or 'questions' not in data:
#             return jsonify({
#                 'error': 'Please provide questions in the request body'
#             }), 400
            
#         input_questions = data['questions']
#         num_recommendations = data.get('num_recommendations', 8)  # Default to 8 if not specified
        
#         # Validate input
#         if not isinstance(input_questions, list):
#             return jsonify({
#                 'error': 'Questions should be provided as a list'
#             }), 400
            
#         # Make predictions
#         predictions = recommender.recommend_questions(input_questions, num_recommendations)
        
#         # Return results
#         return jsonify({
#             'recommended_questions': predictions,
#             'input_questions': input_questions,
#             'num_recommendations': num_recommendations
#         })
        
#     except Exception as e:
#         return jsonify({
#             'error': str(e)
#         }), 500

# if __name__ == '__main__':
#     app.run(debug=False, port=5000)

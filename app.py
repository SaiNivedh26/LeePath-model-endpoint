# from flask import Flask, request, jsonify
# import pickle
# import requests
# import io
# import json
# from recommender import QuestionRecommender

# app = Flask(__name__)

# class GoogleDriveModelLoader:
#     def __init__(self, config_path="gdrive_config.json"):
#         """
#         Initialize with a config file containing Google Drive URLs
#         config format:
#         {
#             "chunks": [
#                 {"url": "google-drive-url-for-chunk-0"},
#                 {"url": "google-drive-url-for-chunk-1"},
#                 ...
#             ],
#             "metadata_url": "google-drive-url-for-metadata"
#         }
#         """
#         self.config_path = config_path
#         self.urls = self._load_config()
        
#     def _load_config(self):
#         """Load Google Drive URLs from config file"""
#         with open(self.config_path, 'r') as f:
#             return json.load(f)
    
#     def _get_direct_link(self, sharing_url):
#         """Convert Google Drive sharing URL to direct download link"""
#         file_id = sharing_url.split('/d/')[1].split('/')[0]
#         return f"https://drive.google.com/uc?id={file_id}"
    
#     def _download_chunk(self, url):
#         """Download a single chunk from Google Drive"""
#         try:
#             direct_link = self._get_direct_link(url)
#             response = requests.get(direct_link)
#             if response.status_code == 200:
#                 return response.content
#             else:
#                 raise Exception(f"Failed to download chunk. Status: {response.status_code}")
#         except Exception as e:
#             print(f"Error downloading chunk: {str(e)}")
#             return None
    
#     def load_model(self):
#         """Load and combine all model chunks"""
#         try:
#             # First download metadata
#             metadata_content = self._download_chunk(self.urls["metadata_url"])
#             if metadata_content is None:
#                 raise Exception("Failed to download metadata")
            
#             metadata = pickle.loads(metadata_content)
#             print(f"Model has {metadata['num_chunks']} chunks")
            
#             # Download and combine all chunks
#             model_bytes = b""
#             for chunk_info in self.urls["chunks"]:
#                 chunk_content = self._download_chunk(chunk_info["url"])
#                 if chunk_content is None:
#                     raise Exception(f"Failed to download chunk")
#                 model_bytes += chunk_content
            
#             # Reconstruct the model
#             model = pickle.loads(model_bytes)
#             return model
            
#         except Exception as e:
#             print(f"Error loading model: {str(e)}")
#             return None

# # Initialize model loader
# model_loader = GoogleDriveModelLoader()

# # Load the model when the application starts
# recommender = model_loader.load_model()

# @app.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         'status': 'healthy',
#         'model_loaded': recommender is not None
#     })

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
#         num_recommendations = data.get('num_recommendations', 8)
        
#         # Validate input
#         if not isinstance(input_questions, list):
#             return jsonify({
#                 'error': 'Questions should be provided as a list'
#             }), 400
        
#         # Check if model is loaded
#         if recommender is None:
#             return jsonify({
#                 'error': 'Model is not properly loaded'
#             }), 500
        
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
#     app.run(debug=True, port=5000)  
# from flask import Flask, request, jsonify
# import pickle
# import os
# from recommender import QuestionRecommender

# app = Flask(__name__)

# def load_split_model(chunks_dir):
#     """
#     Load and combine model chunks into the original model
    
#     Args:
#         chunks_dir (str): Directory containing the model chunks
#     """
#     try:
#         # Load metadata
#         with open(os.path.join(chunks_dir, 'chunks_metadata.pkl'), 'rb') as f:
#             metadata = pickle.load(f)
        
#         # Combine chunks
#         model_bytes = b""
#         for i in range(metadata['num_chunks']):
#             chunk_path = os.path.join(chunks_dir, f'model_chunk_{i}.pkl')
#             with open(chunk_path, 'rb') as f:
#                 model_bytes += f.read()
        
#         # Reconstruct the model
#         model = pickle.loads(model_bytes)
#         return model
    
#     except Exception as e:
#         print(f"Error loading model chunks: {str(e)}")
#         return None

# # Load the model when the application starts
# CHUNKS_DIR = "model_chunks"  # Directory containing model chunks
# recommender = load_split_model(CHUNKS_DIR)

# @app.route('/health', methods=['GET'])
# def health_check():
#     """Health check endpoint"""
#     return jsonify({
#         'status': 'healthy',
#         'model_loaded': recommender is not None
#     })

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
#         num_recommendations = data.get('num_recommendations', 8)
        
#         # Validate input
#         if not isinstance(input_questions, list):
#             return jsonify({
#                 'error': 'Questions should be provided as a list'
#             }), 400
        
#         # Check if model is loaded
#         if recommender is None:
#             return jsonify({
#                 'error': 'Model is not properly loaded'
#             }), 500
        
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
#     app.run(debug=True, port=5000)



# import pickle
# import os
# import math

# def split_model(input_file, output_dir, chunk_size_mb=90):
#     """
#     Split a large pickle file into smaller chunks
    
#     Args:
#         input_file (str): Path to the input pickle file
#         output_dir (str): Directory to save the chunks
#         chunk_size_mb (int): Maximum size of each chunk in MB
#     """
#     # Create output directory if it doesn't exist
#     os.makedirs(output_dir, exist_ok=True)
    
#     # Calculate chunk size in bytes
#     chunk_size = chunk_size_mb * 1024 * 1024
    
#     # Read the model file
#     with open(input_file, 'rb') as f:
#         model_bytes = f.read()
    
#     # Calculate total chunks needed
#     total_size = len(model_bytes)
#     num_chunks = math.ceil(total_size / chunk_size)
    
#     print(f"Total model size: {total_size / (1024*1024):.2f} MB")
#     print(f"Splitting into {num_chunks} chunks of {chunk_size_mb} MB each")
    
#     # Split and save chunks
#     for i in range(num_chunks):
#         start_idx = i * chunk_size
#         end_idx = min((i + 1) * chunk_size, total_size)
#         chunk = model_bytes[start_idx:end_idx]
        
#         chunk_filename = os.path.join(output_dir, f'model_chunk_{i}.pkl')
#         with open(chunk_filename, 'wb') as f:
#             f.write(chunk)
        
#         chunk_size_mb = len(chunk) / (1024*1024)
#         print(f"Chunk {i}: {chunk_size_mb:.2f} MB")
    
#     # Save metadata about the chunks
#     metadata = {
#         'num_chunks': num_chunks,
#         'original_size': total_size,
#         'chunk_size': chunk_size
#     }
    
#     metadata_file = os.path.join(output_dir, 'chunks_metadata.pkl')
#     with open(metadata_file, 'wb') as f:
#         pickle.dump(metadata, f)
    
#     return num_chunks

# # Usage example
# if __name__ == "__main__":
#     input_model = "model_question_recommender.pkl"
#     output_directory = "model_chunks"
    
#     num_chunks = split_model(input_model, output_directory)
#     print(f"\nModel successfully split into {num_chunks} chunks in {output_directory}/")






















from flask import Flask, request, jsonify
from recommender import QuestionRecommender
import joblib

app = Flask(__name__)

# Load the model when the application starts
try:
    with open("model_question_recommender_optimized.pkl", "rb") as model_file:
        recommender = joblib.load(model_file) 
except Exception as e:
    print(f"Error loading model: {str(e)}")
    recommender = None

@app.route('/recommend', methods=['POST'])
def recommend_questions():
    try:
        # Get data from request
        data = request.get_json()
        
        if not data or 'questions' not in data:
            return jsonify({
                'error': 'Please provide questions in the request body'
            }), 400
            
        input_questions = data['questions']
        num_recommendations = data.get('num_recommendations', 8)  # Default to 8 if not specified
        
        # Validate input
        if not isinstance(input_questions, list):
            return jsonify({
                'error': 'Questions should be provided as a list'
            }), 400
            
        # Make predictions
        predictions = recommender.recommend_questions(input_questions, num_recommendations)
        
        # Return results
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
    app.run(debug=True, port=5000)


from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import List, Optional
from recommender import QuestionRecommender
import joblib

app = FastAPI()

# Pydantic model for request validation
class RecommendationRequest(BaseModel):
    questions: List[str]
    num_recommendations: Optional[int] = 8

# Load the model when the application starts
try:
    with open("model_question_recommender_optimized.pkl", "rb") as model_file:
        recommender = joblib.load(model_file)
except Exception as e:
    print(f"Error loading model: {str(e)}")
    recommender = None

@app.post("/recommend")
async def recommend_questions(request: RecommendationRequest):
    try:
        # Make predictions
        predictions = recommender.recommend_questions(
            request.questions, 
            request.num_recommendations
        )
        
        # Return results
        return {
            "recommended_questions": predictions,
            "input_questions": request.questions,
            "num_recommendations": request.num_recommendations
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

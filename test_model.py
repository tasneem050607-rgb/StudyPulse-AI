import pandas as pd
import joblib

# Load the trained AI model
model = joblib.load("studypulse_model.pkl")

# New student's performance
student = pd.DataFrame([{
    "quiz_score": 42,
    "previous_score": 50,
    "study_time": 25,
    "revision_count": 2,
    "topic_difficulty": 5
}])

# Ask the model for a prediction
prediction = model.predict(student)[0]

print("STUDYPULSE AI PREDICTION")
print("------------------------")
print("Learning Status:", prediction)
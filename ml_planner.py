import pandas as pd
import joblib

# Load trained ML model
model = joblib.load("studypulse_model.pkl")

# Student/topic data
topics = [
    {
        "name": "Op-Amps",
        "quiz_score": 88,
        "previous_score": 84,
        "study_time": 30,
        "revision_count": 4,
        "difficulty": 2
    },
    {
        "name": "Digital Logic",
        "quiz_score": 76,
        "previous_score": 72,
        "study_time": 25,
        "revision_count": 3,
        "difficulty": 3
    },
    {
        "name": "Transistors",
        "quiz_score": 42,
        "previous_score": 50,
        "study_time": 25,
        "revision_count": 2,
        "difficulty": 5
    },
    {
        "name": "Communication Systems",
        "quiz_score": 65,
        "previous_score": 60,
        "study_time": 20,
        "revision_count": 2,
        "difficulty": 4
    }
]

available_minutes = 120
days_to_exam = 7

# Convert days into exam urgency
if days_to_exam > 21:
    exam_urgency = 1
elif days_to_exam > 7:
    exam_urgency = 2
elif days_to_exam > 3:
    exam_urgency = 3
else:
    exam_urgency = 4

status_weight = {
    "Mastered": 1,
    "Needs Practice": 2,
    "Needs Attention": 3
}

# Predict learning status using ML
for topic in topics:

    student_data = pd.DataFrame([{
        "quiz_score": topic["quiz_score"],
        "previous_score": topic["previous_score"],
        "study_time": topic["study_time"],
        "revision_count": topic["revision_count"],
        "topic_difficulty": topic["difficulty"]
    }])

    prediction = model.predict(student_data)[0]

    topic["status"] = prediction

    # Calculate adaptive priority
    status_score = status_weight[prediction]
    difficulty_score = topic["difficulty"] / 5
    urgency_score = exam_urgency / 4

    topic["priority"] = (
        status_score
        + difficulty_score
        + urgency_score
    )

# Calculate total priority
total_priority = sum(topic["priority"] for topic in topics)

print("STUDYPULSE AI - AI GENERATED STUDY PLAN")
print("----------------------------------------")
print("Days to exam:", days_to_exam)
print("Available study time:", available_minutes, "minutes")
print("Exam urgency:", exam_urgency, "/ 4")
print()

total_allocated = 0

for topic in topics:

    allocated_time = round(
        available_minutes
        * topic["priority"]
        / total_priority
    )

    total_allocated += allocated_time

    print(
        topic["name"],
        "->",
        topic["status"],
        "->",
        allocated_time,
        "minutes"
    )

print()
print("Total allocated:", total_allocated, "minutes")
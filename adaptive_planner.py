# StudyPulse AI - Adaptive Study Planner

topics = [
    {
        "name": "Op-Amps",
        "status": "Mastered",
        "difficulty": 2
    },
    {
        "name": "Digital Logic",
        "status": "Needs Practice",
        "difficulty": 3
    },
    {
        "name": "Transistors",
        "status": "Needs Attention",
        "difficulty": 5
    },
    {
        "name": "Communication Systems",
        "status": "Needs Practice",
        "difficulty": 4
    }
]

available_minutes = 120

# Change this number to represent days remaining
days_to_exam = 7

# Convert days remaining into exam urgency
if days_to_exam > 21:
    exam_urgency = 1
elif days_to_exam > 7:
    exam_urgency = 2
elif days_to_exam > 3:
    exam_urgency = 3
else:
    exam_urgency = 4

# Learning-status priority
status_weight = {
    "Mastered": 1,
    "Needs Practice": 2,
    "Needs Attention": 3
}

# Calculate priority
for topic in topics:

    status_score = status_weight[topic["status"]]

    difficulty_score = topic["difficulty"] / 5

    urgency_score = exam_urgency / 4

    topic["priority"] = (
        status_score
        + difficulty_score
        + urgency_score
    )

# Total priority
total_priority = sum(topic["priority"] for topic in topics)

print("STUDYPULSE AI - ADAPTIVE STUDY PLAN")
print("-----------------------------------")
print("Available study time:", available_minutes, "minutes")
print("Days to exam:", days_to_exam)
print("Exam urgency:", exam_urgency, "/ 4")
print()

total_allocated = 0

for topic in topics:

    allocated_time = round(
        available_minutes
        * topic["priority"]
        / total_priority
    )

    topic["allocated_time"] = allocated_time
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

import pandas as pd
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
import joblib

# 1. Load our training dataset
data = pd.read_csv("training_data.csv")

# 2. Input features used by the ML model
features = [
    "quiz_score",
    "previous_score",
    "study_time",
    "revision_count",
    "topic_difficulty"
]

X = data[features]

# 3. The answer we want the model to predict
y = data["learning_status"]

# 4. Split the data into training and testing portions
X_train, X_test, y_train, y_test = train_test_split(
    X,
    y,
    test_size=0.25,
    random_state=42,
    stratify=y
)

# 5. Create the Random Forest model
model = RandomForestClassifier(
    n_estimators=100,
    random_state=42
)

# 6. Train the model
model.fit(X_train, y_train)

# 7. Test the trained model
predictions = model.predict(X_test)
accuracy = accuracy_score(y_test, predictions)

# 8. Save the trained model
joblib.dump(model, "studypulse_model.pkl")

print("MODEL TRAINED SUCCESSFULLY")
print("Test accuracy:", round(accuracy * 100, 2), "%")
print("Saved as: studypulse_model.pkl")
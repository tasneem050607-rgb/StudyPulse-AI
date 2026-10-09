\# StudyPulse AI — Adaptive Student Study Planner



\## 1. Project Overview



StudyPulse AI is an AI-assisted study planning application designed to help students identify topics that need more attention and organize their available study time.



The application uses a machine learning model to predict learning status from assessment-related data and creates an adaptive study schedule.



\## 2. Problem Statement



Students may struggle to identify weak topics, prioritize revision, and distribute limited study time effectively before examinations.



\## 3. Proposed Solution



StudyPulse AI combines machine learning predictions with a priority-based study planner to recommend how students can allocate their study time across topics.



\## 4. Key Features



\* Dashboard displaying sample quiz performance and learning status.

\* Machine learning predictions for topic learning status.

\* Subject assessment overview.

\* Adaptive study-time allocation.

\* Exam urgency settings.

\* Topic-specific study recommendations.



\## 5. Technology Stack



\* Python

\* Streamlit

\* Pandas

\* NumPy

\* Scikit-learn

\* Matplotlib

\* Plotly

\* Joblib



\## 6. Machine Learning



A Random Forest classifier is trained using a sample dataset containing quiz scores, previous scores, study time, revision count, and topic difficulty.



The predicted learning status is used by the dashboard and adaptive planner.



\*\*Prototype limitation:\*\* The current training dataset contains synthetic examples. Predictions are experimental and have not been scientifically validated.



\## 7. Project Structure



\* `app.py` — Streamlit application and dashboard.

\* `training\_data.csv` — Sample training dataset.

\* `train\_model.py` — Model training script.

\* `test\_model.py` — Model prediction test.

\* `adaptive\_planner.py` — Study planning logic.

\* `ml\_planner.py` — Machine-learning-based planning script.

\* `studypulse\_model.pkl` — Saved trained model.

\* `requirements.txt` — Python package dependencies.



\## 8. Installation and Setup



Install Python 3.12 and create a virtual environment.



Install dependencies:



```bash

pip install -r requirements.txt

```



If the trained model file is missing, run:



```bash

python train\_model.py

```



Start the application:



```bash

python -m streamlit run app.py

```



Open the local URL shown in the terminal.



\## 9. Usage



1\. Open the dashboard.

2\. Review the sample topic assessment data.

3\. Explore the My Subjects page.

4\. Adjust available study time and exam countdown in Study Planner.

5\. Review topic-specific suggestions in AI Recommendations.



\## 10. Testing



The model prediction script has been run successfully. The four Streamlit pages have also been opened and manually checked.



Further testing is required for deployment, different inputs, and other devices.



\## 11. Privacy and Limitations



The current prototype uses predefined sample assessment data. It does not yet provide persistent student accounts or permanent storage of user-edited scores.



The predictions are for educational demonstration only and should not be treated as definitive measurements of a student's ability.



\## 12. Future Improvements



\* Student accounts and persistent progress tracking.

\* Saving updated quiz scores.

\* Personalized weekly study schedules.

\* Larger, validated training datasets.

\* Live deployment and cross-device testing.



\## 13. Domain



AI for Education




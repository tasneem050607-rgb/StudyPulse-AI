import streamlit as st
import pandas as pd
import joblib

# -----------------------------------------
# STUDYPULSE AI - ADAPTIVE STUDY PLANNER
# -----------------------------------------

st.set_page_config(
    page_title="StudyPulse AI",
    page_icon="📚",
    layout="wide"
)

# -----------------------------------------
# LOAD MACHINE LEARNING MODEL
# -----------------------------------------

@st.cache_resource
def load_model():
    return joblib.load("studypulse_model.pkl")


try:
    model = load_model()
except Exception as e:
    st.error("Could not load the trained ML model.")
    st.write("Make sure studypulse_model.pkl exists in your project folder.")
    st.code(str(e))
    st.stop()


# -----------------------------------------
# SAMPLE STUDENT ASSESSMENT DATA
# -----------------------------------------

topics = pd.DataFrame({
    "Topic": [
        "Op-Amps",
        "Digital Logic",
        "Transistors",
        "Communication Systems"
    ],
    "Quiz Score": [88, 76, 42, 65],
    "Previous Score": [84, 72, 50, 60],
    "Study Time": [30, 25, 25, 20],
    "Revision Count": [4, 3, 2, 2],
    "Difficulty": [2, 3, 5, 4],
    "Study Minutes": [19, 20, 41, 40]
})


# -----------------------------------------
# PREDICT LEARNING STATUS USING ML
# -----------------------------------------

predictions = []

for _, topic in topics.iterrows():

    student_data = pd.DataFrame([{
        "quiz_score": topic["Quiz Score"],
        "previous_score": topic["Previous Score"],
        "study_time": topic["Study Time"],
        "revision_count": topic["Revision Count"],
        "topic_difficulty": topic["Difficulty"]
    }])

    prediction = model.predict(student_data)[0]
    predictions.append(prediction)

topics["Learning Status"] = predictions


# -----------------------------------------
# SIDEBAR NAVIGATION
# -----------------------------------------

st.sidebar.title("📚 StudyPulse AI")
st.sidebar.write("Your Adaptive Study Companion")

page = st.sidebar.radio(
    "Navigation",
    [
        "Dashboard",
        "My Subjects",
        "Study Planner",
        "AI Recommendations"
    ]
)

st.sidebar.divider()

st.sidebar.caption(
    "Personalized study planning using machine learning."
)


# -----------------------------------------
# DASHBOARD
# -----------------------------------------

if page == "Dashboard":

    st.title("📚 StudyPulse AI Dashboard")

    st.write(
        "Monitor your learning progress and organize "
        "your study time more effectively."
    )

    average_score = topics["Quiz Score"].mean()

    needs_attention = (
        topics["Learning Status"] == "Needs Attention"
    ).sum()

    col1, col2, col3, col4 = st.columns(4)

    col1.metric(
        "Average Quiz Score",
        f"{average_score:.1f}%"
    )

    col2.metric(
        "Topics Tracked",
        len(topics)
    )

    col3.metric(
        "Needs Attention",
        int(needs_attention)
    )

    col4.metric(
        "Study Time Available",
        "120 min"
    )

    st.divider()

    st.subheader("📊 Quiz Performance by Topic")

    chart_data = topics.set_index("Topic")[["Quiz Score"]]

    st.bar_chart(chart_data)

    st.subheader("🧠 ML Learning Status")

    st.dataframe(
        topics[
            ["Topic", "Quiz Score", "Difficulty", "Learning Status"]
        ],
        hide_index=True,
        use_container_width=True
    )

    st.subheader("⏱️ Current Sample Study Plan")

    st.dataframe(
        topics[["Topic", "Study Minutes"]],
        hide_index=True,
        use_container_width=True
    )

    st.caption(
        "Scores and assessments shown here are sample data."
    )


# -----------------------------------------
# MY SUBJECTS
# -----------------------------------------

elif page == "My Subjects":

    st.title("📖 My Subjects")

    st.write(
        "Review the assessment information for each topic."
    )

    st.dataframe(
        topics[
            [
                "Topic",
                "Quiz Score",
                "Previous Score",
                "Study Time",
                "Revision Count",
                "Difficulty",
                "Learning Status"
            ]
        ],
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Update a Sample Quiz Score")

    selected_topic = st.selectbox(
        "Choose a topic",
        topics["Topic"].tolist()
    )

    new_score = st.slider(
        "Latest quiz score",
        min_value=0,
        max_value=100,
        value=int(
            topics.loc[
                topics["Topic"] == selected_topic,
                "Quiz Score"
            ].iloc[0]
        )
    )

    if st.button("Update Score and Prediction"):

        row_index = topics.index[
            topics["Topic"] == selected_topic
        ][0]

        student_data = pd.DataFrame([{
            "quiz_score": new_score,
            "previous_score": topics.loc[
                row_index, "Previous Score"
            ],
            "study_time": topics.loc[
                row_index, "Study Time"
            ],
            "revision_count": topics.loc[
                row_index, "Revision Count"
            ],
            "topic_difficulty": topics.loc[
                row_index, "Difficulty"
            ]
        }])

        new_status = model.predict(student_data)[0]

        st.success(
            f"Predicted learning status for {selected_topic}: "
            f"{new_status}"
        )

        st.info(
            "This updates the displayed prediction for this action. "
            "The sample dataset itself is not permanently changed."
        )


# -----------------------------------------
# ADAPTIVE STUDY PLANNER
# -----------------------------------------

elif page == "Study Planner":

    st.title("⏱️ Adaptive Study Planner")

    available_minutes = st.slider(
        "How many minutes can you study today?",
        min_value=30,
        max_value=360,
        value=120,
        step=30
    )

    days_to_exam = st.number_input(
        "Days remaining until exam",
        min_value=1,
        max_value=365,
        value=7
    )

    if days_to_exam > 21:
        urgency_score = 0.25
    elif days_to_exam > 7:
        urgency_score = 0.50
    elif days_to_exam > 3:
        urgency_score = 0.75
    else:
        urgency_score = 1.00

    status_weight = {
        "Mastered": 1,
        "Needs Practice": 2,
        "Needs Attention": 3
    }

    priorities = []

    for _, topic in topics.iterrows():

        status_score = status_weight.get(
            topic["Learning Status"], 2
        )

        difficulty_score = topic["Difficulty"] / 5

        priority = (
            status_score
            + difficulty_score
            + urgency_score
        )

        priorities.append(priority)

    total_priority = sum(priorities)

    exact_minutes = [
        available_minutes * priority / total_priority
        for priority in priorities
    ]

    allocated_minutes = [
        int(minutes) for minutes in exact_minutes
    ]

    remaining_minutes = (
        available_minutes - sum(allocated_minutes)
    )

    order = sorted(
        range(len(exact_minutes)),
        key=lambda i: exact_minutes[i] - allocated_minutes[i],
        reverse=True
    )

    for i in order[:remaining_minutes]:
        allocated_minutes[i] += 1

    plan = pd.DataFrame({
        "Topic": topics["Topic"],
        "Learning Status": topics["Learning Status"],
        "Difficulty": topics["Difficulty"],
        "Recommended Minutes": allocated_minutes
    })

    col1, col2 = st.columns(2)

    col1.metric(
        "Available Study Time",
        f"{available_minutes} min"
    )

    col2.metric(
        "Days Until Exam",
        int(days_to_exam)
    )

    st.subheader("Your Personalized Study Schedule")

    st.dataframe(
        plan,
        hide_index=True,
        use_container_width=True
    )

    st.subheader("Study Time by Topic")

    st.bar_chart(
        plan,
        x="Topic",
        y="Recommended Minutes"
    )

    st.success(
        f"Total planned study time: "
        f"{sum(allocated_minutes)} minutes"
    )

    st.caption(
        "Study time is allocated using predicted learning status, "
        "topic difficulty, and exam urgency."
    )


# -----------------------------------------
# AI RECOMMENDATIONS
# -----------------------------------------

elif page == "AI Recommendations":

    st.title("🤖 AI Study Recommendations")

    st.write(
        "Suggestions based on sample quiz scores, "
        "topic difficulty, and ML-predicted learning status."
    )

    for _, topic in topics.iterrows():

        topic_name = topic["Topic"]
        score = topic["Quiz Score"]
        status = topic["Learning Status"]
        difficulty = topic["Difficulty"]

        st.subheader(f"📘 {topic_name}")

        st.write(f"Quiz Score: {score}%")
        st.write(f"Learning Status: {status}")

        if status == "Needs Attention":

            st.error(
                f"High priority: Spend extra time practising "
                f"{topic_name}. Review basic concepts and "
                "solve worked examples."
            )

        elif status == "Needs Practice":

            st.warning(
                f"Medium priority: Revise {topic_name} "
                "and solve practice questions."
            )

        else:

            st.success(
                f"Keep revising {topic_name} periodically "
                "to maintain your progress."
            )

        if difficulty >= 4:

            st.write(
                "💡 Tip: Break this difficult topic into "
                "smaller concepts and practise step by step."
            )

        if score < 50:

            st.write(
                "📌 Suggested action: Review the fundamentals "
                "before attempting another quiz."
            )

        st.divider()


# -----------------------------------------
# FOOTER
# -----------------------------------------

st.divider()

st.caption(
    "StudyPulse AI | Prototype dashboard | "
    "Learning support, not a replacement for teaching."
)

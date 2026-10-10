import streamlit as st
import pandas as pd
from datetime import date

from student_data import load_subjects, save_subjects

st.set_page_config(
    page_title="StudyPulse AI",
    page_icon="📚",
    layout="wide",
)

st.title("📚 StudyPulse AI")
st.caption("Adaptive study planning based on your subjects, exam dates, and learning progress.")

REQUIRED_COLUMNS = [
    "Subject",
    "Exam Date",
    "Quiz Score",
    "Previous Score",
    "Study Time",
    "Revision Count",
    "Difficulty",
    "Syllabus Completion",
]


def get_subjects():
    """Load saved subjects and make sure the expected columns exist."""
    df = load_subjects()

    if df is None or df.empty:
        return pd.DataFrame(columns=REQUIRED_COLUMNS)

    for column in REQUIRED_COLUMNS:
        if column not in df.columns:
            if column == "Syllabus Completion":
                df[column] = 0
            elif column == "Exam Date":
                df[column] = date.today().isoformat()
            elif column == "Subject":
                df[column] = ""
            else:
                df[column] = 0

    df = df[REQUIRED_COLUMNS].copy()
    for col in ["Quiz Score", "Previous Score", "Study Time", "Revision Count", "Difficulty", "Syllabus Completion"]:
        df[col] = pd.to_numeric(df[col], errors="coerce").fillna(0)

    df["Exam Date"] = pd.to_datetime(df["Exam Date"], errors="coerce").dt.date
    return df


def status_for_score(score):
    if score < 50:
        return "Needs Attention"
    if score < 75:
        return "Needs Practice"
    return "On Track"


def days_remaining(exam_date):
    if pd.isna(exam_date) or exam_date is None:
        return 0
    return max((exam_date - date.today()).days, 0)


def priority_for_row(row):
    """Transparent priority score: urgency + difficulty + learning needs."""
    days = days_remaining(row["Exam Date"])
    if days <= 2:
        urgency = 4.0
    elif days <= 7:
        urgency = 3.0
    elif days <= 14:
        urgency = 2.0
    elif days <= 30:
        urgency = 1.0
    else:
        urgency = 0.5

    score = float(row["Quiz Score"])
    difficulty = float(row["Difficulty"])
    completion = float(row["Syllabus Completion"])

    score_need = 3.0 if score < 50 else 2.0 if score < 75 else 0.5
    unfinished_need = (100 - completion) / 100 * 2.0
    difficulty_need = difficulty / 5
    return urgency + score_need + unfinished_need + difficulty_need


def build_plan(df, available_minutes):
    if df.empty:
        return pd.DataFrame()

    plan_df = df.copy()
    plan_df["Days Until Exam"] = plan_df["Exam Date"].apply(days_remaining)
    plan_df["Priority"] = plan_df.apply(priority_for_row, axis=1)

    priorities = plan_df["Priority"].tolist()
    total_priority = sum(priorities)
    if total_priority <= 0:
        allocations = [available_minutes // len(plan_df)] * len(plan_df)
    else:
        exact = [available_minutes * p / total_priority for p in priorities]
        allocations = [int(value) for value in exact]
        remainder = available_minutes - sum(allocations)
        remainder_order = sorted(
            range(len(exact)),
            key=lambda i: exact[i] - allocations[i],
            reverse=True,
        )
        for i in remainder_order[:remainder]:
            allocations[i] += 1

    plan_df["Recommended Minutes"] = allocations
    plan_df["Learning Status"] = plan_df["Quiz Score"].apply(status_for_score)
    plan_df = plan_df.sort_values(
        ["Priority", "Days Until Exam"],
        ascending=[False, True],
    )
    return plan_df


subjects = get_subjects()

with st.sidebar:
    st.header("📚 Navigation")
    page = st.radio(
        "Choose a page",
        ["Dashboard", "Student Profile", "Study Planner", "AI Recommendations"],
    )
    st.divider()
    st.caption("Your saved subject details are stored in a local CSV file in this project.")


if page == "Dashboard":
    st.header("Your Learning Dashboard")
    st.write("A quick view of your subjects, progress, and upcoming exams.")

    if subjects.empty:
        st.info("You haven't added any subjects yet. Open **Student Profile** to add your first subject.")
    else:
        average_score = subjects["Quiz Score"].mean()
        upcoming = sum(
            0 <= days_remaining(exam_date) <= 7
            for exam_date in subjects["Exam Date"]
        )
        avg_completion = subjects["Syllabus Completion"].mean()

        c1, c2, c3, c4 = st.columns(4)
        c1.metric("Subjects tracked", len(subjects))
        c2.metric("Average quiz score", f"{average_score:.1f}%")
        c3.metric("Syllabus completed", f"{avg_completion:.0f}%")
        c4.metric("Exams in next 7 days", upcoming)

        st.subheader("Subject progress")
        display = subjects.copy()
        display["Learning Status"] = display["Quiz Score"].apply(status_for_score)
        st.dataframe(
            display[["Subject", "Exam Date", "Quiz Score", "Syllabus Completion", "Difficulty", "Learning Status"]],
            hide_index=True,
            use_container_width=True,
        )

        st.subheader("Quiz scores")
        chart_df = subjects.set_index("Subject")[["Quiz Score"]]
        st.bar_chart(chart_df)

        st.subheader("Upcoming exams")
        upcoming_df = subjects.copy()
        upcoming_df["Days Until Exam"] = upcoming_df["Exam Date"].apply(days_remaining)
        upcoming_df = upcoming_df.sort_values("Days Until Exam")
        st.dataframe(
            upcoming_df[["Subject", "Exam Date", "Days Until Exam"]],
            hide_index=True,
            use_container_width=True,
        )


elif page == "Student Profile":
    st.header("🎓 Student Profile")
    st.write("Add your real subjects and update their details. Saved subjects remain available after app reruns.")

    with st.form("add_subject_form", clear_on_submit=True):
        subject_name = st.text_input("Subject name")
        exam_date = st.date_input("Exam date", value=date.today())
        quiz_score = st.number_input("Latest quiz score (%)", min_value=0, max_value=100, value=50)
        previous_score = st.number_input("Previous quiz score (%)", min_value=0, max_value=100, value=50)
        study_time = st.number_input("Study time so far (minutes)", min_value=0, max_value=10000, value=60)
        revision_count = st.number_input("Number of revisions", min_value=0, max_value=100, value=0)
        difficulty = st.slider("Subject difficulty (1 = easy, 5 = difficult)", min_value=1, max_value=5, value=3)
        syllabus_completion = st.slider("Syllabus completed (%)", min_value=0, max_value=100, value=0)
        submitted = st.form_submit_button("Save Subject")

    if submitted:
        cleaned_name = subject_name.strip()
        current = get_subjects()
        if not cleaned_name:
            st.error("Please enter a subject name.")
        elif exam_date < date.today():
            st.error("Please choose today or a future exam date.")
        elif not current.empty and cleaned_name.casefold() in current["Subject"].astype(str).str.casefold().tolist():
            st.error("This subject already exists. Use the update section below to edit it.")
        else:
            new_row = pd.DataFrame([{
                "Subject": cleaned_name,
                "Exam Date": exam_date.isoformat(),
                "Quiz Score": int(quiz_score),
                "Previous Score": int(previous_score),
                "Study Time": int(study_time),
                "Revision Count": int(revision_count),
                "Difficulty": int(difficulty),
                "Syllabus Completion": int(syllabus_completion),
            }])
            combined = pd.concat([current, new_row], ignore_index=True)
            combined["Exam Date"] = combined["Exam Date"].apply(
                lambda x: x.isoformat() if hasattr(x, "isoformat") else str(x)
            )
            save_subjects(combined[REQUIRED_COLUMNS])
            st.success(f"{cleaned_name} saved successfully.")
            st.rerun()

    st.subheader("Your saved subjects")
    current = get_subjects()
    if current.empty:
        st.info("No subjects saved yet. Add your first subject above.")
    else:
        st.dataframe(current, hide_index=True, use_container_width=True)

        st.subheader("Update an existing subject")
        subject_to_edit = st.selectbox("Choose a subject to update", current["Subject"].tolist())
        row = current[current["Subject"] == subject_to_edit].iloc[0]
        with st.form("update_subject_form"):
            updated_exam_date = st.date_input(
                "Updated exam date",
                value=row["Exam Date"] if row["Exam Date"] else date.today(),
                key="updated_exam_date",
            )
            updated_quiz = st.number_input(
                "Updated latest quiz score (%)", 0, 100, int(row["Quiz Score"]), key="updated_quiz"
            )
            updated_previous = st.number_input(
                "Updated previous quiz score (%)", 0, 100, int(row["Previous Score"]), key="updated_previous"
            )
            updated_study_time = st.number_input(
                "Updated study time so far (minutes)", 0, 10000, int(row["Study Time"]), key="updated_study_time"
            )
            updated_revisions = st.number_input(
                "Updated revision count", 0, 100, int(row["Revision Count"]), key="updated_revisions"
            )
            updated_difficulty = st.slider(
                "Updated difficulty", 1, 5, max(1, min(5, int(row["Difficulty"]))), key="updated_difficulty"
            )
            updated_completion = st.slider(
                "Updated syllabus completion (%)", 0, 100,
                max(0, min(100, int(row["Syllabus Completion"]))), key="updated_completion"
            )
            update_clicked = st.form_submit_button("Save Changes")

        if update_clicked:
            if updated_exam_date < date.today():
                st.error("Please choose today or a future exam date.")
            else:
                current.loc[current["Subject"] == subject_to_edit, "Exam Date"] = updated_exam_date.isoformat()
                current.loc[current["Subject"] == subject_to_edit, "Quiz Score"] = int(updated_quiz)
                current.loc[current["Subject"] == subject_to_edit, "Previous Score"] = int(updated_previous)
                current.loc[current["Subject"] == subject_to_edit, "Study Time"] = int(updated_study_time)
                current.loc[current["Subject"] == subject_to_edit, "Revision Count"] = int(updated_revisions)
                current.loc[current["Subject"] == subject_to_edit, "Difficulty"] = int(updated_difficulty)
                current.loc[current["Subject"] == subject_to_edit, "Syllabus Completion"] = int(updated_completion)
                current["Exam Date"] = current["Exam Date"].apply(
                    lambda x: x.isoformat() if hasattr(x, "isoformat") else str(x)
                )
                save_subjects(current[REQUIRED_COLUMNS])
                st.success(f"{subject_to_edit} updated.")
                st.rerun()

        if st.button("Delete selected subject", type="secondary"):
            remaining = current[current["Subject"] != subject_to_edit].copy()
            remaining["Exam Date"] = remaining["Exam Date"].apply(
                lambda x: x.isoformat() if hasattr(x, "isoformat") else str(x)
            )
            save_subjects(remaining[REQUIRED_COLUMNS])
            st.success(f"{subject_to_edit} deleted.")
            st.rerun()


elif page == "Study Planner":
    st.header("🗓️ Adaptive Study Planner")
    st.write("Choose how much time you have today. Study time is distributed using exam urgency, quiz score, difficulty, and unfinished syllabus.")

    if subjects.empty:
        st.warning("Add at least one subject in **Student Profile** before generating a timetable.")
    else:
        available_hours = st.number_input(
            "Available study hours today",
            min_value=0.5,
            max_value=16.0,
            value=2.0,
            step=0.5,
        )
        available_minutes = int(round(available_hours * 60))
        plan = build_plan(subjects, available_minutes)

        a, b = st.columns(2)
        a.metric("Study time available", f"{available_minutes} minutes")
        b.metric("Subjects included", len(plan))

        st.subheader("Today's recommended timetable")
        view = plan[[
            "Subject", "Exam Date", "Days Until Exam", "Quiz Score",
            "Syllabus Completion", "Learning Status", "Recommended Minutes"
        ]].copy()
        view = view.rename(columns={
            "Subject": "Subject",
            "Exam Date": "Exam date",
            "Days Until Exam": "Days until exam",
            "Quiz Score": "Quiz score (%)",
            "Syllabus Completion": "Syllabus completed (%)",
            "Learning Status": "Learning status",
            "Recommended Minutes": "Recommended minutes",
        })
        st.dataframe(view, hide_index=True, use_container_width=True)
        st.bar_chart(plan.set_index("Subject")[["Recommended Minutes"]])

        st.success(f"Total allocated: {int(plan['Recommended Minutes'].sum())} minutes.")
        st.caption("This is a rule-based planning recommendation, not a guaranteed measure of learning outcomes.")


elif page == "AI Recommendations":
    st.header("💡 Personalized Study Recommendations")
    st.write("Suggestions are generated from the subject details you entered.")

    if subjects.empty:
        st.info("Add subjects in Student Profile to receive recommendations.")
    else:
        for _, row in subjects.iterrows():
            name = row["Subject"]
            score = float(row["Quiz Score"])
            completion = float(row["Syllabus Completion"])
            difficulty = int(row["Difficulty"])
            days = days_remaining(row["Exam Date"])

            st.subheader(f"📘 {name}")
            st.write(
                f"Quiz score: {score:.0f}% · Syllabus completed: {completion:.0f}% · "
                f"Exam in {days} day(s)"
            )

            if score < 50:
                st.error("High priority: revise the core concepts, review worked examples, and practise a small set of basic questions.")
            elif score < 75:
                st.warning("Medium priority: review mistakes from your last quiz and complete a focused practice session.")
            else:
                st.success("Your quiz score is strong. Use spaced revision and a short self-test to maintain it.")

            if completion < 50:
                st.write("📌 Much of the syllabus remains: split it into smaller topics and mark each topic complete as you study.")
            elif completion < 100:
                st.write("📌 Finish the remaining syllabus, then use practice questions to check understanding.")

            if difficulty >= 4:
                st.write("🧩 This subject feels difficult: use 25-minute focused blocks and take short breaks.")
            if days <= 3:
                st.write("⏰ Your exam is very close: prioritize the most important unfinished topics and avoid trying to learn everything at once.")

            st.divider()


st.divider()
st.caption("StudyPulse AI · Student planning prototype · Recommendations support learning and do not replace teaching.")

import streamlit as st
import pandas as pd

# ============================================================
# PAGE CONFIGURATION
# ============================================================

st.set_page_config(
    page_title="SmartStudy Agent",
    page_icon="🎓",
    layout="wide"
)

# Custom CSS for UI Badges and Visual Polish
st.markdown("""
    <style>
    .stProgress > div > div > div > div {
        background-color: #4CAF50;
    }
    .badge-very-high { color: #FF4B4B; font-weight: bold; }
    .badge-high { color: #FFA500; font-weight: bold; }
    .badge-medium { color: #FACA2B; font-weight: bold; }
    .badge-low { color: #2196F3; font-weight: bold; }
    </style>
""", unsafe_allow_html=True)


# ============================================================
# AGENT LOGIC & HELPER FUNCTIONS
# ============================================================

PRIORITY_WEIGHTS = {
    "VERY HIGH": 4,
    "HIGH": 3,
    "MEDIUM": 2,
    "LOW": 1
}

PRIORITY_COLORS = {
    "VERY HIGH": "🔴",
    "HIGH": "🟠",
    "MEDIUM": "🟡",
    "LOW": "🟢"
}

def calculate_priority(days_left: int, difficulty: str, confidence: str) -> str:
    """Calculates a priority level based on deadline, difficulty, and confidence."""
    score = 0

    # Exam urgency
    if days_left <= 2:
        score += 5
    elif days_left <= 5:
        score += 4
    elif days_left <= 10:
        score += 3
    else:
        score += 1

    # Subject Difficulty
    if difficulty == "High":
        score += 3
    elif difficulty == "Medium":
        score += 2
    else:
        score += 1

    # Student Confidence
    if confidence == "Low":
        score += 3
    elif confidence == "Medium":
        score += 2
    else:
        score += 1

    # Priority Categorization
    if score >= 9:
        return "VERY HIGH"
    elif score >= 7:
        return "HIGH"
    elif score >= 5:
        return "MEDIUM"
    else:
        return "LOW"


def get_recommendation(subject: dict) -> str:
    """Generates dynamic agent advice per subject."""
    if subject["days_left"] <= 2:
        return "Exam is imminent. Focus exclusively on active recall, high-yield revision, and past papers."
    elif subject["confidence"] == "Low":
        return "Low confidence area. Begin with core fundamentals before advancing to complex problems."
    elif subject["difficulty"] == "High":
        return "High difficulty rating. Allocate focus to solving worked examples and step-by-step practice."
    else:
        return "Steady state. Maintain periodic revision and review key concepts."


def create_study_plan(subjects: list, total_hours: float) -> list:
    """Computes priority, dynamic weighted time allocation, and advice for all subjects."""
    # Step 1: Compute Priority and Base Weights
    total_weight = 0
    for subject in subjects:
        priority = calculate_priority(
            subject["days_left"],
            subject["difficulty"],
            subject["confidence"]
        )
        subject["priority"] = priority
        subject["weight"] = PRIORITY_WEIGHTS[priority]
        subject["recommendation"] = get_recommendation(subject)
        total_weight += subject["weight"]

    # Step 2: Proportionally allocate available study hours
    for subject in subjects:
        allocated_hours = (subject["weight"] / total_weight) * total_hours
        subject["study_time"] = round(allocated_hours, 2)

    # Step 3: Sort subjects by priority order, then by days left
    subjects.sort(
        key=lambda x: (PRIORITY_WEIGHTS[x["priority"]], -x["days_left"]),
        reverse=True
    )

    return subjects


# ============================================================
# HEADER
# ============================================================

st.title("🎓 SmartStudy Agent")
st.caption("Intelligent Automated Workload & Revision Planner")

st.markdown(
    "SmartStudy evaluates your upcoming exam deadlines, subjective difficulty, "
    "and current confidence levels to dynamically generate an optimal, time-budgeted study schedule."
)

st.divider()


# ============================================================
# SIDEBAR CONTROLS
# ============================================================

st.sidebar.header("👤 Student Profile")

student_name = st.sidebar.text_input(
    "Student Name",
    placeholder="e.g. Alex Johnson"
)

total_hours = st.sidebar.number_input(
    "Available Study Hours Today",
    min_value=0.5,
    max_value=24.0,
    value=4.0,
    step=0.5,
    help="Total hours you can dedicate to studying today."
)

number_of_subjects = st.sidebar.number_input(
    "Number of Subjects to Plan",
    min_value=1,
    max_value=10,
    value=3,
    step=1
)


# ============================================================
# SUBJECT INPUT SECTION
# ============================================================

st.header("📚 Input Subject Parameters")

raw_subjects = []

for i in range(int(number_of_subjects)):
    with st.expander(f"Book Subject {i + 1}", expanded=True):
        col1, col2, col3, col4 = st.columns([3, 2, 2, 2])

        with col1:
            subject_name = st.text_input(
                "Subject Name",
                key=f"name_{i}",
                placeholder=f"e.g. Calculus" if i == 0 else "e.g. Physics"
            )

        with col2:
            days_left = st.number_input(
                "Days Until Exam",
                min_value=0,
                max_value=365,
                value=7,
                key=f"days_{i}"
            )

        with col3:
            difficulty = st.selectbox(
                "Difficulty Level",
                ["Low", "Medium", "High"],
                index=1,
                key=f"difficulty_{i}"
            )

        with col4:
            confidence = st.selectbox(
                "Current Confidence",
                ["Low", "Medium", "High"],
                index=1,
                key=f"confidence_{i}"
            )

        if subject_name.strip():
            raw_subjects.append({
                "name": subject_name.strip(),
                "days_left": days_left,
                "difficulty": difficulty,
                "confidence": confidence
            })

st.divider()

generate = st.button(
    "⚡ Generate Optimization Plan",
    type="primary",
    use_container_width=True
)


# ============================================================
# GENERATION & OUTPUT DISPLAY
# ============================================================

if generate:
    if not student_name.strip():
        st.error("⚠️ Please enter your name in the sidebar before generating.")
    elif len(raw_subjects) == 0:
        st.error("⚠️ Please fill in at least one Subject Name above.")
    else:
        study_plan = create_study_plan(raw_subjects, total_hours)

        st.success(f"🎉 Optimized plan generated successfully for **{student_name}**!")

        # Top Level Metrics
        st.header("📊 Executive Plan Overview")
        col1, col2, col3, col4 = st.columns(4)
        
        col1.metric("Total Subjects", len(study_plan))
        col2.metric("Allocated Hours", f"{total_hours} hrs")
        col3.metric("Top Priority Target", study_plan[0]["name"])
        col4.metric("Top Priority Time", f"{study_plan[0]['study_time']} hrs")

        st.subheader("⏱️ Daily Time Allocation Breakdown")
        
        # Display progress allocation visualization
        for sub in study_plan:
            ratio = sub["study_time"] / total_hours
            st.write(f"**{sub['name']}** — {sub['study_time']} hrs ({int(ratio * 100)}%)")
            st.progress(ratio)

        st.divider()

        # Detailed Breakdown & Cards
        st.header("📋 Priority Action Schedule")

        for idx, subject in enumerate(study_plan, start=1):
            icon = PRIORITY_COLORS.get(subject["priority"], "⚪")
            
            with st.container():
                st.subheader(f"{idx}. {icon} {subject['name']}")
                
                col1, col2, col3, col4 = st.columns(4)
                col1.metric("Priority Rank", subject["priority"])
                col2.metric("Days Remaining", f"{subject['days_left']} d")
                col3.metric("Difficulty", subject["difficulty"])
                col4.metric("Target Study Time", f"{subject['study_time']} hrs")

                st.info(f"💡 **Agent Strategy Recommendation:** {subject['recommendation']}")
                st.write("")

        # Data Frame Overview
        st.header("📄 Consolidated Data Table")
        df = pd.DataFrame(study_plan)[
            ["name", "priority", "study_time", "days_left", "difficulty", "confidence"]
        ]
        df.columns = [
            "Subject Name", "Priority Rank", "Allocated Time (hrs)", 
            "Days Left", "Difficulty", "Confidence"
        ]
        st.dataframe(df, use_container_width=True)

        st.divider()

        # Strategic Action Plan Summary
        st.header("🎯 Immediate Next Steps")
        top_subject = study_plan[0]
        
        st.success(f"### 🚀 Start with **{top_subject['name']}**")
        st.write(
            f"Set a timer for **{top_subject['study_time']} hours**. "
            f"This task is prioritized first due to its rating of **{top_subject['priority']} priority** "
            f"with only **{top_subject['days_left']} days** remaining until assessment."
        )


# ============================================================
# ARCHITECTURE EXPLANATION
# ============================================================

st.divider()
st.header("🧠 How SmartStudy Works")

col1, col2, col3, col4 = st.columns(4)

with col1:
    st.markdown("#### 1️⃣ Observe")
    st.caption("Gathers exam dates, difficulty levels, confidence, and total available hours.")

with col2:
    st.markdown("#### 2️⃣ Weight Analysis")
    st.caption("Evaluates urgency vs difficulty to rank tasks into discrete priority tiers.")

with col3:
    st.markdown("#### 3️⃣ Normalized Allocation")
    st.caption("Distributes exact study hours dynamically using proportional priority weighting.")

with col4:
    st.markdown("#### 4️⃣ Strategy Routing")
    st.caption("Applies automated heuristic advice catered to deadline proximity.")
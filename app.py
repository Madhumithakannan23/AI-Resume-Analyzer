
import streamlit as st
import plotly.express as px
from PyPDF2 import PdfReader
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from io import BytesIO
from datetime import date
import re
from html import escape

st.set_page_config(
    page_title="AI Resume Analyzer",
    page_icon="📄",
    layout="wide"
)

st.title("📄 AI Resume Analyzer")
st.write("Analyze your resume and discover ways to improve it.")
st.divider()

job_roles = {
    "Python Developer": [
        "python", "sql", "data structures", "django",
        "flask", "git", "problem solving",
        "communication", "object oriented programming"
    ],
    "Data Analyst": [
        "python", "sql", "excel", "power bi",
        "data analysis", "pandas", "numpy",
        "communication", "problem solving"
    ],
    "Machine Learning Engineer": [
        "python", "machine learning", "deep learning",
        "tensorflow", "scikit-learn", "pandas",
        "numpy", "sql", "data structures"
    ]
}

section_patterns = {
    "Education": r"\b(education|academic background|qualification)\b",
    "Skills": r"\b(skills|technical skills|key skills)\b",
    "Projects": r"\b(projects|personal projects|academic projects)\b",
    "Experience": r"\b(experience|work experience|internship)\b",
    "Certifications": r"\b(certifications|certificates|licenses)\b"
}

weak_phrases = [
    "hardworking",
    "team player",
    "good communication skills",
    "responsible for",
    "worked on",
    "helped with",
    "fast learner"
]

def analyze_sections(text):
    found = []
    missing = []

    for section, pattern in section_patterns.items():
        if re.search(pattern, text, re.IGNORECASE):
            found.append(section)
        else:
            missing.append(section)

    return found, missing


def analyze_projects(text):
    project_match = re.search(
        r"(projects|personal projects|academic projects)(.*?)(experience|education|certifications|$)",
        text,
        re.IGNORECASE | re.DOTALL
    )

    if not project_match:
        return 0, [
            "Add a separate Projects section to your resume."
        ]

    project_text = project_match.group(2).lower()
    score = 0
    suggestions = []

    if len(project_text.split()) >= 30:
        score += 1
    else:
        suggestions.append(
            "Add more details about your project."
        )

    if re.search(
        r"\b(python|java|sql|html|css|javascript|machine learning|django|flask)\b",
        project_text
    ):
        score += 1
    else:
        suggestions.append(
            "Mention the technologies used in your projects."
        )

    if re.search(
        r"\b(developed|built|created|designed|implemented|automated)\b",
        project_text
    ):
        score += 1
    else:
        suggestions.append(
            "Use action words to explain your contribution."
        )

    if re.search(
        r"\b(\d+%|\d+\+|\d+\s*(users|records|customers|hours))\b",
        project_text
    ):
        score += 1
    else:
        suggestions.append(
            "Add measurable results if you have them."
        )

    return score, suggestions


def find_weak_phrases(text):
    found = []

    for phrase in weak_phrases:
        if phrase in text.lower():
            found.append(phrase)

    return found


col1, col2 = st.columns(2)

with col1:
    st.subheader("📂 Upload Resume")
    resume = st.file_uploader(
        "Upload your PDF resume",
        type=["pdf"]
    )

with col2:
    st.subheader("💼 Select Job Role")
    selected_role = st.selectbox(
        "Choose your target job role",
        list(job_roles.keys())
    )

    st.write("Required skills:")
    st.write(", ".join(job_roles[selected_role]))

if st.button("🔍 Analyze My Resume", type="primary"):

    if resume is None:
        st.error("Please upload your resume.")

    else:
        try:
            reader = PdfReader(resume)
            resume_text = ""

            for page in reader.pages:
                resume_text += page.extract_text() or ""

            resume_text = resume_text.lower()

            if not resume_text.strip():
                st.error("Could not extract text. Please upload a text-based PDF.")

            else:
                required_skills = job_roles[selected_role]

                matched_skills = [
                    skill for skill in required_skills
                    if skill in resume_text
                ]

                missing_skills = [
                    skill for skill in required_skills
                    if skill not in resume_text
                ]

                ats_score = (
                    len(matched_skills) / len(required_skills)
                ) * 100

                found_sections, missing_sections = analyze_sections(
                    resume_text
                )

                project_score, project_suggestions = analyze_projects(
                    resume_text
                )

                weak_words = find_weak_phrases(resume_text)

                section_score = (
                    len(found_sections) / len(section_patterns)
                ) * 100

                project_percentage = (project_score / 4) * 100

                improvement_score = (
                    section_score * 0.4
                    + ats_score * 0.4
                    + project_percentage * 0.2
                )

                suggestions = []

                for section in missing_sections:
                    suggestions.append(
                        f"Add a clear {section} section."
                    )

                suggestions.extend(project_suggestions)

                for word in weak_words:
                    suggestions.append(
                        f"Replace '{word}' with a specific example or achievement."
                    )

                for skill in missing_skills:
                    suggestions.append(
                        f"Learn or highlight {skill} if you have this skill."
                    )

                if not suggestions:
                    suggestions.append(
                        "Your resume covers all the checks in this analysis."
                    )

                st.session_state["analysis"] = {
                    "role": selected_role,
                    "ats_score": ats_score,
                    "improvement_score": improvement_score,
                    "matched": matched_skills,
                    "missing": missing_skills,
                    "found_sections": found_sections,
                    "missing_sections": missing_sections,
                    "project_score": project_score,
                    "project_suggestions": project_suggestions,
                    "weak_words": weak_words,
                    "suggestions": suggestions
                }

        except Exception as e:
            st.error(f"Error: {e}")


if "analysis" in st.session_state:

    result = st.session_state["analysis"]

    st.divider()
    st.header("📊 Resume Analysis Dashboard")

    c1, c2, c3 = st.columns(3)

    c1.metric(
        "ATS Match Score",
        f"{result['ats_score']:.1f}%"
    )

    c2.metric(
        "Resume Improvement Score",
        f"{result['improvement_score']:.1f}%"
    )

    c3.metric(
        "Matched Skills",
        len(result["matched"])
    )

    st.subheader("🎯 Resume Improvement Progress")
    st.progress(int(result["improvement_score"]))

    st.subheader("📋 Resume Section Analysis")

    left, right = st.columns(2)

    with left:
        st.write("✅ Sections Found")

        for section in result["found_sections"]:
            st.success(section)

    with right:
        st.write("❌ Sections Missing")

        for section in result["missing_sections"]:
            st.warning(section)

    st.divider()

    st.subheader("💻 Skills Analysis")

    left, right = st.columns(2)

    with left:
        st.write("✅ Matched Skills")

        for skill in result["matched"]:
            st.success(skill)

    with right:
        st.write("❌ Missing Skills")

        for skill in result["missing"]:
            st.warning(skill)

    st.divider()

    st.subheader("🚀 Project Analysis")

    st.metric(
        "Project Quality Checks",
        f"{result['project_score']} / 4"
    )

    for suggestion in result["project_suggestions"]:
        st.info(suggestion)

    st.divider()

    st.subheader("✍️ Weak Phrase Detection")

    if result["weak_words"]:
        for word in result["weak_words"]:
            st.warning(f"Consider improving: {word}")
    else:
        st.success("No common weak phrases detected.")

    st.divider()

    st.subheader("📈 Skills Visualization")

    chart_data = {
        "Status": ["Matched Skills", "Missing Skills"],
        "Count": [
            len(result["matched"]),
            len(result["missing"])
        ]
    }

    fig = px.pie(
        chart_data,
        names="Status",
        values="Count",
        title="Resume Skill Analysis",
        hole=0.4
    )

    st.plotly_chart(fig, width="stretch")

    st.divider()

    st.subheader("💡 Personalized Improvement Suggestions")

    for suggestion in result["suggestions"]:
        st.write("• " + suggestion)

    st.divider()

    pdf_buffer = BytesIO()

    document = SimpleDocTemplate(
        pdf_buffer,
        pagesize=A4
    )

    styles = getSampleStyleSheet()
    content = []

    content.append(
        Paragraph("AI RESUME ANALYZER REPORT", styles["Title"])
    )

    content.append(Spacer(1, 20))

    content.append(
        Paragraph(f"Date: {date.today()}", styles["Normal"])
    )

    content.append(
        Paragraph(
            f"Target Job Role: {escape(result['role'])}",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            f"ATS Match Score: {result['ats_score']:.1f}%",
            styles["Heading2"]
        )
    )

    content.append(
        Paragraph(
            f"Resume Improvement Score: {result['improvement_score']:.1f}%",
            styles["Heading2"]
        )
    )

    content.append(Spacer(1, 15))

    report_sections = [
        ("Matched Skills", result["matched"]),
        ("Missing Skills", result["missing"]),
        ("Sections Found", result["found_sections"]),
        ("Sections Missing", result["missing_sections"]),
        ("Weak Phrases", result["weak_words"]),
        ("Improvement Suggestions", result["suggestions"])
    ]

    for heading, items in report_sections:
        content.append(
            Paragraph(heading, styles["Heading2"])
        )

        if items:
            for item in items:
                content.append(
                    Paragraph(
                        escape(str(item)),
                        styles["Normal"]
                    )
                )
        else:
            content.append(
                Paragraph("None", styles["Normal"])
            )

        content.append(Spacer(1, 12))

    document.build(content)

    st.download_button(
        "📥 Download Complete PDF Report",
        data=pdf_buffer.getvalue(),
        file_name="AI_Resume_Analyzer_Report.pdf",
        mime="application/pdf"
    )

st.divider()

st.caption(
    "AI Resume Analyzer | Python | Streamlit | Plotly | ReportLab"
)

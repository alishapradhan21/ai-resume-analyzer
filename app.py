import streamlit as st
from backend import extract_text_from_pdf, analyze_resume, save_result, get_history, COMPANY_REQUIREMENTS

# Page config
st.set_page_config(page_title="AI Resume Analyzer", layout="centered")

# Load your CSS once
with open('styles.css') as f:
    st.markdown(f"<style>{f.read()}</style>", unsafe_allow_html=True)

# Title and description
st.title("📄 AI Resume Analyzer")
st.caption("Enhance your resume to match your dream job role and company!")

# Main form for user input
with st.form("resume_form"):
    name = st.text_input("👤 Your Name")
    experience = st.radio("💼 Are you a...", ["Fresher", "Experienced"])
    company = st.selectbox("🏢 Target Company", list(COMPANY_REQUIREMENTS.keys()))
    designation = st.selectbox("🎯 Job Role", list(COMPANY_REQUIREMENTS[company].keys()))
    resume = st.file_uploader("📄 Upload your Resume (PDF only)", type=["pdf"])
    submitted = st.form_submit_button("🔍 Submit for Analysis")

# Handle submission and display results
if submitted:
    if not name.strip():
        st.error("Please enter your name.")
    elif resume is None:
        st.error("Please upload your resume (PDF format).")
    else:
        with st.spinner("Analyzing your resume..."):
            resume_text = extract_text_from_pdf(resume)
            result = analyze_resume(resume_text, company, designation, experience)
            save_result(name, company, designation, experience, result)

        st.markdown("### 🎯 Skill Match Score")
        st.success(f"✅ Your Score: {result['score']}%")

        st.markdown("### 🧠 Skills Found")
        st.markdown(", ".join(result['skills_found']) or "❌ None found")

        st.markdown("### ⚠️ Suggestions")
        for tip in result["tips"]:
            st.markdown(f"- {tip}")

        st.markdown("### ✅ ATS Format Suggestions")
        st.info(result["ats_format"])

        if result.get("career_objective"):
            st.markdown("### ✍️ Career Objective Suggestion")
            st.success(result["career_objective"])

        st.markdown("---")
        st.markdown("### 🛠️ Useful AI Resume Tools")
        st.markdown("""
        <div style='display: flex; flex-wrap: wrap; gap: 10px;'>
            <a href='https://resumeworded.com/' target='_blank'><button class='tool-btn'>ResumeWorded</button></a>
            <a href='https://enhancv.com/' target='_blank'><button class='tool-btn'>Enhancv</button></a>
            <a href='https://zety.com/resume-builder' target='_blank'><button class='tool-btn'>Zety Resume Builder</button></a>
            <a href='https://rezi.ai/' target='_blank'><button class='tool-btn'>Rezi.ai</button></a>
        </div>
        """, unsafe_allow_html=True)

# Optional admin panel for past results
with st.expander("🧾 Admin: View Past Analyses"):
    history = get_history()
    if history:
        st.markdown("#### Analysis History:")
        for row in history:
            st.write(f"{row[5]} - {row[0]} ({row[3]}) → {row[1]} / {row[2]} — Score: {row[4]}%")
    else:
        st.info("No records found.")

import streamlit as st
import google.generativeai as genai
import docx2txt
import PyPDF2
import re

# Configure Gemini (Free Tier)
genai.configure(api_key=st.secrets["GEMINI_API_KEY"])  # Set in Streamlit Secrets

# Initialize the model
model = genai.GenerativeModel('gemini-1.5-pro-latest')  # Updated model name

def analyze_with_gemini(resume_text: str, jd_text: str):
    prompt = f"""
    Analyze this resume against the job description and provide:
    
    1. Fit Score (0-100) with justification
    2. Top 3 matching skills with evidence
    3. Top 3 missing qualifications
    4. Summary (3-4 sentences)
    
    ---JOB DESCRIPTION---\n{jd_text}\n---
    ---RESUME---\n{resume_text}\n---
    """
    
    try:
        response = model.generate_content(prompt)
        return response.text
    except Exception as e:
        st.error(f"Gemini error: {str(e)}")
        return None

# File extraction function (same as before)
def extract_text_from_file(uploaded_file):
    try:
        if uploaded_file.type == "application/pdf":
            reader = PyPDF2.PdfReader(uploaded_file)
            text = " ".join(page.extract_text() for page in reader.pages if page.extract_text())
        elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document", "application/msword"]:
            text = docx2txt.process(uploaded_file)
        else:
            text = uploaded_file.read().decode("utf-8")
        return text.strip()
    except Exception as e:
        st.error(f"File error: {str(e)}")
        return ""

# Streamlit UI (same layout)
st.set_page_config(page_title="Resume Matcher (Gemini)", layout="wide")
st.title("🔍 AI Resume Matcher (Powered by Gemini)")

with st.form("resume_form"):
    jd = st.text_area("Job Description", height=200)
    resume_file = st.file_uploader("Upload Resume", type=["pdf", "docx", "txt"])
    submitted = st.form_submit_button("Analyze")

if submitted:
    if jd and resume_file:
        with st.spinner("Analyzing with Gemini..."):
            resume_text = extract_text_from_file(resume_file)
            if resume_text:
                analysis = analyze_with_gemini(resume_text, jd)
                
                if analysis:
                    st.success("Analysis Complete!")
                    st.subheader("📊 Results")
                    
                    # Display score if found
                    score_match = re.search(r"1\. Fit Score: (\d+)", analysis)
                    if score_match:
                        st.metric("Match Score", f"{score_match.group(1)}/100")
                    
                    st.markdown(analysis.replace("1.", "### 1.").replace("2.", "### 2."))
    else:
        st.error("Upload a resume and enter a job description.")

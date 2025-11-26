import streamlit as st
import os
from dotenv import load_dotenv
from utils import extract_text_from_pdf, extract_text_from_url, analyze_cv

# Load environment variables
load_dotenv()

# Page Config
st.set_page_config(
    page_title="CV Matcher",
    page_icon="🎯",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# Custom CSS for "Pierre-Louis" Playful Dashboard Look
st.markdown("""
    <style>
    @import url('https://fonts.googleapis.com/css2?family=Outfit:wght@400;700;900&display=swap');
    
    /* GLOBAL STYLES */
    html, body, [class*="css"]  {
        font-family: 'Outfit', sans-serif;
        color: #ffffff !important;
    }
    
    /* Background Pattern (Dark Dotted Grid) */
    .stApp {
        background-color: #111827;
        background-image: radial-gradient(#374151 1px, transparent 1px);
        background-size: 20px 20px;
    }
    
    /* Main Container - The "Blue Card" */
    .main .block-container {
        background-color: #2563eb; /* Royal Blue */
        border-radius: 24px;
        padding: 3rem !important;
        margin-top: 2rem;
        box-shadow: 0 20px 25px -5px rgba(0, 0, 0, 0.1), 0 10px 10px -5px rgba(0, 0, 0, 0.04);
        border: 4px solid #1e40af;
        max-width: 900px;
    }
    
    /* HEADERS */
    h1 {
        font-weight: 900;
        letter-spacing: -0.02em;
        color: #ffffff !important;
        text-shadow: 2px 2px 0px rgba(0,0,0,0.1);
    }
    h2, h3, h4 {
        font-weight: 700;
        color: #dbeafe !important;
    }
    p, .stMarkdown {
        color: #eff6ff !important;
    }
    
    /* BUTTONS - Chunky & Tactile */
    .stButton>button {
        width: 100%;
        border-radius: 16px;
        height: 4em;
        background-color: #fbbf24; /* Yellow/Gold Accent */
        color: #92400e !important;
        border: none;
        font-weight: 800;
        font-size: 1.1em;
        box-shadow: 0 6px 0 #d97706; /* Darker yellow shadow for 3D effect */
        transition: all 0.1s ease;
        text-transform: uppercase;
        letter-spacing: 0.05em;
    }
    .stButton>button:hover {
        transform: translateY(2px);
        box-shadow: 0 4px 0 #d97706;
        background-color: #fcd34d;
        color: #92400e !important;
    }
    .stButton>button:active {
        transform: translateY(6px);
        box-shadow: 0 0 0 #d97706;
    }
    
    /* INPUTS & CARDS */
    .stTextInput>div>div, .stTextArea>div>div {
        background-color: #1e3a8a !important; /* Darker Blue */
        color: white !important;
        border: 2px solid #3b82f6;
        border-radius: 12px;
    }
    .stTextInput>div>div:focus-within, .stTextArea>div>div:focus-within {
        border-color: #fbbf24;
    }
    
    /* METRIC CARDS */
    .metric-card {
        background-color: #1e3a8a; /* Dark Blue */
        border: 2px solid #3b82f6;
        border-radius: 20px;
        padding: 24px;
        text-align: center;
        box-shadow: inset 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* TABS */
    .stTabs [data-baseweb="tab-list"] {
        gap: 10px;
        background-color: #1e3a8a;
        padding: 10px;
        border-radius: 16px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 45px;
        background-color: transparent;
        border-radius: 10px;
        color: #93c5fd;
        font-weight: 700;
        border: none;
    }
    .stTabs [aria-selected="true"] {
        background-color: #3b82f6;
        color: white;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
    }
    
    /* ALERTS/INFO BOXES */
    .stAlert {
        background-color: #1e3a8a !important;
        color: white !important;
        border: 1px solid #3b82f6;
        border-radius: 12px;
    }
    
    /* DOWNLOAD BUTTON */
    .stDownloadButton>button {
        background-color: #2dd4bf; /* Teal Accent */
        color: #0f766e !important;
        box-shadow: 0 6px 0 #0d9488;
    }
    .stDownloadButton>button:hover {
        background-color: #5eead4;
        box-shadow: 0 4px 0 #0d9488;
    }
    
    /* Trust Section Box */
    .trust-box {
        background-color: #1e3a8a !important;
        border: 2px dashed #3b82f6 !important;
        color: #bfdbfe !important;
    }

    /* CUSTOM INPUT BOX STYLING */
    /* Make File Uploader and Text Input look like equal cards */
    .upload-box, .job-box {
        background-color: #1e3a8a;
        border: 2px solid #3b82f6;
        border-radius: 16px;
        padding: 20px;
        height: 100%; /* Try to force equal height */
        min-height: 250px;
    }
    
    /* Bigger Labels */
    .stFileUploader label, .stRadio label, .stTextInput label, .stTextArea label {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #dbeafe !important;
    }
    
    /* Hide default Streamlit input borders since we have a wrapper card? 
       Actually, let's keep the input styles but ensure the containers align. */
    
    </style>
    """, unsafe_allow_html=True)

# Header / Hero Section
st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 3em; margin-bottom: 10px; color: white !important;">Stop chasing scores. Start getting interviews.</h1>
        <p style="font-size: 1.2em; color: #bfdbfe !important; margin-bottom: 30px;">
            Honest CV feedback. No games. No subscriptions.
        </p>
    </div>
""", unsafe_allow_html=True)

# ... (rest of the code)

# Trust Section (Updated Class)
# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key here if not set in .env")

# Get API Key
api_key = os.getenv("GOOGLE_API_KEY") or api_key_input

if not api_key:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to proceed.")
    st.stop()

# Inputs Section (Moved Up)
st.markdown('<div class="action-card">', unsafe_allow_html=True)
col1, col2 = st.columns(2)

with col1:
    uploaded_cv = st.file_uploader("1. Upload PDF", type=["pdf"])

with col2:
    job_input_type = st.radio("2. Job Details", ["URL", "Text"], horizontal=True, label_visibility="collapsed")
    
    if job_input_type == "URL":
        job_url = st.text_input("Paste Job URL", placeholder="https://linkedin.com/jobs/...", label_visibility="collapsed")
        job_text_input = None
    else:
        job_text_input = st.text_area("Paste Job Description", height=100, placeholder="Paste the full job description here...", label_visibility="collapsed")
        job_url = None

# Analysis Button
if st.button("Get Honest Feedback"):
    if not uploaded_cv:
        st.error("Please upload your CV.")
    elif (job_input_type == "URL" and not job_url) or (job_input_type == "Text" and not job_text_input):
        st.error("Please provide the job details.")
    else:
        with st.spinner("Analysing... (This might take a few seconds)"):
            # 1. Extract CV Text
            cv_text = extract_text_from_pdf(uploaded_cv)
            
            # 2. Extract Job Text
            if job_input_type == "URL":
                job_text = extract_text_from_url(job_url)
            else:
                job_text = job_text_input
                
            # 3. Analyze
            result = analyze_cv(cv_text, job_text, api_key)
            
            if "error" in result:
                st.error(f"Analysis failed: {result['error']}")
            else:
                # Display Results
                st.divider()
                
                # Top Section: Score & Title
                c1, c2 = st.columns([1, 2])
                with c1:
                    score = result.get('match_score', 0)
                    score_color = "#28a745" if score >= 80 else "#ffc107" if score >= 50 else "#dc3545"
                    
                    # Likelihood Badge
                    likelihood = result.get('response_likelihood', 'Unknown')
                    like_color = "#28a745" if likelihood == "High" else "#ffc107" if likelihood == "Moderate" else "#dc3545"
                    
                    st.markdown(f"""
                        <div class="metric-card">
                            <h2 style="margin:0; color: {score_color}; font-size: 3em;">{score}%</h2>
                            <p style="margin:0; color: #666; font-weight: 600;">Match Score</p>
                            <div style="margin-top: 10px; padding: 5px 10px; background-color: {like_color}20; color: {like_color}; border-radius: 20px; display: inline-block; font-weight: bold; font-size: 0.9em;">
                                {likelihood} Chance
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.subheader(result.get('job_title', 'Unknown Role'))
                    st.caption(f"Level: {result.get('job_level', 'Unknown')}")
                    st.write(f"**{likelihood} chance of a response.** Here's what would move the needle.")
                    
                    # Component Scores
                    st.markdown("##### Score Breakdown")
                    cs = result.get('component_scores', {})
                    sc1, sc2, sc3 = st.columns(3)
                    with sc1:
                        st.metric("Skills", f"{cs.get('skills', 0)}%")
                    with sc2:
                        st.metric("Experience", f"{cs.get('experience', 0)}%")
                    with sc3:
                        st.metric("Keywords", f"{cs.get('keywords', 0)}%")

                # Tabs for Deep Dive
                tab1, tab2, tab3, tab4 = st.tabs(["Priority Fixes", "Gap Analysis", "Impact & Quant", "Ready-to-Use Phrases"])
                
                with tab1:
                    # Priority Fixes
                    st.subheader("Top Priority Fixes")
                    st.caption("These 3 changes would have the biggest impact. Focus here first.")
                    for i, fix in enumerate(result.get('priority_fixes', [])):
                        st.info(f"**{i+1}.** {fix}")
                        
                    st.divider()
                    
                    # ATS Keywords Side-by-Side
                    st.subheader("ATS Keyword Gap Analysis")
                    st.caption("Missing keywords that actually matter.")
                    
                    missing_ats = result.get('ats_keywords', {}).get('missing', [])
                    
                    if missing_ats:
                        st.markdown(f"""
                        <div style="display: flex; gap: 20px;">
                            <div style="flex: 1; padding: 15px; background-color: #fff3cd; border-radius: 8px; border-left: 5px solid #ffc107;">
                                <h4 style="margin-top:0; color: #856404;">⚠️ Missing from CV</h4>
                                <ul style="padding-left: 20px; color: #856404;">
                                    {''.join([f'<li>{kw}</li>' for kw in missing_ats])}
                                </ul>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("Great job! No major ATS keywords missing.")

                    # Red Flags
                    red_flags = result.get('red_flags', [])
                    if red_flags:
                        st.divider()
                        st.subheader("Potential Concerns")
                        for flag in red_flags:
                            st.error(flag)

                with tab2:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("### Hard Skills")
                        if result.get('hard_skills', {}).get('missing', []):
                            st.markdown("**Missing**")
                            for skill in result.get('hard_skills', {}).get('missing', []):
                                st.markdown(f"- <span style='color:#dc3545'>{skill}</span>", unsafe_allow_html=True)
                        
                        st.markdown("**Present**")
                        for skill in result.get('hard_skills', {}).get('present', []):
                            st.markdown(f"- <span style='color:#28a745'>{skill}</span>", unsafe_allow_html=True)
                            
                    with col_b:
                        st.markdown("### Soft Skills")
                        if result.get('soft_skills', {}).get('missing', []):
                            st.markdown("**Missing**")
                            for skill in result.get('soft_skills', {}).get('missing', []):
                                st.markdown(f"- <span style='color:#dc3545'>{skill}</span>", unsafe_allow_html=True)

                        st.markdown("**Present**")
                        for skill in result.get('soft_skills', {}).get('present', []):
                            st.markdown(f"- <span style='color:#28a745'>{skill}</span>", unsafe_allow_html=True)

                with tab3:
                    st.subheader("Quantification Score")
                    st.caption("Recruiters look for numbers to understand the scale of your impact.")
                    
                    q_score = result.get('quantification_analysis', {}).get('score', 0)
                    st.progress(q_score / 100, text=f"{q_score}/100")
                    
                    st.markdown("**Analysis:**")
                    for item in result.get('quantification_analysis', {}).get('feedback', []):
                        st.info(item)

                with tab4:
                    st.subheader("Culture Signals")
                    st.write(result.get('cultural_fit', 'No specific details found.'))
                    
                    st.divider()
                    
                    st.subheader("Ready-to-Use Phrases")
                    st.caption("Professional phrasing you can adapt for your CV.")
                    for phrase in result.get('suggested_phrases', []):
                        with st.expander(f"{phrase.get('context', 'General')}"):
                            st.markdown(f"_{phrase.get('suggestion', '')}_")

                # Export Button
                st.divider()
                report_text = f"""
CV Matcher Report
=================
Job Title: {result.get('job_title')}
Match Score: {result.get('match_score')}%
Response Likelihood: {result.get('response_likelihood')}

---
PRIORITY FIXES
{chr(10).join(['- ' + f for f in result.get('priority_fixes', [])])}

---
ATS MISSING KEYWORDS
{', '.join(result.get('ats_keywords', {}).get('missing', []))}

---
SUGGESTED PHRASES
{chr(10).join([f"- {p.get('context')}: {p.get('suggestion')}" for p in result.get('suggested_phrases', [])])}
"""
                st.download_button(
                    label="📥 Download Report (No Signup Required)",
                    data=report_text,
                    file_name="cv_analysis_report.txt",
                    mime="text/plain",
                    help="Your report. No watermark. No signup. Just take it."
                )

# Trust Footer (Integrated)
st.markdown("""
    <div style="text-align: center; margin-top: 10px; margin-bottom: 30px;">
        <p style="color: #bfdbfe !important; font-size: 0.9em; margin: 0;">
            No "free trial" • No signup required • No watermarks • No upsell
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# Value Props (3 Columns)
c1, c2, c3 = st.columns(3)
with c1:
    st.markdown("### Real Chances")
    st.caption("Not just a gamified number. An honest assessment of whether you'll actually hear back.")
with c2:
    st.markdown("### The 3 Gaps")
    st.caption("We flag the top 3 things hurting you most, not 47 suggestions you'll never action.")
with c3:
    st.markdown("### Actual Phrases")
    st.caption("Copy-pasteable suggestions that sound human, not like a keyword-stuffing bot.")

st.divider()

# Sidebar for API Key
with st.sidebar:
    st.header("Settings")
    api_key_input = st.text_input("Gemini API Key", type="password", help="Enter your Google Gemini API Key here if not set in .env")

# Get API Key
api_key = os.getenv("GOOGLE_API_KEY") or api_key_input

if not api_key:
    st.warning("⚠️ Please enter your Gemini API Key in the sidebar to proceed.")
    st.stop()

# Inputs
st.subheader("Check my CV")

# Custom CSS wrapper for equal height columns isn't natively supported in Streamlit easily without components.
# We will simulate it by styling the inner elements to fill space.

col1, col2 = st.columns(2)

with col1:
    # We can't easily wrap st elements in a div *and* keep them functional in pure python without components.
    # But we can style the specific widgets.
    st.markdown("##### 1. Upload PDF")
    uploaded_cv = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")

with col2:
    st.markdown("##### 2. Job Details")
    # Radio horizontal to save vertical space and align
    job_input_type = st.radio("Job Details", ["URL", "Text"], horizontal=True, label_visibility="collapsed")
    
    if job_input_type == "URL":
        job_url = st.text_input("Paste Job URL", placeholder="https://linkedin.com/jobs/...", label_visibility="collapsed")
        job_text_input = None
    else:
        job_text_input = st.text_area("Paste Job Description", height=150, placeholder="Paste description...", label_visibility="collapsed")
        job_url = None

# Analysis Button
if st.button("Get Honest Feedback"):
    if not uploaded_cv:
        st.error("Please upload your CV.")
    elif (job_input_type == "URL" and not job_url) or (job_input_type == "Text" and not job_text_input):
        st.error("Please provide the job details.")
    else:
        with st.spinner("Analysing... (This might take a few seconds)"):
            # 1. Extract CV Text
            cv_text = extract_text_from_pdf(uploaded_cv)
            
            # 2. Extract Job Text
            if job_input_type == "URL":
                job_text = extract_text_from_url(job_url)
            else:
                job_text = job_text_input
                
            # 3. Analyze
            result = analyze_cv(cv_text, job_text, api_key)
            
            if "error" in result:
                st.error(f"Analysis failed: {result['error']}")
            else:
                # Display Results
                st.divider()
                
                # Top Section: Score & Title
                c1, c2 = st.columns([1, 2])
                with c1:
                    score = result.get('match_score', 0)
                    score_color = "#28a745" if score >= 80 else "#ffc107" if score >= 50 else "#dc3545"
                    
                    # Likelihood Badge
                    likelihood = result.get('response_likelihood', 'Unknown')
                    like_color = "#28a745" if likelihood == "High" else "#ffc107" if likelihood == "Moderate" else "#dc3545"
                    
                    st.markdown(f"""
                        <div class="metric-card">
                            <h2 style="margin:0; color: {score_color}; font-size: 3em;">{score}%</h2>
                            <p style="margin:0; color: #666; font-weight: 600;">Match Score</p>
                            <div style="margin-top: 10px; padding: 5px 10px; background-color: {like_color}20; color: {like_color}; border-radius: 20px; display: inline-block; font-weight: bold; font-size: 0.9em;">
                                {likelihood} Chance
                            </div>
                        </div>
                    """, unsafe_allow_html=True)
                with c2:
                    st.subheader(result.get('job_title', 'Unknown Role'))
                    st.caption(f"Level: {result.get('job_level', 'Unknown')}")
                    st.write(f"**{likelihood} chance of a response.** Here's what would move the needle.")
                    
                    # Component Scores
                    st.markdown("##### Score Breakdown")
                    cs = result.get('component_scores', {})
                    sc1, sc2, sc3 = st.columns(3)
                    with sc1:
                        st.metric("Skills", f"{cs.get('skills', 0)}%")
                    with sc2:
                        st.metric("Experience", f"{cs.get('experience', 0)}%")
                    with sc3:
                        st.metric("Keywords", f"{cs.get('keywords', 0)}%")

                # Tabs for Deep Dive
                # Renamed Features: Priority Fixes, Gap Analysis, Impact & Quant, Ready-to-Use Phrases
                tab1, tab2, tab3, tab4 = st.tabs(["Priority Fixes", "Gap Analysis", "Impact & Quant", "Ready-to-Use Phrases"])
                
                with tab1:
                    # Priority Fixes
                    st.subheader("Top Priority Fixes")
                    st.caption("These 3 changes would have the biggest impact. Focus here first.")
                    for i, fix in enumerate(result.get('priority_fixes', [])):
                        st.info(f"**{i+1}.** {fix}")
                        
                    st.divider()
                    
                    # ATS Keywords Side-by-Side
                    st.subheader("ATS Keyword Gap Analysis")
                    st.caption("Missing keywords that actually matter.")
                    
                    missing_ats = result.get('ats_keywords', {}).get('missing', [])
                    
                    if missing_ats:
                        # Create a visual representation
                        st.markdown(f"""
                        <div style="display: flex; gap: 20px;">
                            <div style="flex: 1; padding: 15px; background-color: #fff3cd; border-radius: 8px; border-left: 5px solid #ffc107;">
                                <h4 style="margin-top:0; color: #856404;">⚠️ Missing from CV</h4>
                                <ul style="padding-left: 20px; color: #856404;">
                                    {''.join([f'<li>{kw}</li>' for kw in missing_ats])}
                                </ul>
                            </div>
                        </div>
                        """, unsafe_allow_html=True)
                    else:
                        st.success("Great job! No major ATS keywords missing.")

                    # Red Flags
                    red_flags = result.get('red_flags', [])
                    if red_flags:
                        st.divider()
                        st.subheader("Potential Concerns")
                        for flag in red_flags:
                            st.error(flag)

                with tab2:
                    col_a, col_b = st.columns(2)
                    with col_a:
                        st.markdown("### Hard Skills")
                        if result.get('hard_skills', {}).get('missing', []):
                            st.markdown("**Missing**")
                            for skill in result.get('hard_skills', {}).get('missing', []):
                                st.markdown(f"- <span style='color:#dc3545'>{skill}</span>", unsafe_allow_html=True)
                        
                        st.markdown("**Present**")
                        for skill in result.get('hard_skills', {}).get('present', []):
                            st.markdown(f"- <span style='color:#28a745'>{skill}</span>", unsafe_allow_html=True)
                            
                    with col_b:
                        st.markdown("### Soft Skills")
                        if result.get('soft_skills', {}).get('missing', []):
                            st.markdown("**Missing**")
                            for skill in result.get('soft_skills', {}).get('missing', []):
                                st.markdown(f"- <span style='color:#dc3545'>{skill}</span>", unsafe_allow_html=True)

                        st.markdown("**Present**")
                        for skill in result.get('soft_skills', {}).get('present', []):
                            st.markdown(f"- <span style='color:#28a745'>{skill}</span>", unsafe_allow_html=True)

                with tab3:
                    st.subheader("Quantification Score")
                    st.caption("Recruiters look for numbers to understand the scale of your impact.")
                    
                    q_score = result.get('quantification_analysis', {}).get('score', 0)
                    st.progress(q_score / 100, text=f"{q_score}/100")
                    
                    st.markdown("**Analysis:**")
                    for item in result.get('quantification_analysis', {}).get('feedback', []):
                        st.info(item)

                with tab4:
                    st.subheader("Culture Signals")
                    st.write(result.get('cultural_fit', 'No specific details found.'))
                    
                    st.divider()
                    
                    st.subheader("Ready-to-Use Phrases")
                    st.caption("Professional phrasing you can adapt for your CV.")
                    for phrase in result.get('suggested_phrases', []):
                        with st.expander(f"{phrase.get('context', 'General')}"):
                            st.markdown(f"_{phrase.get('suggestion', '')}_")

                # Export Button
                st.divider()
                report_text = f"""
CV Matcher Report
=================
Job Title: {result.get('job_title')}
Match Score: {result.get('match_score')}%
Response Likelihood: {result.get('response_likelihood')}

---
PRIORITY FIXES
{chr(10).join(['- ' + f for f in result.get('priority_fixes', [])])}

---
ATS MISSING KEYWORDS
{', '.join(result.get('ats_keywords', {}).get('missing', []))}

---
SUGGESTED PHRASES
{chr(10).join([f"- {p.get('context')}: {p.get('suggestion')}" for p in result.get('suggested_phrases', [])])}
"""
                st.download_button(
                    label="📥 Download Report (No Signup Required)",
                    data=report_text,
                    file_name="cv_analysis_report.txt",
                    mime="text/plain",
                    help="Your report. No watermark. No signup. Just take it."
                )
                
                # Trust Section
                st.markdown("""
                    <div style="margin-top: 50px; padding: 20px; background-color: #f8fafc; border-radius: 10px; text-align: center; border: 1px dashed #cbd5e1;">
                        <h4 style="color: #64748b; margin-bottom: 10px;">No tricks. No traps.</h4>
                        <p style="color: #64748b; font-size: 0.9em; margin: 0;">
                            No "free trial" that charges you • No signup required • No watermarked downloads • No upsell
                        </p>
                    </div>
                """, unsafe_allow_html=True)


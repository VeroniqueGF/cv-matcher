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

    /* CUSTOM CONTAINER STYLING (For Input Cards) */
    [data-testid="stVerticalBlockBorderWrapper"] {
        background-color: #1e3a8a !important;
        border: 2px solid #3b82f6 !important;
        border-radius: 16px !important;
        padding: 20px !important;
        transition: transform 0.2s ease, box-shadow 0.2s ease;
        min-height: 320px; /* Force equal height for both cards */
        display: flex;
        flex-direction: column;
        justify-content: flex-start;
    }
    
    /* Hover Effect for Cards */
    [data-testid="stVerticalBlockBorderWrapper"]:hover {
        transform: translateY(-5px);
        box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.2);
        border-color: #fbbf24 !important; /* Gold border on hover */
    }
    
    /* Next Badge Styling */
    .next-badge {
        background-color: #fbbf24;
        color: #92400e;
        font-weight: 900;
        font-size: 1.1em;
        width: 60px;
        height: 60px;
        border-radius: 50%;
        display: flex;
        align-items: center;
        justify-content: center;
        margin: 120px auto 0 auto; /* Adjusted top margin for better vertical centering */
        box-shadow: 0 4px 0 #d97706;
        border: 2px solid #fff;
        z-index: 10;
        position: relative; /* Ensure it respects flow but z-index works */
    }
    
    /* Remove default file uploader background to blend in */
    [data-testid="stFileUploader"] {
        padding-top: 0;
    }
    section[data-testid="stFileUploaderDropzone"] {
        background-color: #172554 !important; /* Even darker blue for contrast */
        border: 2px dashed #60a5fa !important;
        border-radius: 12px;
    }
    
    /* Make text areas blend in */
    .stTextArea textarea {
        background-color: #172554 !important;
        border: 2px solid #3b82f6 !important;
    }

    /* Bigger Labels */
    .stFileUploader label, .stRadio label, .stTextInput label, .stTextArea label, h5 {
        font-size: 1.2rem !important;
        font-weight: 700 !important;
        color: #dbeafe !important;
    }
    </style>
    """, unsafe_allow_html=True)

# Header / Hero Section
st.markdown("""
    <div style="text-align: center; padding: 40px 0;">
        <h1 style="font-size: 3em; margin-bottom: 10px; color: white !important;">Know where you stand before you apply.</h1>
        <p style="font-size: 1.2em; color: #bfdbfe !important; margin-bottom: 30px;">
            Quick, honest feedback to strengthen your application.
        </p>
    </div>
""", unsafe_allow_html=True)

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
# We use st.container(border=True) to create visual "Cards" for the inputs

# Adjusted column ratios to give more space for the "Next" badge
col1, col_mid, col2 = st.columns([1, 0.3, 1])

with col1:
    with st.container(border=True):
        st.markdown("##### 📄 Your CV")
        uploaded_cv = st.file_uploader("Upload PDF", type=["pdf"], label_visibility="collapsed")
        st.caption("Limit 200MB per file • PDF")

with col_mid:
    st.markdown('<div class="next-badge">Next</div>', unsafe_allow_html=True)

with col2:
    with st.container(border=True):
        st.markdown("##### 🎯 Job Spec")
        # Radio horizontal to save vertical space and align
        job_input_type = st.radio("Job Spec", ["URL", "Text"], horizontal=True, label_visibility="collapsed")
        
        if job_input_type == "URL":
            job_url = st.text_input("Paste Job URL", placeholder="https://linkedin.com/jobs/...", label_visibility="collapsed")
            st.caption("Works with LinkedIn, Indeed, and most job sites.")
            job_text_input = None
        else:
            job_text_input = st.text_area("Paste Job Description", height=150, placeholder="Paste description...", label_visibility="collapsed")
            job_url = None

# Analysis Button (Full Width)
st.markdown("<br>", unsafe_allow_html=True) # Add some spacing
# Button is placed directly to span the full width of the container
if st.button("CHECK MY CV", use_container_width=True, type="primary"):
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
            Free • No signup • Results in 30 seconds
        </p>
    </div>
""", unsafe_allow_html=True)

st.divider()

# Value Props (3 Columns)
c1, c2, c3 = st.columns(3)

with c1:
    # Use columns to put image next to text or just above
    # User said "next to it or in a way that you suggest would look good"
    # Centered icon above text often looks best for 3-column layouts
    st.image("assets/icon_chances.png", width=80) 
    st.markdown("### Your Real Chances")
    st.caption("See how likely you are to hear back—and understand why.")

with c2:
    st.image("assets/icon_matters.png", width=80)
    st.markdown("### What Matters Most")
    st.caption("The 3 changes that will make the biggest difference, ranked by impact.")

with c3:
    st.image("assets/icon_phrases.png", width=80)
    st.markdown("### Ready-to-Use Phrases")
    st.caption("Suggestions you can copy straight into your CV. Written like a human, not a robot.")

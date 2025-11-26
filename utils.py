import google.generativeai as genai
import pypdf
import requests
from bs4 import BeautifulSoup
import json
import os

def extract_text_from_pdf(uploaded_file):
    """Extracts text from a PDF file."""
    try:
        pdf_reader = pypdf.PdfReader(uploaded_file)
        text = ""
        for page in pdf_reader.pages:
            text += page.extract_text()
        return text
    except Exception as e:
        return f"Error reading PDF: {e}"

def extract_text_from_url(url):
    """Extracts text from a job listing URL."""
    try:
        response = requests.get(url, timeout=10)
        response.raise_for_status()
        soup = BeautifulSoup(response.content, 'html.parser')
        
        # Remove script and style elements
        for script in soup(["script", "style"]):
            script.decompose()
            
        text = soup.get_text()
        
        # Break into lines and remove leading/trailing space on each
        lines = (line.strip() for line in text.splitlines())
        # Break multi-headlines into a line each
        chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
        # Drop blank lines
        text = '\n'.join(chunk for chunk in chunks if chunk)
        
        return text
    except Exception as e:
        return f"Error fetching URL: {e}"

def analyze_cv(cv_text, job_text, api_key):
    """Analyzes CV against Job Description using Gemini API."""
    
    genai.configure(api_key=api_key)
    
    # Set up the model
    generation_config = {
        "temperature": 0.7,
        "top_p": 1,
        "top_k": 1,
        "max_output_tokens": 2048,
        "response_mime_type": "application/json",
    }
    
    model = genai.GenerativeModel(model_name="gemini-1.5-flash", generation_config=generation_config)

    prompt = f"""
    You are an expert UK Career Coach and Recruiter who knows modern CV writing conventions inside out. 
    Your task is to provide a "Deep Dive" analysis of a candidate's CV against a job listing.
    
    **CV Text:**
    {cv_text}
    
    **Job Listing Text:**
    {job_text}
    
    Please analyze the match and provide the output in the following JSON format:
    {{
        "match_score": "Integer between 0 and 100",
        "match_explanation": "Short explanation of the score (max 2 sentences)",
        "response_likelihood": "High, Moderate, or Low",
        "component_scores": {{
            "skills": "Integer 0-100",
            "experience": "Integer 0-100",
            "keywords": "Integer 0-100"
        }},
        "job_title": "Extracted Job Title",
        "job_level": "Junior, Mid, Senior, Lead, etc.",
        "ats_keywords": {{
            "missing": ["List of exact keywords/skills from the job description that are missing from the CV. CRITICAL for ATS."]
        }},
        "hard_skills": {{
            "present": ["List of hard skills found in CV"],
            "missing": ["List of hard skills required but missing"]
        }},
        "soft_skills": {{
            "present": ["List of soft skills found in CV"],
            "missing": ["List of soft skills required but missing"]
        }},
        "quantification_analysis": {{
            "score": "Integer 0-100 representing how well achievements are quantified",
            "feedback": ["Specific bullet points on where numbers/metrics are needed (e.g., 'Sales increased by X%')"]
        }},
        "red_flags": ["List of potential red flags (e.g., employment gaps, job hopping, vague dates, formatting issues). Return empty list if none."],
        "cultural_fit": "Summary of cultural fit based on values mentioned in the listing (or 'Not mentioned' if none found)",
        "priority_fixes": ["The Top 3 most critical things to fix FIRST to improve the match score."],
        "suggested_phrases": [
            {{
                "context": "Brief context (e.g. 'For the Leadership section')",
                "suggestion": "Draft text the user can adapt (e.g. 'Spearheaded a cross-functional team of 5...')"
            }}
        ]
    }}
    
    **Important Guidelines:**
    - Use British English spelling.
    - **ATS Focus**: Be ruthless about missing keywords.
    - **Quantification**: Look for numbers, percentages, and $ amounts. If missing, flag it.
    - **Tone**: Professional, constructive, but direct. Don't sugarcoat red flags.
    - If the CV or Job text is too short or invalid, return a JSON with a score of 0 and an explanation of the error.
    """

    # Define preferred models in order of priority (Flash models first for speed/cost)
    preferred_models = [
        "gemini-1.5-flash",
        "gemini-1.5-flash-001",
        "models/gemini-1.5-flash",
        "models/gemini-1.5-flash-001",
        "gemini-1.5-pro",
        "gemini-1.5-pro-001",
        "models/gemini-1.5-pro",
        "models/gemini-1.5-pro-001",
        "gemini-pro",
        "models/gemini-pro"
    ]
    
    # Get all available models from the API
    available_models = []
    try:
        for m in genai.list_models():
            if 'generateContent' in m.supported_generation_methods:
                available_models.append(m.name)
    except Exception as e:
        # If list_models fails, we'll just rely on the preferred list
        pass

    # Build a comprehensive list of candidates to try
    # 1. Preferred models that are confirmed available
    # 2. Preferred models that might be available (if list_models failed or missed them)
    # 3. Any other available models (as a last resort)
    
    candidates = []
    
    # Add preferred models first
    for pref in preferred_models:
        candidates.append(pref)
        
    # Add other available models if they aren't already in the list
    for avail in available_models:
        if avail not in candidates and "models/" + avail not in candidates:
            candidates.append(avail)
            
    last_error = None
    
    # Iterate through candidates and try to generate content
    for model_name in candidates:
        try:
            model = genai.GenerativeModel(model_name=model_name, generation_config=generation_config)
            response = model.generate_content(prompt)
            return json.loads(response.text)
        except Exception as e:
            last_error = e
            # If it's a rate limit (429) or not found (404), we continue to the next model.
            # We print the error to console for debugging but don't stop.
            print(f"Model {model_name} failed: {e}")
            continue
            
    return {"error": f"All models failed. Please check your API key and Quota. Last error: {str(last_error)}"}

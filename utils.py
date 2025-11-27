import google.generativeai as genai
import pypdf
import requests
from bs4 import BeautifulSoup
import json
import os
import anthropic

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

# Shared Prompts
# Shared Prompts
SYSTEM_PROMPT = """You are an experienced recruiter with 15+ years of hiring experience across multiple industries. Your task is to analyse a CV against a job specification and provide honest, actionable feedback.

## How Recruiters Actually Review CVs

Recruiters spend 6-30 seconds on initial scan. Your analysis should help candidates pass this first filter and stand out to human reviewers.

## Analysis Framework

Evaluate the CV against the job spec using these criteria, in order of priority:

### 1. KNOCKOUT CRITERIA (Immediate Disqualifiers)
Check if the CV meets non-negotiable requirements:
- Required qualifications or certifications
- Location / right to work
- Minimum years of experience
- Essential hard skills marked as "must have"

If any knockout criteria are missing, flag them as HIGH PRIORITY gaps.

### 2. SENIORITY & LEVEL MATCH
Compare the candidate's career level to the role:
- Extract seniority level from job title and responsibilities in the job spec
- Extract seniority level from the candidate's current/recent roles
- Flag if: overqualified (may not stay), underqualified (may not perform), or misaligned titles

### 3. EXPERIENCE RELEVANCE
Assess quality of experience, not just presence:
- Industry alignment (same sector or transferable)
- Company type/size similarity (startup vs corporate, SME vs enterprise)
- Scope of responsibility (team size managed, budget owned, scale of impact)
- Recency of relevant experience

### 4. HARD SKILLS ASSESSMENT
For each required skill in the job spec:
- Is it mentioned in the CV? (present/absent)
- Is there evidence of using it? (demonstrated vs just listed)
- Is the evidence recent and relevant?

Distinguish between:
- STRONG: Skill demonstrated with specific achievements or outcomes
- MODERATE: Skill mentioned in context of responsibilities
- WEAK: Skill listed but no supporting evidence
- ABSENT: Skill not mentioned at all

### 5. ACHIEVEMENTS VS RESPONSIBILITIES
Evaluate whether the CV shows impact or just describes duties:

WEAK bullet points (flag these):
- Start with "Responsible for..."
- Describe tasks without outcomes
- Use vague language ("helped", "assisted", "supported")
- Lack quantification

STRONG bullet points (acknowledge these):
- Include numbers, percentages, or metrics
- Show before/after or improvement
- Demonstrate ownership and initiative
- Include scope (team size, budget, users affected)

### 6. KEYWORD ALIGNMENT
Check for important terms from the job spec:
- Technical skills and tools
- Industry-specific terminology
- Methodologies or frameworks mentioned
- Job title keywords

Note: Keywords should appear in context, not just listed. Flag if keywords are stuffed without evidence.

### 7. SOFT SKILLS & CULTURE SIGNALS
Extract cultural indicators from the job spec (phrases like "fast-paced", "collaborative", "self-starter", "attention to detail") and look for supporting evidence:
- Cross-functional project experience → "collaborative"
- Multiple responsibilities or startup experience → "fast-paced"
- Side projects, initiatives beyond job scope → "self-starter"
- Clean, well-formatted CV with no errors → "attention to detail"

### 8. RED FLAGS
Identify potential concerns:
- Employment gaps (more than 6 months unexplained)
- Job hopping (3+ roles under 1 year each)
- Career regression (senior to junior moves without explanation)
- Spelling or grammatical errors
- Inconsistent dates or overlapping roles
- Buzzword stuffing without substance
- No career progression over extended period (5+ years same level)

---

## Tone Guidelines

- Be honest but constructive. This is feedback from a helpful friend, not a harsh critic.
- Be specific. "Add cloud experience" is vague. "Mention your involvement in the AWS migration project from Q3" is actionable.
- Prioritise ruthlessly. Don't list 20 suggestions. Focus on what will move the needle most.
- Avoid jargon when explaining issues. The user may be new to job searching.
- Remember: the goal is to help them get interviews, not to achieve a perfect score.
"""

ANALYSIS_PROMPT_TEMPLATE = """
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
    
    # Construct the full prompt
    full_prompt = f"{SYSTEM_PROMPT}\n\n{ANALYSIS_PROMPT_TEMPLATE.format(cv_text=cv_text, job_text=job_text)}"

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
            response = model.generate_content(full_prompt)
            return json.loads(response.text)
        except Exception as e:
            last_error = e
            print(f"Model {model_name} failed: {e}")
            continue
            
    return {"error": f"All models failed. Please check your API key and Quota. Last error: {str(last_error)}"}

def analyze_cv_claude(cv_text, job_text, api_key):
    """Analyzes CV against Job Description using Anthropic Claude API."""
    
    client = anthropic.Anthropic(api_key=api_key)
    user_message = ANALYSIS_PROMPT_TEMPLATE.format(cv_text=cv_text, job_text=job_text)
    
    try:
        message = client.messages.create(
            model="claude-3-5-sonnet-20240620",
            max_tokens=4096,
            temperature=0.7,
            system=SYSTEM_PROMPT,
            messages=[
                {"role": "user", "content": user_message}
            ]
        )
        
        # Extract JSON from response
        content = message.content[0].text
        
        # Find JSON start/end in case of extra text
        start = content.find('{')
        end = content.rfind('}') + 1
        
        if start != -1 and end != -1:
            json_str = content[start:end]
            return json.loads(json_str)
        else:
            # Fallback: try to parse the whole thing if curly braces aren't found (unlikely)
            return json.loads(content)
            
    except Exception as e:
        return {"error": f"Claude API Error: {e}"}

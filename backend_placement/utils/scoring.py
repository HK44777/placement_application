import os
import requests
import PyPDF2
from groq import Groq
import json

# Constants
PREDEFINED_SKILLS_FILE = os.path.join(os.path.dirname(os.path.dirname(__file__)), "predefined_skills.txt")

def get_groq_client():
    api_key = os.environ.get("GROQ_API_KEY", "")
    if not api_key:
        return None
    try:
        return Groq(api_key=api_key)
    except Exception as e:
        print(f"Warning: Could not initialize Groq client: {e}")
        return None

def load_predefined_skills():
    if not os.path.exists(PREDEFINED_SKILLS_FILE):
        return []
    with open(PREDEFINED_SKILLS_FILE, 'r') as f:
        return [line.strip() for line in f if line.strip()]

def extract_text_from_pdf(pdf_path):
    """Extract text from a PDF file using PyPDF2."""
    try:
        text = ""
        with open(pdf_path, 'rb') as file:
            reader = PyPDF2.PdfReader(file)
            for page in reader.pages:
                page_text = page.extract_text()
                if page_text:
                    text += page_text + "\n"
        return text
    except Exception as e:
        print(f"Error reading PDF {pdf_path}: {e}")
        return ""

try:
    from sentence_transformers import SentenceTransformer
    embedding_model = SentenceTransformer('all-MiniLM-L6-v2')
except ImportError:
    embedding_model = None
    print("Warning: sentence-transformers not installed. Please install it using `pip install sentence-transformers`")

def get_hf_embeddings(texts):
    """Get embeddings locally using sentence-transformers."""
    if embedding_model is None:
        raise RuntimeError("sentence-transformers is not installed.")
    
    embeddings = embedding_model.encode(texts)
    return embeddings.tolist()

def cosine_similarity(vec1, vec2):
    """Calculate cosine similarity between two vectors."""
    dot_product = sum(a * b for a, b in zip(vec1, vec2))
    norm_a = sum(a * a for a in vec1) ** 0.5
    norm_b = sum(b * b for b in vec2) ** 0.5
    if norm_a == 0 or norm_b == 0:
        return 0.0
    return dot_product / (norm_a * norm_b)

def extract_skills_with_groq(text, is_jd=False):
    """Extract skills using Groq LLaMA model in JSON format."""
    groq_client = get_groq_client()
    if not groq_client:
        return {"must_have": [], "nice_to_have": []} if is_jd else {"internship_skills": [], "project_skills": [], "skills": []}
        
    if is_jd:
        prompt = (
            "Extract ONLY hard technical skills, programming languages, software tools, databases, cloud platforms, and frameworks from the following job description. "
            "Categorize them into 'must_have' and 'nice_to_have' based on the text.\n"
            "STRICT RULES:\n"
            "1. DO NOT include soft skills.\n"
            "2. DO NOT include business concepts, methodologies, or descriptive workflows.\n"
            "3. DO NOT include full sentences or project descriptions.\n"
            "4. EVERY item must be a recognizable, concrete technology.\n"
            "Return ONLY a valid JSON object with the keys 'must_have' and 'nice_to_have' containing arrays of strings.\n\n"
            f"Text:\n{text}"
        )
    else:
        prompt = (
            "Extract ONLY hard technical skills, programming languages, software tools, databases, cloud platforms, and frameworks from the following resume. "
            "Categorize them based on where they appear into 'internship_skills', 'project_skills', and 'skills' (general skills).\n"
            "STRICT RULES:\n"
            "1. DO NOT include soft skills.\n"
            "2. DO NOT include business concepts, methodologies, or descriptive workflows.\n"
            "3. DO NOT include full sentences or project descriptions.\n"
            "4. EVERY item must be a recognizable, concrete technology.\n"
            "Return ONLY a valid JSON object with the keys 'internship_skills', 'project_skills', and 'skills' containing arrays of strings.\n\n"
            f"Text:\n{text}"
        )
    
    try:
        chat_completion = groq_client.chat.completions.create(
            messages=[
                {
                    "role": "system",
                    "content": "You are an extremely strict IT recruiter AI. You ONLY extract concrete technical tools, frameworks, and languages. You silently ignore soft skills, concepts, and descriptive text. You strictly output valid JSON."
                },
                {
                    "role": "user",
                    "content": prompt,
                }
            ],
            model="llama-3.1-8b-instant",
            temperature=0.1,
            response_format={"type": "json_object"}
        )
        
        output = chat_completion.choices[0].message.content
        return json.loads(output)
    except Exception as e:
        print(f"Error extracting skills with Groq: {e}")
        return {"must_have": [], "nice_to_have": []} if is_jd else {"internship_skills": [], "project_skills": [], "skills": []}

def map_skills_to_predefined(extracted_skills, predefined_skills, threshold=0.7):
    """Map extracted skills to the predefined taxonomy using embeddings."""
    if not extracted_skills or not predefined_skills:
        return []
        
    try:
        predefined_embeddings = get_hf_embeddings(predefined_skills)
        extracted_embeddings = get_hf_embeddings(extracted_skills)
        
        mapped_skills = set()
        
        for i, ext_skill in enumerate(extracted_skills):
            ext_emb = extracted_embeddings[i]
            best_match = None
            best_score = 0.0
            
            if not isinstance(ext_emb, list) or len(ext_emb) == 0 or isinstance(ext_emb[0], list):
                continue
                
            for j, pre_skill in enumerate(predefined_skills):
                pre_emb = predefined_embeddings[j]
                if not isinstance(pre_emb, list) or len(pre_emb) == 0 or isinstance(pre_emb[0], list):
                    continue
                    
                score = cosine_similarity(ext_emb, pre_emb)
                
                if score > best_score:
                    best_score = score
                    best_match = pre_skill
            
            if best_score >= threshold and best_match:
                mapped_skills.add(best_match)
                
        return list(mapped_skills)
        
    except Exception as e:
        print(f"Error during skill mapping (API issues or rate limit): {e}")
        return [s for s in extracted_skills if any(p.lower() in s.lower() or s.lower() in p.lower() for p in predefined_skills)]

def calculate_match_score(jd_must_haves, jd_nice_to_haves, student_skills_weighted, weight_must_have=0.7, weight_nice_to_have=0.3):
    """
    Calculates the match score between a Job Description and a Student Profile.
    """
    # 1. Handle Must-Haves
    must_have_max = len(jd_must_haves) * 1.0
    must_have_actual = 0.0
    
    for skill in jd_must_haves:
        if skill in student_skills_weighted:
            must_have_actual += student_skills_weighted[skill]
            
    must_have_percentage = (must_have_actual / must_have_max * 100) if must_have_max > 0 else 0.0

    # 2. Handle Nice-to-Haves
    nice_to_have_max = len(jd_nice_to_haves) * 1.0
    nice_to_have_actual = 0.0
    
    for skill in jd_nice_to_haves:
        if skill in student_skills_weighted:
            nice_to_have_actual += student_skills_weighted[skill]
            
    nice_to_have_percentage = (nice_to_have_actual / nice_to_have_max * 100) if nice_to_have_max > 0 else 0.0

    # 3. Handle Edge Cases for Weights (Dynamic Weight Shifting)
    if must_have_max == 0 and nice_to_have_max == 0:
        return 0.0
    elif must_have_max == 0:
        return round(nice_to_have_percentage, 2)
    elif nice_to_have_max == 0:
        return round(must_have_percentage, 2)

    # 4. Calculate Final Weighted Score
    final_score = (must_have_percentage * weight_must_have) + (nice_to_have_percentage * weight_nice_to_have)
    
    return round(final_score, 2)

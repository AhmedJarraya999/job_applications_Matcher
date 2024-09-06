import os
import json
from fastapi import FastAPI
from pydantic import BaseModel
from proprecessing import Processing
import logging

# Paths for your patterns
majors_patterns_path = "/patterns/majors.jsonl"
degrees_patterns_path = "/patterns/degrees.jsonl"
skills_patterns_path = "/patterns/skills.jsonl"
labels_path_2 = {
    "MAJOR": {
        "DEV": [
            "software engineering", "software development", "computer sciences", "computer software",
            "information systems", "information science", "information sciences", "computer engineering",
            "cybersecurity", "web development", "network security", "programming", "computer science",
            "computer engineering", "systems analysis", "computer programming", "information sciences",
            "information technology", "cybersecurity", "systems and network administration"
        ],
        "AI": [
            "data sciences", "artificial intelligence", "data analysis", "nlp", "nlp engineering", "ai engineering",
            "ai", "computer vision", "data engineering", "mathematics", "statistics"
        ],
        "BUSINESS": ["business administration", "business analytics", "business intelligence"]
    }
}

# Initialize FastAPI
app = FastAPI()

# Initialize Processing instance
EXTRACT_DATA_FROM_CV = Processing(majors_patterns_path, degrees_patterns_path, skills_patterns_path)

# Pydantic model for input
class ResumeAnalysisRequest(BaseModel):
    resume_path: str
    job_description_path: str

# Function to calculate the final score
def calculate_final_score(resume_path: str, job_description_path: str) -> float:
    # Translate job description from file
    translated_job_description = EXTRACT_DATA_FROM_CV.translate_line_by_line(job_description_path)
    cv_jobdescription_as_a_string = ' '.join(translated_job_description)
    
    # Process resume
    CV_WORDS = EXTRACT_DATA_FROM_CV.define_type_of_file_and_make_action(resume_path)
    cv_translated_as_a_string = ' '.join(CV_WORDS)
    
    # Extract entities from resume and job description
    extract_entities_from_resume = EXTRACT_DATA_FROM_CV.extract_entities_from_resume(CV_WORDS)
    extract_entities_from_job_description = EXTRACT_DATA_FROM_CV.extract_entities_from_job_description(cv_jobdescription_as_a_string)
    
    # Degrees extraction
    degrees_list_from_a_resume = EXTRACT_DATA_FROM_CV.match_degrees_by_spacy(cv_translated_as_a_string)
    highest_degree = EXTRACT_DATA_FROM_CV.get_maximum_degree(degrees_list_from_a_resume)
    
    degrees_list_from_a_job_description = EXTRACT_DATA_FROM_CV.match_degrees_by_spacy(cv_jobdescription_as_a_string)
    minimum_degree_for_job_description = EXTRACT_DATA_FROM_CV.get_minimum_degree(degrees_list_from_a_job_description)
    
    # Degree score calculation
    score_degree = EXTRACT_DATA_FROM_CV.calculate_degree_score(minimum_degree_for_job_description, highest_degree)
    
    # Skills extraction
    skills_list_from_a_resume = EXTRACT_DATA_FROM_CV.match_skills_by_spacy(cv_translated_as_a_string)
    skills_list_from_a_job_description = EXTRACT_DATA_FROM_CV.match_skills_by_spacy(cv_jobdescription_as_a_string)
    
    # Skills score calculation
    score_skills = EXTRACT_DATA_FROM_CV.semantic_skills_similarity_sbert_base_v2(skills_list_from_a_job_description, skills_list_from_a_resume)
    
    # Major extraction
    majors_from_resume = EXTRACT_DATA_FROM_CV.match_majors_by_spacy(', '.join(CV_WORDS))
    major_categoriesv3_from_resume = EXTRACT_DATA_FROM_CV.get_major_categoriesv3(majors_from_resume, labels_path_2)
    
    majors_from_job_description = EXTRACT_DATA_FROM_CV.match_majors_by_spacy(cv_jobdescription_as_a_string)
    major_categoriesv3_from_job_description = EXTRACT_DATA_FROM_CV.get_major_categoriesv3(majors_from_job_description, labels_path_2)
    
    # Major score calculation
    exact_majors_from_job_description = majors_from_job_description[0] if majors_from_job_description else ''
    exact_major_category_in_job_description = major_categoriesv3_from_job_description[0] if major_categoriesv3_from_job_description else ''
    
    score_major = EXTRACT_DATA_FROM_CV.score_major_match(
        exact_majors_from_job_description,
        exact_major_category_in_job_description,
        majors_from_resume,
        major_categoriesv3_from_resume
    )
    
    # Final score calculation
    final_score = EXTRACT_DATA_FROM_CV.calculate_final_score(score_degree, score_skills, score_major)
    
    return final_score

# Set logging level to show all messages, including INFO and DEBUG
logging.basicConfig(level=logging.INFO)

# FastAPI endpoint
# @app.post("/analyze")
# def analyze_resume(request: ResumeAnalysisRequest) -> float:
#     resume_path = request.resume_path
#     job_description_path = request.job_description_path
#     return calculate_final_score(resume_path, job_description_path)
@app.post("/analyze")
def analyze_resume(request: ResumeAnalysisRequest) -> dict:
    resume_path = request.resume_path
    job_description_path = request.job_description_path
    # Log the current working directory
    current_directory = os.getcwd()
    logging.info(f"Current working directory: {current_directory}")
    # Using print to ensure it shows in the console
    print(f"Current working directory: {current_directory}")


    try:
        final_score = calculate_final_score(resume_path, job_description_path)
        return {"final_score": final_score}
    except Exception as e:
        logging.error(f"Error analyzing resume: {e}")
        return {"error": "An error occurred while processing the resume."}

# GET endpoint for a status check
@app.get("/status")
def get_status():
    return {"status": "API is running", "version": "1.0.0"}



# To run the FastAPI server
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)

from fastapi import FastAPI
from pydantic import BaseModel
import os
import logging
import base64
# Configure logging
logging.basicConfig(level=logging.INFO)

from AI.proprecessing import Processing

# Define paths for patterns
majors_patterns_path = "/AI/patterns/majors.jsonl"
degrees_patterns_path = "/AI/patterns/degrees.jsonl"
skills_patterns_path = "/AI/patterns/skills.jsonl"
labels_path = "/AI/patterns/labels.json"
labels_path_3 = "/AI/patterns/degrees.jsonl"
model_path = "/AI/model_loading/Translation_From_Frensh_words_to_English.pkl"

app = FastAPI()


# Pydantic model for the new endpoint
class FilePayload(BaseModel):
    file_path: str  # Relative file path with directories (e.g., "uploads/resumes/example.pdf")
    file_content: str  # Base64-encoded file content


class AnalyzeRequest(BaseModel):
     resume_path: str
     job_description: str

EXTRACT_DATA_FROM_CV = Processing(majors_patterns_path, degrees_patterns_path, skills_patterns_path)

# Default route for "Hello, World!"
@app.get("/")
def read_root():
    logging.info("Root endpoint accessed.")
    return {"message": "Hellorfez, Worlddd!"}

# New endpoint to handle file creation
@app.post("/upload-file")
def upload_file(payload: FilePayload):
    try:
        # Extract file path and content
        file_path = payload.file_path
        file_content = payload.file_content

        # Decode the Base64 content
        decoded_content = base64.b64decode(file_content)

        # Ensure the directory exists
        full_path = os.path.join(os.getcwd(), file_path)
        os.makedirs(os.path.dirname(full_path), exist_ok=True)

        # Write the file
        with open(full_path, "wb") as file:
            file.write(decoded_content)

        logging.info(f"File successfully created at {full_path}")
        return {"message": f"File created successfully at {full_path}"}
    except Exception as e:
        logging.error(f"Error creating file: {e}")
        return {"error": f"An error occurred: {str(e)}"}

@app.post("/analyze")
async def analyze_resume_job_description(request: AnalyzeRequest):
    """
    Process a resume file path and a job description string to calculate a final score.
    """
    resume_path = request.resume_path
    job_description = request.job_description  # Accept job description as a string

    # Validate if the resume path exists
    if not os.path.exists(resume_path):
        return {"error": f"Resume file not found: {resume_path}"}

    # Process the resume file
    cv_translated_as_a_string = ' '.join(EXTRACT_DATA_FROM_CV.define_type_of_file_and_make_action(resume_path))

    # Use the updated translate_line_by_linev2 method to process the job description string
    translated_job_description = EXTRACT_DATA_FROM_CV.translate_line_by_linev2(job_description)
    cv_jobdescription_as_a_string = ' '.join(translated_job_description)

    # Extract entities
    extract_entities_from_resume = EXTRACT_DATA_FROM_CV.extract_entities_from_resume(cv_translated_as_a_string)
    major_extracted_from_resume = extract_entities_from_resume.get("Major", [])
    list_majors_extracted_from_resume = major_extracted_from_resume if isinstance(major_extracted_from_resume, list) else []

    extract_entities_from_job_description = EXTRACT_DATA_FROM_CV.extract_entities_from_job_description(cv_jobdescription_as_a_string)
    major_extracted_from_job_description = extract_entities_from_job_description.get("Major", [])

    # Degree-related calculations
    degrees_list_from_a_resume = EXTRACT_DATA_FROM_CV.match_degrees_by_spacy(cv_translated_as_a_string)
    highest_degree = EXTRACT_DATA_FROM_CV.get_maximum_degree(degrees_list_from_a_resume)
    degrees_list_from_a_job_description = EXTRACT_DATA_FROM_CV.match_degrees_by_spacy(cv_jobdescription_as_a_string)
    minimum_degree_for_job_description = EXTRACT_DATA_FROM_CV.get_minimum_degree(degrees_list_from_a_job_description)
    score_degree = EXTRACT_DATA_FROM_CV.calculate_degree_score(minimum_degree_for_job_description, highest_degree)

    # Skills-related calculations
    skills_list_from_a_resume = EXTRACT_DATA_FROM_CV.match_skills_by_spacy(cv_translated_as_a_string)
    skills_list_from_a_job_description = EXTRACT_DATA_FROM_CV.match_skills_by_spacy(cv_jobdescription_as_a_string)
    score_skills = EXTRACT_DATA_FROM_CV.semantic_skills_similarity_sbert_base_v2(skills_list_from_a_job_description, skills_list_from_a_resume)

    # Major-related calculations
    major_categoriesv3_from_resume = EXTRACT_DATA_FROM_CV.get_major_categoriesv3(list_majors_extracted_from_resume, labels_path_3)
    major_categoriesv3_from_job_description = EXTRACT_DATA_FROM_CV.get_major_categoriesv3(major_extracted_from_job_description, labels_path_3)
    score_major = EXTRACT_DATA_FROM_CV.score_major_match(
        major_extracted_from_job_description,
        major_categoriesv3_from_job_description[0] if major_categoriesv3_from_job_description else None,
        list_majors_extracted_from_resume,
        major_categoriesv3_from_resume
    )

    # Final score calculation
    final_score = EXTRACT_DATA_FROM_CV.calculate_final_score(score_degree, score_skills, score_major)

    # Log details for debugging
    logging.info(f"Skills extracted from resume: {skills_list_from_a_resume}")
    logging.info(f"Skills extracted from job description: {skills_list_from_a_job_description}")
    logging.info(f"Score calculated from skills: {score_skills}")
    logging.info(f"Major extracted from resume: {major_categoriesv3_from_resume}")
    logging.info(f"Major extracted from the job description: {major_categoriesv3_from_job_description}")
    logging.info(f"Highest candidate degree: {highest_degree}")
    logging.info(f"Degree required for the job description: {minimum_degree_for_job_description}")
    logging.info(f"Score degree: {score_degree}")
    logging.info(f"Final score: {final_score}")

    return {
        "final_score": final_score
    }

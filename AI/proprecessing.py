from PyPDF2 import PdfReader
import pickle
import aspose.words as aw
import os
from spacy.lang.en import English
import pandas as pd
from sentence_transformers import SentenceTransformer
from sklearn.metrics.pairwise import cosine_similarity
# from resources import DEGREES_IMPORTANCE
DEGREES_IMPORTANCE = {'high school': 0, 'BACCALAUREATE': 1, 'BS-LEVEL': 2, 'MS-LEVEL': 3, 'PHD-LEVEL': 4}

class Processing:
        def __init__(self, majors_patterns_path, degrees_patterns_path, skills_patterns_path):
            # No preprocessing logic is needed at the moment...
            self.skills_patterns_path = skills_patterns_path
            self.majors_patterns_path = majors_patterns_path
            self.degrees_patterns_path = degrees_patterns_path
            self.degrees_importance = DEGREES_IMPORTANCE
        
        def translate_from_french_to_english(self, cv_words):
            """This method will call pretrained model that translate text from frensh to english
            """
            with open('uploaded_files/Translation_From_Frensh_words_to_English.pkl', 'rb') as file:
              MODEL_AI = pickle.load(file)
              TEXT = MODEL_AI(cv_words)
              return TEXT[0]["translation_text"]
          
        def handle_text_when_length_sup_512(self, cv_words_before_translation_to_english):
                """This method is used to translate words from French to English when the length of the word is greater than 512 because the maximum characters that the model can handle is 512.
                """
                CV_WORDS_AFTER_TRANSLATE_WORDS_TO_ENGLISH = []
                for word in cv_words_before_translation_to_english:
                    try:
                        # Translate words from French to English
                        translated_word = self.translate_from_french_to_english(word) + " "
                        CV_WORDS_AFTER_TRANSLATE_WORDS_TO_ENGLISH.append(translated_word)
                    except Exception as e:
                        LEN_WORDS = len(word)
                        MIN_LEN = 0
                        MAX_LEN = 512
                        while LEN_WORDS > 0:
                            # Check if the length of the word is greater than 512
                            if LEN_WORDS > 512:
                                # Translate a segment of the word and add it to the result
                                translated_segment = self.translate_from_french_to_english(word[MIN_LEN:MAX_LEN])
                                CV_WORDS_AFTER_TRANSLATE_WORDS_TO_ENGLISH.append(translated_segment)
                                # Update indices and length for the next segment
                                MIN_LEN = MAX_LEN
                                MAX_LEN += 512
                                LEN_WORDS -= 512
                            else:
                                # Translate the remaining part of the word and add it to the result
                                translated_segment = self.translate_from_french_to_english(word[MIN_LEN:])
                                CV_WORDS_AFTER_TRANSLATE_WORDS_TO_ENGLISH.append(translated_segment)
                                break
                return CV_WORDS_AFTER_TRANSLATE_WORDS_TO_ENGLISH
        
        def match_majors_by_spacy(self,job):
            """
             Match majors mentioned in the text using spaCy's entity ruler.

             Parameters:
              - Resume (str): The text to process.

            Returns:
            - acceptable_majors (list): A list of acceptable majors found in the text.
            """

            nlp = English()
            # Add the pattern to the matcher
            patterns_path = "patterns/majors.jsonl"
            ruler = nlp.add_pipe("entity_ruler")
            ruler.from_disk(patterns_path)
            # Process some text
            doc1 = nlp(job)
            # Initialize an empty list to collect unique acceptable majors
            acceptable_majors = []
            # Iterate over the identified entities in the processed text
            for ent in doc1.ents:
                # Split the entity label to check if it's a major entity
                labels_parts = ent.label_.split('|')
                # If the entity label indicates a major
                if labels_parts[0] == 'MAJOR':
                    # Replace hyphens with spaces in the major name and check if it's not already in the list
                    if labels_parts[2].replace('-', ' ') not in acceptable_majors:
                        # Add the unique major to the list
                        acceptable_majors.append(labels_parts[2].replace('-', ' '))
            return acceptable_majors
        def match_skills_by_spacy(self, job):
            """
        Extracts skills mentioned in a job description/parsed_resume using spaCy entity recognition.

        Parameters:
            job (str)/parsed resume(as string): The  skills will be extracted from here.

        Returns:
            list: A list of unique skills mentioned in the job description/parsed resume.

        Example:
            >>> processing_instance = Processing()
            >>> job_description = "We are looking for candidates with proficiency in Python and SQL."
            >>> processing_instance.match_skills_by_spacy(job_description)
            ['Python', 'SQL']
        """
            nlp = English()
            patterns_path = "patterns/skills.jsonl"
            # Add the EntityRuler to the spaCy pipeline
            ruler = nlp.add_pipe("entity_ruler")
            # Load entity patterns from the specified JSONL file
            ruler.from_disk(patterns_path)
            # Process some text
            doc1 = nlp(job)
            # Initialize an empty list to collect unique job skills
            job_skills = []
            # Iterate over the identified entities in the processed text
            for ent in doc1.ents:
                # Split the entity label to check if it's a skill entity
                labels_parts = ent.label_.split('|')
                # If the entity label indicates a skill
                if labels_parts[0] == 'SKILL':
                # Replace hyphens with spaces in the skill name and check if it's not already in the list
                    if labels_parts[1].replace('-', ' ') not in job_skills:
                        job_skills.append(labels_parts[1].replace('-', ' '))
            return job_skills
        
        def match_degrees_by_spacy(self, job):
            """
                    Extracts degree levels mentioned in a parsed resume/job description using spaCy entity recognition.

                    Parameters:
                        job (str): The parsedd resume/job description  text from which degree levels will be extracted.

                    Returns:
                        list: A list of unique degree levels mentioned in the job description.

                    Example:
                        >>> processing_instance = Processing()
                        >>> job_description = "We are looking for candidates with a Bachelor's degree in Computer Science."
                        >>> processing_instance.match_degrees_by_spacy(job_description)
                        ['BS-LEVEL']
            """        
            nlp = English()
            # Add the pattern to the matcher
            patterns_path = "patterns/degrees.jsonl"
            ruler = nlp.add_pipe("entity_ruler")
            ruler.from_disk(patterns_path)
            # Process some text
            doc1 = nlp(job)
            # Initialize an empty list to collect unique degree levels
            degree_levels = []
            # Iterate over the identified entities in the processed text
            for ent in doc1.ents:
                # Split the entity label to check if it's a degree entity
                labels_parts = ent.label_.split('|')
                # If the entity label indicates a degree
                if labels_parts[0] == 'DEGREE':
                   # Check if the degree level is not already in the list
                    if labels_parts[1] not in degree_levels:
                        # Add the unique degree level to the list
                        degree_levels.append(labels_parts[1])
            return degree_levels

        def pdf_read(self, file_path):
            """Reads all the words from a PDF file and translates them to English.

            :param file_path: The path of the PDF file to read.

            :return: A list containing words from the PDF after translation to English.
            """
            # Initialize variables
            cv_words_after_translate = []

            # Read PDF file
            with open(file_path, 'rb') as file:
                pdf_reader = PdfReader(file)
                # Extract text from each page and append to the list
                for page in pdf_reader.pages:
                    cv_words_before_translate = page.extract_text()
                    cv_words_after_translate.append(cv_words_before_translate)

            # Translate paragraphs into English
            cv_words_after_translate = self.handle_text_when_length_sup_512(cv_words_after_translate)
            
            return cv_words_after_translate
        
        def define_type_of_file_and_make_action(self, file_path):
            """This method defines the type of the input file and runs the READ_PDF method if the file is a PDF.
            Otherwise, it will convert it into pdf. The return value will be None if the type of the file is not PDF or Word format.
            
            :param file_path: The CV file's path will be stored in this variable.
            :return: The extracted text from the file if it's successfully processed, or None if the file type is unsupported or processing fails.
            """
            try:
                if file_path.endswith(".pdf"):
                    return self.pdf_read(file_path)
                elif file_path.endswith(".docx"):
                    doc = aw.Document(file_path)
                    PATH = "output.pdf"
                    doc.save(PATH)
                    return self.pdf_read(PATH)
                else:
                    return None
            except Exception as e:
                # Add appropriate error handling/logging here
                print(f"Error occurred while processing file: {e}")
                return None    
            
        def translate_line_by_line(self, job_requirement):
            """Translate job offer From frensh to english
            """
            JOB_REQUIRMENTS = []
            # Open the text file
            with open(job_requirement, 'r') as file:
            # Iterate through each line in the file
                for line in file:
                    JOB_REQUIRMENTS.append(self.translate_from_french_to_english(line))
            return JOB_REQUIRMENTS
        
        def translate_line_by_linev2(self, job_requirement: str) -> list:
            """
            Translate job requirements line by line from French to English.

            Args:
                job_requirement (str): A string containing job requirements (can include multiple lines).

            Returns:
                list: A list of translated lines.
            """
            JOB_REQUIREMENTS = []
            
            # Split the input string into lines
            lines = job_requirement.splitlines()
            
            # Translate each line from French to English
            for line in lines:
                translated_line = self.translate_from_french_to_english(line)
                JOB_REQUIREMENTS.append(translated_line)
            
            return JOB_REQUIREMENTS

                
            
        def get_maximum_degree(self, degrees):
         """Get the maximum degree that the candidate has.
    
        Parameters:
        degrees (list): A list of degrees obtained by the candidate.
        
        Returns:
        str: The highest degree obtained by the candidate.

        Note:
        The 'degrees' parameter should be a list of strings representing the degrees.
        The 'degrees_importance' attribute should be a dictionary mapping degrees to their importance levels.
        Example: DEGREES_IMPORTANCE = {'high school': 0, 'associate': 1, 'BS-LEVEL': 2, 'MS-LEVEL': 3, 'PHD-LEVEL': 4}
    """
         d = {degree: self.degrees_importance[degree] for degree in degrees}
         return max(d, key=d.get)
        
        def get_minimum_degree(self, degrees):
         """Get the minimum degree required for the  job description
    
        Parameters:
        degrees (list): A list of degrees obtained by the candidate.
        
        Returns:
        str: The minimum degree required for the job description.

        Note:
        The 'degrees' parameter should be a list of strings representing the degrees.
        The 'degrees_importance' attribute should be a dictionary mapping degrees to their importance levels.
        Example: DEGREES_IMPORTANCE = {'high school': 0, 'associate': 1, 'BS-LEVEL': 2, 'MS-LEVEL': 3, 'PHD-LEVEL': 4}
    """
         d = {degree: self.degrees_importance[degree] for degree in degrees}
         return min(d, key=d.get)
          
        def extract_entities_from_resume(self, resume_list):
            """
        Extracts entities such as degrees, majors, and skills from a given resume.

        Args:
            resume_list (list): A list containing text segments of the resume.

        Returns:
            pd.DataFrame: A DataFrame containing the extracted entities.
        """
            # Convert the resume to a string
            cv_translated_as_a_string = ' '.join(resume_list)
            
            # Create an empty dataframe to store the extracted entities
            columns = ['Highest degree', 'Degrees', 'Major', 'Skill']
            extracted_entities_cv_df = pd.DataFrame(columns=columns)
   
            # Match degrees, majors, and skills using spaCy
            degrees = self.match_degrees_by_spacy(cv_translated_as_a_string)
            majors = self.match_majors_by_spacy(cv_translated_as_a_string)
            skills = self.match_skills_by_spacy(cv_translated_as_a_string)
            
            # Extract highest degree
            highest_degree = self.get_maximum_degree(degrees) if degrees else ""
            
            # Populate the dataframe with extracted entities
            extracted_entities_cv_df.loc[0] = [highest_degree, ', '.join(degrees), ', '.join(majors), ', '.join(skills)]
 
            # Assuming extracted_entities_df is your dataframe
            extracted_entities_cv_df.to_csv('extracted_entities_resume.csv', index=False)
        
            return extracted_entities_cv_df
        
        
        def extract_entities_from_job_description(self,job_description_string):
            """
        Extracts entities such as degrees, majors, and skills from a given job description.

        Args:
            Job description: A string containing a job description

        Returns:
            pd.DataFrame: A DataFrame containing the extracted entities.
        """
             
            # Create an empty dataframe to store the extracted entities
            columns = ['Minimum degree', 'Degrees', 'Major', 'Skill']
            extracted_entities_job_description_df = pd.DataFrame(columns=columns)
            
            # Match degrees, majors, and skills using spaCy
            degrees = self.match_degrees_by_spacy(job_description_string)
            majors = self.match_majors_by_spacy(job_description_string)
            skills = self.match_skills_by_spacy(job_description_string)
            
            # Extract highest degree
            minimum_degree = self.get_minimum_degree(degrees) if degrees else ""
            
            # Populate the dataframe with extracted entities
            extracted_entities_job_description_df.loc[0] = [minimum_degree, ', '.join(degrees), ', '.join(majors), ', '.join(skills)]
           
             # Assuming extracted_entities_df is your dataframe
            extracted_entities_job_description_df.to_csv('extracted_entities_jobdescription.csv', index=False)
            return extracted_entities_job_description_df
        
        def calculate_degree_score(self,job_min_degree, resume_degree):
            """
        Calculate a degree matching score based on the difference in degree importance.

        Parameters:
        - job_min_degree (str): The minimum degree required for the job.
        - resume_degree (str): The highest degree in the candidate's resume.

        Returns:
        - float: The degree matching score ranging from 0 to 1.
          - 1: If the job's minimum degree and the candidate's highest degree are the same.
          - 0.75: If the required degree is one level lower than the candidate's degree.
          - 0.5: If the difference is two levels.
          - 0.25: If the difference is higher than two levels.
          - 0: If the required degree is higher than the candidate's degree.
        """
            job_min_degree_importance = self.degrees_importance.get(job_min_degree, -1)
            resume_degree_importance = self.degrees_importance.get(resume_degree, -1)

            if job_min_degree_importance == -1 or resume_degree_importance == -1:
                return None  # Handle invalid degrees

            difference = resume_degree_importance - job_min_degree_importance

            if difference == 0:
                return 1
            elif difference == 1:
                return 0.75
            elif difference == 2:
                return 0.5
            elif difference > 2:
                return 0.25
            else:
                return 0  # If required degree > candidate degree
            
        def semantic_skills_similarity_sbert_base_v2(self,job_skills,resume_skills):
            """
                Calculate semantic similarity between job skills and resume skills using SBERT all-mpnet-base-v2.

                Parameters:
                - job_skills (list of str): List of job skills.
                - resume_skills (list of str): List of resume skills.

                Returns:
                - float: Semantic similarity score rounded to 3 decimal places.

            """
            model_path = "sentence-transformers/all-mpnet-base-v2"
            model = SentenceTransformer(model_path)
            #Encoding:
            score = 0
            sen = job_skills+resume_skills
            sen_embeddings = model.encode(sen)
            # Iterate over each job skill to calculate the similarity score
            for i in range(len(job_skills)):
                if job_skills[i] in resume_skills:
                    # If there is an exact match, increment the score by 1
                    score += 1
                else:
                    # If there is no exact match, calculate the cosine similarity between the job skill embedding
            # and all resume skill embeddings
                    # If the maximum cosine similarity is 0.4 or higher, add this maximum score to the total score
                    if max(cosine_similarity([sen_embeddings[i]],sen_embeddings[len(job_skills):])[0]) >= 0.4:
                        score += max(cosine_similarity([sen_embeddings[i]],sen_embeddings[len(job_skills):])[0])
            # Normalize the score by dividing it by the number of job skills to get the average match score
            score = score/len(job_skills)  
             # Return the final score rounded to three decimal places
            return round(score,3)   
        def get_major_categoryv3(self, major, labels_path_3):
            """
            Get major category for a specific major.

            Args:
                major (str): The major to get the category for.
                labels_path_3 (dict): A dictionary containing category information.

            Returns:
                list or None: A list of categories that the major belongs to, if found; otherwise None.
            """
            if 'MAJOR' in labels_path_3 and isinstance(labels_path_3['MAJOR'], dict):
                categories = set()
                for category, subcategories in labels_path_3['MAJOR'].items():
                    if major in subcategories:
                        categories.add(category)
                return list(categories) if categories else None
            return None

        def get_major_categoriesv3(self, majors, labels_path):
            """
            Get major categories for a list of majors.

            Args:
                majors (list): A list of majors.
                labels_path (dict): A dictionary containing category information.

            Returns:
                list or None: A list of unique major categories if found, otherwise None.
            """
            categories = set()
            for major in majors:
                category = self.get_major_categoryv3(major, labels_path)
                if category:
                    categories.update(category)
            return list(categories) if categories else None
        
        def score_major_match_old_way(self, exact_majors_from_job_description, exact_major_category_in_job_description, majors_from_resume, major_categoriesv3_from_resume):
            """
            Score the match between majors from a job description and those from a resume.

            Args:
                exact_majors_from_job_description (list): List of majors extracted from the job description.
                exact_major_category_in_job_description (str): Exact major category extracted from the job description.
                majors_from_resume (list): List of majors extracted from the resume.
                major_categoriesv3_from_resume (list): List of major categories extracted from the resume.

            Returns:
                float: Score indicating the match between majors from the job description and those from the resume.
                    1.0 if an exact match is found, 0.5 for partial match, and 0 otherwise.
            """
        # Initialize score to 0
            score = 0
            
            # Check if the major extracted from the job description exists in the list of majors from the resume
            if exact_majors_from_job_description in majors_from_resume:
                # If it exists, set the score to 1
                score = 1
            else:
                # Check for partial matches
                for major in major_categoriesv3_from_resume:
                    if major in exact_major_category_in_job_description:
                        score = 0.5
                        break  # Break out of the loop once a partial match is found
            
            return score
        def score_major_match(self, exact_majors_from_job_description, exact_major_category_in_job_description, majors_from_resume, major_categoriesv3_from_resume):
            """
            Score the match between majors from a job description and those from a resume.

            Args:
                exact_majors_from_job_description (list): List of majors extracted from the job description.
                exact_major_category_in_job_description (str): Exact major category extracted from the job description.
                majors_from_resume (list): List of majors extracted from the resume.
                major_categoriesv3_from_resume (list): List of major categories extracted from the resume.

            Returns:
                float: Score indicating the match between majors from the job description and those from the resume.
                    1.0 if an exact match is found,  and 0 otherwise.
            """
        # Initialize score to 0
            score = 0
            
            # Check if the major extracted from the job description exists in the list of majors from the resume
            if exact_majors_from_job_description in majors_from_resume:
                # If it exists, set the score to 1
                score = 1
                
            return score
        
        def calculate_final_score(self,score_degree, score_skills, score_major):
            """
            Calculate the final score as a percentage based on three scores.

            Args:
                score_degree (float): The score for degree, between 0 and 1.
                score_skills (float): The score for skills, between 0 and 1.
                score_major (float): The score for major, between 0 and 1.

            Returns:
                float: The final score as a percentage, rounded to two decimal places.
            """
            # Calculate the average of the three scores
            average_score = (score_degree + score_skills + score_major) / 3
            
            # Convert the average score to a percentage
            final_score_percentage = average_score * 100
            
            # Round the final score to two decimal places
            # final_score_percentage = round(final_score_percentage, 2)
            final_score_percentage = f"{round(final_score_percentage, 2)}%"

            
            return final_score_percentage

                    
       
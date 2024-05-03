from PyPDF2 import PdfReader
import pickle
import aspose.words as aw
import os
from spacy.lang.en import English
import pandas as pd
from resources import DEGREES_IMPORTANCE

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
            with open('model_loading/Translation_From_Frensh_words_to_English.pkl', 'rb') as file:
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
            acceptable_majors = []
            for ent in doc1.ents:
                labels_parts = ent.label_.split('|')
                if labels_parts[0] == 'MAJOR':
                    if labels_parts[2].replace('-', ' ') not in acceptable_majors:
                        acceptable_majors.append(labels_parts[2].replace('-', ' '))
                    if labels_parts[2].replace('-', ' ') not in acceptable_majors:
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
            ruler = nlp.add_pipe("entity_ruler")
            ruler.from_disk(patterns_path)
            # Process some text
            doc1 = nlp(job)
            job_skills = []
            for ent in doc1.ents:
                labels_parts = ent.label_.split('|')
                if labels_parts[0] == 'SKILL':
                    #print((ent.text, ent.label_))
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
            degree_levels = []
            for ent in doc1.ents:
                labels_parts = ent.label_.split('|')
                if labels_parts[0] == 'DEGREE':
                   # print((ent.text, ent.label_))
                    if labels_parts[1] not in degree_levels:
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
            
       
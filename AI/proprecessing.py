import pickle

class Processing:
    class Preprocessing:
        def __init__(self):
            # No preprocessing logic is needed at the moment...
            pass
        
        def translate_from_french_to_english(self, cv_words):
            """This method will call pretrained model that translate text from frensh to english
            """
            with open('Translation_From_French_words_to_English.pkl', 'rb') as file:
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

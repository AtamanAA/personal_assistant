import speech_recognition as sr


class AudioSolve:
    """
    Convert audio to text
    """
    def __init__(self, audio_file_path: str):
        self.audio_file_path = audio_file_path
        self.recognizer = sr.Recognizer()

    def _convert_audio_to_text(self):
        # Open the audio file
        with sr.AudioFile(self.audio_file_path) as source:
            # Record the audio data
            audio_data = self.recognizer.record(source)
            try:
                # Recognize the speech
                result_text = self.recognizer.recognize_google(audio_data)
                print("Recognized speech: ", result_text)
                return result_text
            except sr.UnknownValueError:
                print("Speech recognition could not understand the audio.")
                return None
            except sr.RequestError as e:
                print(f"Could not request results from service; {e}")
                return None

    def _convert_text_to_numbers(self, text):
        word_to_number = {
            'zero': 0, 'one': 1, 'two': 2, 'three': 3, 'four': 4,
            'five': 5, 'six': 6, 'seven': 7, 'eight': 8, 'nine': 9
        }

        words = text.split()
        numbers = []
        for word in words:
            # If the word is a number, convert it to integer and append to the list
            if word in word_to_number:
                numbers.append(word_to_number[word])
        return numbers

    def get_numbers_from_audio(self):
        text = self._convert_audio_to_text()
        numbers = self._convert_text_to_numbers(text=text)
        return numbers


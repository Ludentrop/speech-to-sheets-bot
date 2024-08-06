"""
This module implements the SpeechRecognition system to recognize a user speech.
"""
import speech_recognition as sr


def recognize_speech(file_path: str, language: str = "ru-RU") -> str:
    """
    The functon recognizes a speech from audio file.

    :param file_path: Path to audio file.
    :param language: Language of speech.
    :return: recognized speech.
    """
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)

    try:
        speech = r.recognize_google(audio, language=language)
        print("Вы сказали: " + speech)
        return speech
    except sr.UnknownValueError:
        return "Не удалось распознать речь"
    except sr.RequestError as e:
        return f"Could not request results from Google Speech Recognition service; {e}"

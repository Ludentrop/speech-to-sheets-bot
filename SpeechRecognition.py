"""
This module implements the SpeechRecognition system to recognize a user speech.
"""
import speech_recognition as sr


def recognize_speech(file_path: str, language: str = "ru-RU") -> str:
    """
    Recognize speech from audio file.

    :param file_path: path to audio file
    :param language: language of speech
    :return: recognized speech
    """
    r = sr.Recognizer()
    with sr.AudioFile(file_path) as source:
        audio = r.record(source)

    try:
        speech = r.recognize_google(audio, language=language)
        print("Вы сказали: " + speech)
        return speech
    except sr.UnknownValueError:
        print("Не удалось распознать речь")
    except sr.RequestError as e:
        print(
            "Could not request results from Google Speech Recognition service; {0}".format(
                e
            )
        )

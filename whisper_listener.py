import logging

from openai.types.audio.transcription import Transcription
from speech_recognition import (
    AudioData,
    Microphone,
    Recognizer,
    RequestError,
    UnknownValueError,
)

from bases.listener import Listener
from exceptions.failed_to_understand_listener_error import (
    FailedToUnderstandListenerError,
)
from exceptions.listener_fatal_error import ListenerFatalError
from exceptions.no_input_listener_error import (
    NoInputListenerError,
)
from models.input_device import InputDevice
from openai import OpenAI
import tempfile


class WhisperSpeechListener(Listener):
    """Class to listen to speech convert it to text"""

    def __init__(self, input_device: InputDevice, api_key: str) -> None:
        self._recognizer = Recognizer()
        self._input_device: InputDevice = input_device
        self._client = OpenAI(api_key=api_key)

    def listen(self) -> str:
        """
        Listen on the specified input device for speech and return the heard text.
        :return: the text from the speech listened to.
        """
        with Microphone(device_index=self._input_device.index) as source:
            logging.info(f"Listening for input with mic '{self._input_device.name}'...")
            audio: AudioData = self._recognizer.listen(source)
            logging.debug("Received speech input.")

        return self._recognize_text_in_audio(audio)

    def set_input_device(self, input_device: InputDevice) -> None:
        """Set the input device to use when listening.

        Args:
            input_device: The new input device to use for listening.
        """
        self._input_device = input_device

    def _recognize_text_in_audio(self, audio: AudioData) -> str:
        try:
            with tempfile.NamedTemporaryFile(suffix=".wav") as a:
                a.write(audio.get_wav_data())

                response: Transcription = self._client.audio.transcriptions.create(
                    model="whisper-1",
                    file=a.file,
                )
                text: str = response.text

            if text is None or len(text) == 0:
                raise NoInputListenerError("No speech detected in audio")

            logging.info(f"Speech: {text}")
            return text
        except UnknownValueError as unknown_value:
            raise FailedToUnderstandListenerError(
                "Google Speech Recognition could not understand audio"
            ) from unknown_value
        except RequestError as request_error:
            raise ListenerFatalError(
                "Error requesting results from Google Speech Recognition service"
            ) from request_error

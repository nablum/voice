from bases.listener import Listener
from bases.options_parser import OptionsParser
from bases.text_generator import TextGenerator
from bases.text_to_speech_client import TextToSpeechClient
from clients.apple_say_text_to_speech_client import (
    AppleSayTextToSpeechClient,
)
from clients.google_text_to_speech_client import (
    GoogleTextToSpeechClient,
)
from cli_parser import CommandLineParser
from clients.openai_text_to_speech_client import (
    OpenAITextToSpeechClient,
)
from computer_voice_responder import ComputerVoiceResponder
from conversation import Conversation
from helpers.get_input_device_from_user import (
    get_input_device_from_user,
)
from helpers.set_keyboard_interrupt_handler import (
    set_keyboard_interrupt_handler,
)
from helpers.set_log_level import set_log_level
from input_devices import InputDevices
from models.command_line_arguments import CommandLineArguments
from models.input_device import InputDevice
from open_ai_text_generator import OpenAITextGenerator
from whisper_listener import WhisperSpeechListener


def main() -> None:
    options_parser: OptionsParser = CommandLineParser()

    # parse the options passed in from the user
    options: CommandLineArguments = options_parser.parse()

    # set log level from CLI options
    set_log_level(options.log_level)

    # get all input devices on the current machine
    input_devices: list[InputDevice] = InputDevices.get_list_of_input_devices()

    # ask the user which input device to use for this session
    input_device: InputDevice = get_input_device_from_user(
        input_devices=input_devices, input_device_name=options.input_device_name
    )

    # service to listen for speech and convert it to text
    listener: Listener = WhisperSpeechListener(
        input_device,
        api_key=options.open_ai_key,
    )

    # service to generate text given an input
    text_generator: TextGenerator = OpenAITextGenerator(
        open_ai_key=options.open_ai_key, model=options.open_ai_model
    )

    # client to create speech from a given text
    text_to_speech_client: TextToSpeechClient

    if options.tts == "apple":
        text_to_speech_client = AppleSayTextToSpeechClient()
    elif options.tts == "google":
        text_to_speech_client = GoogleTextToSpeechClient(options.lang, options.tld)
    else:
        text_to_speech_client = OpenAITextToSpeechClient(api_key=options.open_ai_key)

    # service to respond to the user the generated text
    responder = ComputerVoiceResponder(
        text_to_speech_client, "temp_audio", options.speech_rate
    )

    # set interrupt to exit the process when Cmd+C / Ctrl+C is hit
    set_keyboard_interrupt_handler()

    conversation = Conversation(
        listener=listener,
        text_generator=text_generator,
        responder=responder,
        safe_word=options.safe_word,
        wake_word=options.wake_word,
    )

    conversation.start_conversation()


if __name__ == "__main__":
    main()

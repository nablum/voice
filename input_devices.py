import logging
from typing import cast

from pyaudio import PyAudio

from models.input_device import InputDevice
from models.pyaudio_device_info import PyAudioDeviceInfo


class InputDevices:
    """Class to interact with the current machines input devices."""

    py_audio = PyAudio()

    @staticmethod
    def get_list_of_input_devices() -> list[InputDevice]:
        """Get a list of input devices on the current machine.

        Returns:
            List of input device objects on the current machine.
        """
        logging.debug("InputDevices.get_list_of_input_devices called")

        pyaudio_input_devices: list[PyAudioDeviceInfo] = (
            InputDevices._get_all_pyaudio_input_devices()
        )
        input_devices: list[InputDevice] = []

        for input_device in pyaudio_input_devices:
            device_index: int = cast(int, input_device["index"])
            device_name: str = cast(str, input_device["name"])
            input_devices.append(InputDevice(device_index, device_name))

        logging.info(f"Found {len(input_devices)} input devices.")
        return input_devices

    @staticmethod
    def _get_all_pyaudio_input_devices() -> list[PyAudioDeviceInfo]:
        """Get a list of pyaudio input devices.

        Returns:
            A list of pyaudio input device objects.
        """
        all_devices: list[PyAudioDeviceInfo] = []
        count_of_input_devices: int = InputDevices.py_audio.get_device_count()

        for device_index in range(0, count_of_input_devices):
            device_info: PyAudioDeviceInfo = cast(
                PyAudioDeviceInfo,
                InputDevices.py_audio.get_device_info_by_index(device_index),
            )
            all_devices.append(device_info)

        return list(
            filter(lambda x: cast(int, x["maxInputChannels"]) >= 1, all_devices)
        )

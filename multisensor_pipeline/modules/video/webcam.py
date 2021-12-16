import sys
import os
from typing import Optional
from .video import PyAVSource


def _get_device_list_linux():
    devs = os.listdir('/dev')
    vid_indices = [int(dev[-1]) for dev in devs
                   if dev.startswith('video')]
    vid_indices = sorted(vid_indices)
    return vid_indices

def _get_device_list_mac():
    import subprocess
    cmd = "system_profiler SPCameraDataType | awk '/Unique ID:/ {print $3}'"
    result = subprocess.run(cmd, stdout=subprocess.PIPE, shell=True, check=True)
    serial_number = str(result.stdout.strip()).split("\\n")
    return list(range(len(serial_number)))


if sys.platform.startswith("win32"):
    from windows_capture_devices import get_capture_devices
elif sys.platform.startswith("linux"):
    get_capture_devices = _get_device_list_linux
elif sys.platform.startswith("darwin"):
    get_capture_devices = _get_device_list_mac
else:
    raise NotImplementedError(f"WebcamSource is currently not supported for the platform {sys.platform}")


def _get_av_format():
    if sys.platform.startswith("win32"):
        return "dshow"
    elif sys.platform.startswith("linux"):
        return "video4linux2"
    elif sys.platform.startswith("darwin"):
        return "avfoundation"
    else:
        raise NotImplementedError(f"WebcamSource is currently not supported for the platform {sys.platform}")


def _get_av_file_from_webcam_id(webcam_id: str):
    if sys.platform.startswith("win32"):
        return f"video={webcam_id}"
    elif sys.platform.startswith("linux"):
        return f"/dev/video{webcam_id}"
    elif sys.platform.startswith("darwin"):
        return f"{webcam_id}"
    else:
        raise NotImplementedError(f"WebcamSource is currently not supported for the platform {sys.platform}")


class WebcamSource(PyAVSource):

    def __init__(self, webcam_id: str, framerate: int = 30, options: Optional[dict] = None):
        self._webcam_id = webcam_id
        self._options = options if options is not None else {}
        self._options["framerate"] = str(framerate)
        super(WebcamSource, self).__init__(
            file=_get_av_file_from_webcam_id(webcam_id),
            av_format=_get_av_format(),
            av_options=self._options,
            playback_speed=float("inf")
        )

    @staticmethod
    def available_webcams():
        return get_capture_devices()

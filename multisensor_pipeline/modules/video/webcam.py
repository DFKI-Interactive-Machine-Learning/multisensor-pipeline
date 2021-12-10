import sys
from typing import Optional
from .video import PyAVSource


if sys.platform.startswith("win32"):
    from windows_capture_devices import get_capture_devices
elif sys.platform.startswith("linux"):
    raise NotImplementedError()
elif sys.platform.startswith("darwin"):
    raise NotImplementedError()
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
        return webcam_id
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

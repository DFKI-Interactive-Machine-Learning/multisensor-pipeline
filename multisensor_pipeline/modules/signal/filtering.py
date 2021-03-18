from multisensor_pipeline import BaseProcessor
from multisensor_pipeline.modules.signal.one_euro_filter import OneEuroFilter
import logging


logger = logging.getLogger(__name__)


class OneEuroProcessor(BaseProcessor):
    """
    Applies the 1€ smoothing filter on a continuous signal.
    Supports b'eyetracking.mobile.gaze' and b'eyetracking.mobile.surfaces'.

    To minimize jitter and lag when tracking human motion, the two parameters (fcmin and beta) can be set using a
    simple two-step procedure. First beta is set to 0 and fcmin (mincutoff) to a reasonable middle-ground value such
    as 1 Hz. Then the body part is held steady or moved at a very low speed while fcmin is adjusted to remove jitter
    and preserve an acceptable lag during these slow movements (decreasing fcmin reduces jitter but increases lag,
    fcmin must be > 0). Next, the body part is moved quickly in different directions while beta is increased with a
    focus on minimizing lag. First find the right order of magnitude to tune beta, which depends on the kind of data
    you manipulate and their units: do not hesitate to start with values like 0.001 or 0.0001. You can first
    multiply and divide beta by factor 10 until you notice an effect on latency when moving quickly. Note that
    parameters fcmin and beta have clear conceptual relationships: if high speed lag is a problem, increase beta;
    if slow speed jitter is a problem, decrease fcmin.
    """

    def __init__(self, freq=30, fcmin=1.5, beta=.001, dcutoff=1):

        super().__init__()

        config = {
            'freq': freq,  # Hz
            'mincutoff': fcmin,
            'beta': beta,  # FIXME
            'dcutoff': dcutoff  # this one should be ok
        }
        self._filter_x = OneEuroFilter(**config)
        self._filter_y = OneEuroFilter(**config)
        self._last_timestamp = None

    def _filter(self, sample):
        norm_pos = sample[b"norm_pos"]
        timestamp = sample[b"timestamp"]
        if self._last_timestamp is not None and self._last_timestamp >= timestamp:
            return None
        sample[b"norm_pos"] = self._filter_x(norm_pos[0], timestamp), self._filter_y(norm_pos[1], timestamp)
        self._last_timestamp = timestamp
        return sample

    def _update(self, frame=None):
        while self._active:
            topic, payload = self.get()

            if topic.decode().startswith("eyetracking.mobile.gaze"):
                sample = payload[b"norm_pos"]
            elif topic == b"eyetracking.mobile.surfaces":
                if len(payload[b"gaze_on_surfaces"]) > 0 and payload[b"gaze_on_surfaces"][-1][b"on_surf"]:
                    sample = payload[b"gaze_on_surfaces"][-1]
                else:
                    continue
            else:
                continue

            smooth_norm_pos = self._filter(sample)
            if smooth_norm_pos is not None:
                self._notify(topic, payload)

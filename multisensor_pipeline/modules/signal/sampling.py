from multisensor_pipeline.dataframe.dataframe import MSPDataFrame
from typing import Optional
import logging
import numpy as np

from multisensor_pipeline.modules import BaseProcessor

logger = logging.getLogger(__name__)


class DownsamplingProcessor(BaseProcessor):

    class DataFrameHistory:
        """Organize the history of a set of data frames."""

        def __init__(
            self,
            topic_uid, fps_out, window_size=5, interpolation=None
        ):
            self.topic_uid = topic_uid
            self.target_fps = fps_out

            # TODO: expose window_size, mainly for interpolation
            self.window_size = window_size

            # TODO: utilize interpolation for, e.g., averaging the data
            self.interpolation = interpolation

            self.target_period_time = 1. / self.target_fps
            self.last_sent = None
            self.dataframes = []
            self._timestamps_out = []  # for fps estimation

        def add(self, frame: MSPDataFrame):
            self.dataframes.append(frame)

        def _update_and_get_last_sample(self, sample_id):
            self.last_sent = self.dataframes[sample_id]
            # keep the last n timestamps for estimating actual frame-rate
            self._timestamps_out.append(self.last_sent.timestamp)
            if len(self._timestamps_out) > self.window_size:
                self._timestamps_out = self._timestamps_out[1:]
            # logger.info(f"{round(self.fps_out, 3)} fps (out)")
            # keep samples that arrived after the sent one
            self.dataframes = self.dataframes[sample_id + 1:]
            return self.last_sent

        def get_dataframe(self) -> Optional[MSPDataFrame]:
            assert len(self.dataframes) > 0, "there was no sample yet"

            # if nothing was sent before take first=last sample and reset the
            # list
            if self.last_sent is None:
                assert len(
                    self.dataframes) == 1, \
                    "if nothing was sent, there should be only one sample " \
                    "in the list"
                return self._update_and_get_last_sample(0)
            else:
                # check whether current sample shall be sent
                current_time = self.last_received.timestamp
                last_sent_time = self.last_sent.timestamp
                current_period_time = current_time - last_sent_time
                if current_period_time >= self.target_period_time:
                    # - self.current_delay:
                    # send sample that is closest to period time
                    # (+/- delay to keep up with target frame-rate)
                    recent_timestamps = \
                        np.array([s.timestamp for s in self.dataframes])
                    recent_time_diffs = np.fabs(
                        recent_timestamps -
                        last_sent_time -
                        self.target_period_time
                    )
                    sample_id = np.argmin(recent_time_diffs)
                    return self._update_and_get_last_sample(sample_id)
            return None

        @property
        def current_delay(self):
            """Return the deviation from the targeted period time."""
            return self.period_time_out - self.target_period_time

        @property
        def fps_out(self):
            return 1. / self.period_time_out

        @property
        def period_time_out(self):
            if len(self._timestamps_out) < self.window_size:
                return self.target_period_time
            else:
                period_time_estimate = \
                    (self._timestamps_out[-1] - self._timestamps_out[0]) / \
                    (len(self._timestamps_out) - 1)
                return period_time_estimate

        @property
        def last_received(self):
            return self.dataframes[-1]

        @property
        def fps_in(self):
            return 1. / self.period_time_in

        @property
        def period_time_in(self):
            return \
                (
                    self.dataframes[-1].timestamp -
                    self.dataframes[0].timestamp
                ) / len(self.dataframes)

    def __init__(self, topic_names=None, sampling_rate=5):
        """
        Downsample a signal.

        This respects the given sampling_rate [Hz], if the original rate is
        higher. Otherwise, the sampling rate stays the same. There is no
        upsampling happening in any case.

        @param topic_names: The dtype to be resampled; if None, all incoming
                            dtypes are resampled
        @param sampling_rate: The desired sampling rate [Hz]
        """
        super(DownsamplingProcessor, self).__init__()
        self._topic_names = topic_names
        self._sampling_rate = sampling_rate
        self._period_time = 1. / sampling_rate

        self._sample_hist = dict()
        self._last_sent = dict()
        self._last_received = dict()

    def _get_history(self, uid) -> DataFrameHistory:
        if uid not in self._sample_hist:
            self._sample_hist[uid] = \
                self.DataFrameHistory(uid, fps_out=self._sampling_rate)
        return self._sample_hist[uid]

    def on_update(self, frame: MSPDataFrame) -> Optional[MSPDataFrame]:
        if self._topic_names is None or frame.topic.name in self._topic_names:
            hist = self._get_history(frame.topic.uuid)
            hist.add(frame)
            _frame = hist.get_dataframe()
            if _frame is not None:
                _topic = \
                    self._generate_topic(
                        name=f"{frame.topic.name}.{self._sampling_rate}Hz",
                        dtype=frame.topic.dtype
                    )
                _frame.topic = _topic
                return _frame

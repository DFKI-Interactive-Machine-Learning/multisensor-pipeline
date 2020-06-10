from multisensor_pipeline.modules.base import BaseSource
from time import sleep
from myo import init, Hub, enums, DeviceListener
import logging

logger = logging.getLogger(__name__)


class MyoSensor(BaseSource, DeviceListener):
    hub = None
    feed = None
    myo = None

    def __init__(self, myo_sdk_path=None, interval=20):
        """
        :param myo_sdk_path: path to myo SDK: '[..]/bin'
        :param interval: capture time [ms]
        """
        super(MyoSensor, self).__init__()
        # initialize native myo library
        if myo_sdk_path:
            init(myo_sdk_path)
        else:
            init()

        # use Feed for constrained 50Hz polling
        #self.feed = Feed()
        self.hub = Hub()
        self.hub.run(interval, self)  # self.feed

    def _connect(self):
        try:
            self.myo = self.feed.wait_for_single_device(timeout=2.0)
            if not self.myo:
                logger.error("Could not connect to Myo...")
                return False
            #self.myo.set_stream_emg(enums.StreamEmg.enabled)
            #logging.info("Myo connected")
            return True

        except:
            self.hub.shutdown()
            return False

    # def _poll(self):
    #     if not self.myo:
    #         self._connect()
    #     try:
    #         assert self.myo is not None
    #         assert self.hub.running
    #         assert self.myo.connected
    #
    #         result = {
    #             'timestamp': time(),
    #             'acc': (self.myo.acceleration.x, self.myo.acceleration.y, self.myo.acceleration.z),
    #             'arm': self.myo.arm.name,
    #             'emg': self.myo.emg,
    #             'gyro': (self.myo.gyroscope.x, self.myo.gyroscope.y, self.myo.gyroscope.z),
    #             'rot': (self.myo.orientation.x, self.myo.orientation.y, self.myo.orientation.z, self.myo.orientation.w),
    #             'pose': self.myo.pose.name
    #         }
    #         return result
    #     except:
    #         self.hub.shutdown()

    def _update_loop(self):
        while self._active:
            sleep(0.5)
            # uncomment following for constrained 50Hz polling
            # t_start = time()
            # data = self._poll()
            # self._notify_all("myo", data)
            # dur = time() - t_start
            # sleep(max(0.0, 0.02 - 0.95 * dur))  # to achieve 50Hz (approx.)

    def on_connect(self, myo, timestamp, firmware_version):
        self._notify_all('myo.connected', {
            'timestamp': timestamp,
            'firmware': firmware_version
        })
        myo.set_stream_emg(enums.StreamEmg.enabled)

    def on_orientation_data(self, myo, timestamp, orientation):
        self._notify_all('myo.orientation', {
            'timestamp': timestamp,
            'orientation': (orientation.x, orientation.y, orientation.z, orientation.w)
        })

    def on_accelerometor_data(self, myo, timestamp, acceleration):
        self._notify_all('myo.acceleration', {
            'timestamp': timestamp,
            'acceleration': (acceleration.x, acceleration.y, acceleration.z)
        })

    def on_gyroscope_data(self, myo, timestamp, gyroscope):
        self._notify_all('myo.gyroscope', {
            'timestamp': timestamp,
            'gyroscope': (gyroscope.x, gyroscope.y, gyroscope.z)
        })

    def on_emg_data(self, myo, timestamp, emg):
        self._notify_all('myo.emg', {
            'timestamp': timestamp,
            'emg': emg
        })

    def _stop(self):
        if self.hub:
            self.hub.shutdown()

from multisensor_pipeline.modules.gesture.myo import MyoSensor
from queue import Queue
import argparse


if __name__ == '__main__':
    parser = argparse.ArgumentParser(description='Myo wristband example.')
    parser.add_argument('myo_sdk', required=True, help="Path to the /bin directory of the Myo SDK (tested with v0.9)")

    args = parser.parse_args()
    path_to_myo_sdk = args.myo_sdk

    queue = Queue()

    try:
        myo = MyoSensor(path_to_myo_sdk)
        myo.add_observer(queue)
        myo.start()

        while True:
            dtype, data = queue.get()
            print(dtype, data)

    except:
        pass

    myo.stop()

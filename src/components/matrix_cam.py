import ctypes
import numpy as np
from mvIMPACT import acquire


class MatrixCam:
    def __init__(self, cam_id: int = 0):
        """
        MatrixCam
        :param cam_id: id for use the camera
        """

        # cam id for use the camera
        self.cam_id = cam_id

        # initialize the device and open it
        devMgr = acquire.DeviceManager()
        cam = devMgr.getDevice(cam_id)
        cam.open()

        # initialize ac setting
        self.ac = acquire.AcquisitionControl(cam)
        self.exposure = self.ac.exposureTime.read()
        self.gain = 0
        self.pPreviousRequest = None

        cam.close()

    def close(self) -> None:
        """
        Close the camera
        :return: none
        """
        self.pPreviousRequest = None

    def set_exposure(self, exposure: float) -> None:
        """
        Set exposure time of the camera
        :param exposure: exposure time
        :return: none
        """

        # initialize ac setting and write new exposure
        devMgr = acquire.DeviceManager()
        cam = devMgr.getDevice(self.cam_id)
        cam.open()
        ac = acquire.AcquisitionControl(cam)
        ac.exposureTime.write(exposure)
        self.exposure = exposure
        cam.close()

    @staticmethod
    def reset_the_queue(device_interface) -> None:
        """
        Reset buffer queue
        :param device_interface: FunctionInterface of the camera
        return: none
        """
        # reset the queue
        request_number = device_interface.imageRequestWaitFor(0)
        while request_number >= 0:
            request = device_interface.getRequest(request_number)
            request.unlock()
            request_number = device_interface.imageRequestWaitFor(0)
        device_interface.imageRequestReset(0, 0)

        # pre-fill the buffer and start the infinite loop
        image_request_result = device_interface.imageRequestSingle()
        while image_request_result == acquire.DMR_NO_ERROR:
            image_request_result = device_interface.imageRequestSingle()

    @staticmethod
    def get_one_channel_image(request) -> np.ndarray:
        """
        Get one channel image
        :param request: request of shot
        :return: image
        """

        # set number of channel and dimension
        channel_count = 1
        height = request.imageHeight.read()
        width = request.imageWidth.read()

        # generate image
        img_data = request.imageData.read()
        c_buf = (ctypes.c_char * height * width).from_address(int(img_data))
        img = np.frombuffer(c_buf, dtype=np.uint8)
        img.shape = (height, width, channel_count)

        return img

    def acquire_frames(self, device, device_interface, time_out, total_frames) -> np.ndarray:
        """
        Acquire frames
        :param device: camera
        :param device_interface: FunctionInterface of the camera
        :param time_out: parameter for loop
        :param total_frames: number of frames that I want to acquire
        :return: output image
        """

        img_saved = 0
        previous_request = None

        # create a circular buffer
        format_control = acquire.ImageFormatControl(device)
        img_height = int(format_control.height.readS())
        img_width = int(format_control.width.readS())

        # set variables
        img_counter = 0
        buffer_capacity = 3
        batch_size = 1
        buffer_total_length = buffer_capacity * batch_size
        img_buffer = np.zeros((img_height, img_width, buffer_capacity * batch_size), dtype=np.uint8)
        out_images = []

        # acquisition loop
        while img_saved < total_frames:
            request_number = device_interface.imageRequestWaitFor(time_out)
            if device_interface.isRequestNrValid(request_number):
                request = device_interface.getRequest(request_number)
                if request.isOK:
                    img = self.get_one_channel_image(request)

                    # Save a copy on circular buffer
                    np.copyto(img_buffer[:, :, img_counter % buffer_total_length], img[:, :, 0])
                    current_image = np.copy(img)
                    out_images.append(current_image)
                    img_saved += 1

                if previous_request is not None:
                    previous_request.unlock()
                previous_request = request

            # the buffer must be filled again with another request
            device_interface.imageRequestSingle()

        return out_images

    def take_photo(self) -> np.ndarray:
        """
        Take photo
        :return: output image
        """

        timeout = -1

        # set the device and open it
        devMgr = acquire.DeviceManager()
        device = devMgr.getDevice(self.cam_id)
        device.open()
        device_interface = acquire.FunctionInterface(device)
        print('Camera {:s} started acquisition...'.format(device.serial.read()))
        self.reset_the_queue(device_interface)

        try:
            result_image = self.acquire_frames(device, device_interface, timeout, 1)[0]
        except Exception as e:
            print(str(e))
        finally:
            device.close()
            print('The camera {:s} is closed'.format(device.serial.read()))

        return result_image

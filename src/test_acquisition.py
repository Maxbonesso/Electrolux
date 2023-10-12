from __future__ import print_function
import ctypes
import cv2
import numpy as np
from mvIMPACT import acquire

from src.components.matrix_cam import MatrixCam


def main():
    # Get a pointer to the first device found
    devMgr = acquire.DeviceManager()
    pDev = devMgr.getDevice(0)
    pDev.close()
    # initialise it(this step is optional as this will be done automatically from
    # all other wrapper classes that accept a device pointer):
    pDev.open()
    ac = acquire.AcquisitionControl(pDev)
    ac.exposureTime.write(100000)

    # create an instance of the function interface for this device
    fi = acquire.FunctionInterface(pDev)
    pPreviousRequest = None
    while fi.imageRequestSingle() == acquire.DMR_NO_ERROR:
        print("Buffer queued")
    while True:
        requestNr = fi.imageRequestWaitFor(10000)
        if fi.isRequestNrValid(requestNr):
            pRequest = fi.getRequest(requestNr)
            if pRequest.isOK:
                cbuf = (ctypes.c_char * pRequest.imageSize.read()).from_address(int(pRequest.imageData.read()))
                channelType = np.uint16 if pRequest.imageChannelBitDepth.read() > 8 else np.uint8

                cv_img = np.frombuffer(cbuf, dtype=channelType)
                cv_img.shape = (
                    pRequest.imageHeight.read(), pRequest.imageWidth.read(), pRequest.imageChannelCount.read())
                cv2.namedWindow("test2", cv2.WINDOW_NORMAL)
                cv2.imshow("test2", cv_img)
                cv2.waitKey(0)

            if pPreviousRequest is not None:
                pPreviousRequest.unlock()
            pPreviousRequest = pRequest
            fi.imageRequestSingle()
        else:
            print("imageRequestWaitFor failed (" + str(
                requestNr) + ", " + acquire.ImpactAcquireException.getErrorCodeAsString(requestNr) + ")")

    pDev.close()

def main2():
    cam = MatrixCam()
    cam.set_exposure(120000)
    cam.set_config()
    devMgr = acquire.DeviceManager()
    pDev = devMgr.getDevice(0)
    fi = acquire.FunctionInterface(pDev)

    pPreviousRequest = None
    while fi.imageRequestSingle() == acquire.DMR_NO_ERROR:
        print("Buffer queued")
    requestNr = fi.imageRequestWaitFor(120000)
    while True:
        if fi.isRequestNrValid(requestNr):
            pRequest = fi.getRequest(requestNr)
            if pRequest.isOK:
                cbuf = (ctypes.c_char * pRequest.imageSize.read()).from_address(int(pRequest.imageData.read()))
                channelType = np.uint16 if pRequest.imageChannelBitDepth.read() > 8 else np.uint8

                cv_img = np.frombuffer(cbuf, dtype=channelType)
                cv_img.shape = (
                    pRequest.imageHeight.read(), pRequest.imageWidth.read(), pRequest.imageChannelCount.read())
                cv2.namedWindow("test", cv2.WINDOW_NORMAL)
                cv2.imshow("test", cv_img)
                cv2.imwrite('data/acquisizione1/forno1_parallelo_00_120728.png', cv_img)
                break
            if pPreviousRequest is not None:
                pPreviousRequest.unlock()
            pPreviousRequest = pRequest
            fi.imageRequestSingle()


if __name__ == '__main__':
    main2()

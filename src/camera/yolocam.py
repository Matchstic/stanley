from .base import BaseCamera
from .detection import Detection

from pathlib import Path
import depthai as dai
import numpy as np
import time
import cv2
import threading

from ..constants import DETECTION_THRESH

THREAD_STOP = False

def thread(callback, _pipeline, outputFrames):
    with dai.Device(_pipeline) as device:
        # Output queues will be used to get the rgb frames and nn data from the outputs defined above
        previewQueue = device.getOutputQueue(name="rgb", maxSize=4, blocking=False)
        detectionNNQueue = device.getOutputQueue(name="detections", maxSize=4, blocking=False)
        xoutBoundingBoxDepthMappingQueue = device.getOutputQueue(name="boundingBoxDepthMapping", maxSize=4, blocking=False)
        depthQueue = device.getOutputQueue(name="depth", maxSize=4, blocking=False)

        startTime = time.monotonic()
        counter = 0
        fps = 0
        color = (255, 255, 255)

        while THREAD_STOP == False:
            inPreview = previewQueue.get()
            inDet = detectionNNQueue.get()
            depth = depthQueue.get()

            frame = None
            depthFrame = None

            if outputFrames:
                frame = inPreview.getCvFrame()
                depthFrame = depth.getFrame() # depthFrame values are in millimeters

                depthFrameColor = cv2.normalize(depthFrame, None, 255, 0, cv2.NORM_INF, cv2.CV_8UC1)
                depthFrameColor = cv2.equalizeHist(depthFrameColor)
                depthFrameColor = cv2.applyColorMap(depthFrameColor, cv2.COLORMAP_HOT)

            counter+=1
            current_time = time.monotonic()
            if (current_time - startTime) > 1 :
                fps = counter / (current_time - startTime)
                counter = 0
                startTime = current_time

            detections = inDet.detections
            if outputFrames and len(detections) != 0:
                boundingBoxMapping = xoutBoundingBoxDepthMappingQueue.get()
                roiDatas = boundingBoxMapping.getConfigData()

                for roiData in roiDatas:
                    roi = roiData.roi
                    roi = roi.denormalize(depthFrameColor.shape[1], depthFrameColor.shape[0])
                    topLeft = roi.topLeft()
                    bottomRight = roi.bottomRight()
                    xmin = int(topLeft.x)
                    ymin = int(topLeft.y)
                    xmax = int(bottomRight.x)
                    ymax = int(bottomRight.y)

                    cv2.rectangle(depthFrameColor, (xmin, ymin), (xmax, ymax), color, cv2.FONT_HERSHEY_SCRIPT_SIMPLEX)

            # If the frame is available, draw bounding boxes on it and show the frame
            height = 0
            width = 0

            if outputFrames:
                height = frame.shape[0]
                width  = frame.shape[1]

            personDetections = []
            for detection in detections:
                if detection.label == 0:
                    personDetections.append(Detection(detection.spatialCoordinates.x, detection.spatialCoordinates.y, detection.spatialCoordinates.z, detection.confidence, fps))

                    if outputFrames:
                        # Denormalize bounding box
                        x1 = int(detection.xmin * width)
                        x2 = int(detection.xmax * width)
                        y1 = int(detection.ymin * height)
                        y2 = int(detection.ymax * height)

                        cv2.putText(frame, "{:.2f}".format(detection.confidence*100), (x1 + 10, y1 + 35), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                        cv2.putText(frame, f"X: {int(detection.spatialCoordinates.x)} mm", (x1 + 10, y1 + 50), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                        cv2.putText(frame, f"Y: {int(detection.spatialCoordinates.y)} mm", (x1 + 10, y1 + 65), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)
                        cv2.putText(frame, f"Z: {int(detection.spatialCoordinates.z)} mm", (x1 + 10, y1 + 80), cv2.FONT_HERSHEY_TRIPLEX, 0.5, 255)

                        cv2.rectangle(frame, (x1, y1), (x2, y2), color, cv2.FONT_HERSHEY_SIMPLEX)

            if outputFrames:
                cv2.putText(frame, "NN fps: {:.2f}".format(fps), (2, frame.shape[0] - 4), cv2.FONT_HERSHEY_TRIPLEX, 0.4, color)

            callback(personDetections, frame if outputFrames else None)

        previewQueue.close()
        detectionNNQueue.close()
        xoutBoundingBoxDepthMappingQueue.close()
        depthQueue.close()

BLOB_PATH = str((Path(__file__).parent / Path('../../models/yolo-v4-tiny-tf_openvino_2021.4_6shave.blob')).resolve().absolute())

class YoloCamera(BaseCamera):

    _thread = None
    _detections = None
    _userCallback = None

    def __init__(self, callback = None):
        self.setup()
        self._userCallback = callback

    def setup(self):
        # Create pipeline
        self._pipeline = dai.Pipeline()

        # Define sources and outputs
        self._camRgb = self._pipeline.create(dai.node.ColorCamera)
        self._spatialDetectionNetwork = self._pipeline.create(dai.node.YoloSpatialDetectionNetwork)
        self._monoLeft = self._pipeline.create(dai.node.MonoCamera)
        self._monoRight = self._pipeline.create(dai.node.MonoCamera)
        self._stereo = self._pipeline.create(dai.node.StereoDepth)

        self._xoutRgb = self._pipeline.create(dai.node.XLinkOut)
        self._xoutNN = self._pipeline.create(dai.node.XLinkOut)
        self._xoutBoundingBoxDepthMapping = self._pipeline.create(dai.node.XLinkOut)
        self._xoutDepth = self._pipeline.create(dai.node.XLinkOut)

        self._xoutRgb.setStreamName("rgb")
        self._xoutNN.setStreamName("detections")
        self._xoutBoundingBoxDepthMapping.setStreamName("boundingBoxDepthMapping")
        self._xoutDepth.setStreamName("depth")

        # Properties
        self._camRgb.setPreviewSize(416, 416)
        self._camRgb.setResolution(dai.ColorCameraProperties.SensorResolution.THE_1080_P)
        self._camRgb.setInterleaved(False)
        self._camRgb.setColorOrder(dai.ColorCameraProperties.ColorOrder.BGR)

        self._monoLeft.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self._monoLeft.setBoardSocket(dai.CameraBoardSocket.LEFT)
        self._monoRight.setResolution(dai.MonoCameraProperties.SensorResolution.THE_400_P)
        self._monoRight.setBoardSocket(dai.CameraBoardSocket.RIGHT)

        # setting node configs
        self._stereo.setDefaultProfilePreset(dai.node.StereoDepth.PresetMode.HIGH_DENSITY)

        self._spatialDetectionNetwork.setBlobPath(BLOB_PATH)
        self._spatialDetectionNetwork.setConfidenceThreshold(DETECTION_THRESH)
        self._spatialDetectionNetwork.input.setBlocking(False)
        self._spatialDetectionNetwork.setBoundingBoxScaleFactor(0.5)
        self._spatialDetectionNetwork.setDepthLowerThreshold(100)
        self._spatialDetectionNetwork.setDepthUpperThreshold(10000)

        # Yolo specific parameters
        self._spatialDetectionNetwork.setNumClasses(80)
        self._spatialDetectionNetwork.setCoordinateSize(4)
        self._spatialDetectionNetwork.setAnchors(np.array([10,14, 23,27, 37,58, 81,82, 135,169, 344,319]))
        self._spatialDetectionNetwork.setAnchorMasks({ "side26": np.array([1,2,3]), "side13": np.array([3,4,5]) })
        self._spatialDetectionNetwork.setIouThreshold(0.5)

        # Linking
        self._monoLeft.out.link(self._stereo.left)
        self._monoRight.out.link(self._stereo.right)

        self._camRgb.preview.link(self._spatialDetectionNetwork.input)
        self._spatialDetectionNetwork.passthrough.link(self._xoutRgb.input)

        self._spatialDetectionNetwork.out.link(self._xoutNN.input)
        self._spatialDetectionNetwork.boundingBoxMapping.link(self._xoutBoundingBoxDepthMapping.input)

        self._stereo.depth.link(self._spatialDetectionNetwork.inputDepth)
        self._spatialDetectionNetwork.passthroughDepth.link(self._xoutDepth.input)

    def start(self):
        self._thread = threading.Thread(target=thread, args=(self._callback, self._pipeline, self._userCallback != None))
        self._thread.start()

    def stop(self):
        global THREAD_STOP
        THREAD_STOP = True

        self._thread.join()

    def _callback(self, detections, frame):
        self._detections = detections

        if self._userCallback != None:
            self._userCallback(detections, frame)

    def detections(self):
        return self._detections
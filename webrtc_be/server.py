import sys
import numpy as np
import os.path
import time
import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid
import fractions
import cv2
from aiohttp import web
from av import AudioFrame, VideoFrame

import requests
from threading import Thread
from time import sleep
from bs4 import BeautifulSoup
from kafka import KafkaConsumer, KafkaProducer

from aiortc import RTCPeerConnection, RTCSessionDescription , VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder
from pyee import EventEmitter

app = web.Application()
# from yolo_test.object_detection_yolo import detect_object

ROOT = os.path.dirname(__file__)

logger = logging.getLogger("pc")
pcs = set()

pc_broadcast = None
local_video_share = None
# This code is written at BigVision LLC. It is based on the OpenCV project. It is subject to the license terms in the LICENSE file found in this distribution and at http://opencv.org/license.html

# Usage example:  python3 object_detection_yolo.py --video=run.mp4
#                 python3 object_detection_yolo.py --image=bird.jpg

'''

# Initialize the parameters
#AUDIO_PTIME = 0.020  # 20ms audio packetization
AUDIO_PTIME = 0.20 
VIDEO_CLOCK_RATE = 90000
#VIDEO_PTIME = 1 / 30  # 30fps
VIDEO_PTIME = 1 / 3
VIDEO_TIME_BASE = fractions.Fraction(1, VIDEO_CLOCK_RATE)
'''
confThreshold = 0.3  #Confidence threshold
nmsThreshold = 0.3   #Non-maximum suppression threshold
inpWidth = 160       #Width of network's input image
inpHeight = 160      #Height of network's input image
parser = argparse.ArgumentParser(description='Object Detection using YOLO in OPENCV')
parser.add_argument('--image', help='Path to image file.')
parser.add_argument('--video', help='Path to video file.')
args = parser.parse_args()
        
# Load names of classes
# classesFile = "coco.names"
classesFile = "yolo_test/coco.names"
classes = None
with open(classesFile, 'rt') as f:
    classes = f.read().rstrip('\n').split('\n')

# Give the configuration and weight files for the model and load the network using them.
modelConfiguration = "yolo_test/yolov3.cfg"
modelWeights = "yolo_test/yolov3.weights"
# modelConfiguration = "yolov3.cfg"
# modelWeights = "yolov3.weights"

net = cv2.dnn.readNetFromDarknet(modelConfiguration, modelWeights)
net.setPreferableBackend(cv2.dnn.DNN_BACKEND_OPENCV)
net.setPreferableTarget(cv2.dnn.DNN_TARGET_CPU)

#detect function call
def detect_object(frame):
    blob = cv2.dnn.blobFromImage(frame, 1/255, (inpWidth, inpHeight), [0,0,0], 1, crop=False)
    net.setInput(blob)
    outs = net.forward(getOutputsNames(net))
    postprocess(frame, outs)
    return frame

class VideoTransformTrack(VideoStreamTrack):
    def __init__(self, track, transform):
        super().__init__()  # don't forget this!
        self.track = track
        self.transform = transform
        self.skip = 1
        

    async def recv(self):

        # frame = await self.track.read()
        frame = await self.track.recv()

        if self.skip < 10 :
            if hasattr(self, "oldframe"):
                #print ('old:',self.skip)
                self.skip = self.skip+1
                return self.oldframe
            else:
                self.skip = self.skip+1
                return frame    
        else:
            self.skip = 1

        if not frame:
            return
        #if (countnum % 2 == 0):
        #    print ('pass')

        if self.transform == "cartoon":
            img = frame.to_ndarray(format="bgr24")

            # prepare color
            img_color = cv2.pyrDown(cv2.pyrDown(img))
            for _ in range(6):
                img_color = cv2.bilateralFilter(img_color, 9, 9, 7)
            img_color = cv2.pyrUp(cv2.pyrUp(img_color))

            # prepare edges
            img_edges = cv2.cvtColor(img, cv2.COLOR_RGB2GRAY)
            img_edges = cv2.adaptiveThreshold(
                cv2.medianBlur(img_edges, 7),
                255,
                cv2.ADAPTIVE_THRESH_MEAN_C,
                cv2.THRESH_BINARY,
                9,
                2,
            )
            img_edges = cv2.cvtColor(img_edges, cv2.COLOR_GRAY2RGB)

            # combine color and edges
            img = cv2.bitwise_and(img_color, img_edges)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == "edges":
            # perform edge detection
            img = frame.to_ndarray(format="bgr24")
            img = cv2.cvtColor(cv2.Canny(img, 100, 200), cv2.COLOR_GRAY2BGR)

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame
        elif self.transform == "rotate":
            # rotate image
            img = frame.to_ndarray(format="bgr24")
            rows, cols, _ = img.shape
            M = cv2.getRotationMatrix2D((cols / 2, rows / 2), frame.time * 45, 1)
            img = cv2.warpAffine(img, M, (cols, rows))

            # rebuild a VideoFrame, preserving timing information
            new_frame = VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            return new_frame

        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
        #@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@@#
        elif self.transform == "caicai":
            img = frame.to_ndarray(format="bgr24")
            detect_object(img)
            new_frame =VideoFrame.from_ndarray(img, format="bgr24")
            new_frame.pts = frame.pts
            new_frame.time_base = frame.time_base
            self.oldframe = new_frame
            return new_frame
        else:
            return frame


async def index(request):
    content = open(os.path.join(ROOT, "index.html"), "r").read()
    return web.Response(content_type="text/html", text=content)


async def javascript(request):
    content = open(os.path.join(ROOT, "client.js"), "r").read()
    return web.Response(content_type="application/javascript", text=content)

def destroy_broadcast(request):
    global pc_broadcast
    pc_broadcast = None
    return web.Response(content_type="application/javascript", text={"status": "success"})

async def i_want_an_offer(request):
    global pc_broadcast
    pc_broadcast = RTCPeerConnection()

    if local_video_share is not None:
        pc_broadcast.addTrack(local_video_share)

    offer = await pc_broadcast.createOffer()
    await pc_broadcast.setLocalDescription(offer)


    @pc_broadcast.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc_broadcast.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        log_info("ICE connection state is %s", pc_broadcast.iceConnectionState)
        if pc_broadcast.iceConnectionState == "failed":
            await pc_broadcast.close()


    # @pc.on("track")
    # def on_track(track):
    #     log_info("Track %s received", track.kind)

    #     # if track.kind == "audio":
    #     #     pc.addTrack(player.audio)
    #     #     recorder.addTrack(track)
    #     if track.kind == "video":
    #         local_video = VideoTransformTrack(
    #             track, transform=params["video_transform"]
    #         )
    #         pc.addTrack(local_video)

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            # await recorder.stop()

    

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc_broadcast.localDescription.sdp, "type": pc_broadcast.localDescription.type}
        ),
    )

async def give_back_answer(request):
    pc = pc_broadcast
    params = await request.json()
    answer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])
    await pc.setRemoteDescription(answer)
    return web.Response(content_type="application/json",
        text=json.dumps(
            {"sdp": None, "type": None}
        ))


async def offer(request):
    # print("we are in", await request.body)

    # sdp = request.form['sdp']
    # type1 = request.form['type']
    params = await request.json()
    #print(params)
    offer = RTCSessionDescription(sdp=params["sdp"], type=params["type"])

    pc = RTCPeerConnection()
    pc_id = "PeerConnection(%s)" % uuid.uuid4()
    pcs.add(pc)

    def log_info(msg, *args):
        logger.info(pc_id + " " + msg, *args)

    log_info("Created for %s", request.remote)

    # prepare local media
    # player = MediaPlayer(os.path.join(ROOT, "demo-instruct.wav"))
    # if args.write_audio:
    #     recorder = MediaRecorder(args.write_audio)
    # else:
    #     recorder = MediaBlackhole()

    @pc.on("datachannel")
    def on_datachannel(channel):
        @channel.on("message")
        def on_message(message):
            if isinstance(message, str) and message.startswith("ping"):
                channel.send("pong" + message[4:])

    @pc.on("iceconnectionstatechange")
    async def on_iceconnectionstatechange():
        log_info("ICE connection state is %s", pc.iceConnectionState)
        if pc.iceConnectionState == "failed":
            await pc.close()
            pcs.discard(pc)

    @pc.on("track")
    def on_track(track):
        log_info("Track %s received", track.kind)

        # if track.kind == "audio":
        #     pc.addTrack(player.audio)
        #     recorder.addTrack(track)
        if track.kind == "video":
            local_video = VideoTransformTrack(
                track, transform=params["video_transform"]
            )
            global local_video_share 
            local_video_share = local_video
            pc.addTrack(local_video)

        @track.on("ended")
        async def on_ended():
            log_info("Track %s ended", track.kind)
            # await recorder.stop()

    # handle offer
    await pc.setRemoteDescription(offer)
    # await recorder.start()

    # send answer
    answer = await pc.createAnswer()
    await pc.setLocalDescription(answer)

    return web.Response(
        content_type="application/json",
        text=json.dumps(
            {"sdp": pc.localDescription.sdp, "type": pc.localDescription.type}
        ),
    )


async def on_shutdown(app):
    # close peer connections
    coros = [pc.close() for pc in pcs]
    await asyncio.gather(*coros)
    pcs.clear()



# Get the names of the output layers
def getOutputsNames(net):
    # Get the names of all the layers in the network
    layersNames = net.getLayerNames()
    #print("the layers names", layersNames)
    # Get the names of the output layers, i.e. the layers with unconnected outputs
    return [layersNames[i[0] - 1] for i in net.getUnconnectedOutLayers()]

# Draw the predicted bounding box
def drawPred(frame, classId, conf, left, top, right, bottom):
    # Draw a bounding box.
    #print("drawing pred", frame)
    cv2.rectangle(frame, (left, top), (right, bottom), (255, 0, 0), 1)
    
    label = '%.2f' % conf
        
    # Get the label for the class name and its confidence
    if classes:
        assert(classId < len(classes))
        label = '%s:%s' % (classes[classId], label)

    #Display the label at the top of the bounding box
    labelSize, baseLine = cv2.getTextSize(label, cv2.FONT_HERSHEY_SIMPLEX, 0.5, 1)
    top = max(top, labelSize[1])
    cv2.rectangle(frame, (left, top - round(labelSize[1])), (left + round(labelSize[0]), top + baseLine), (0, 255, 255), 1)
    cv2.putText(frame, label, (left, top), cv2.FONT_HERSHEY_SIMPLEX, 0.55, (0,255,255), 1)

# Remove the bounding boxes with low confidence using non-maxima suppression
def postprocess(frame, outs):
    #print("pos", outs, frame.shape)
    frameHeight = frame.shape[0]
    frameWidth = frame.shape[1]

    # Scan through all the bounding boxes output from the network and keep only the
    # ones with high confidence scores. Assign the box's class label as the class with the highest score.
    classIds = []
    confidences = []
    boxes = []
    for out in outs:
        #print("the out", out)
        for detection in out:
            #print(detection)
            scores = detection[5:]
            classId = np.argmax(scores)
            #print("pass")
            confidence = scores[classId]
            if confidence > confThreshold:
                center_x = int(detection[0] * frameWidth)
                center_y = int(detection[1] * frameHeight)
                width = int(detection[2] * frameWidth)
                height = int(detection[3] * frameHeight)
                left = int(center_x - width / 2)
                top = int(center_y - height / 2)
                classIds.append(classId)
                confidences.append(float(confidence))
                boxes.append([left, top, width, height])

    # Perform non maximum suppression to eliminate redundant overlapping boxes with
    # lower confidences.
    #print("before")
    indices = cv2.dnn.NMSBoxes(boxes, confidences, confThreshold, nmsThreshold)
    #print("the indices", indices)
    #print("the boxes", boxes)
    #print("the classIds", classId)
    for i in indices:
        i = i[0]
        box = boxes[i]
        left = box[0]
        top = box[1]
        width = box[2]
        height = box[3]
        #print("drawing pred before",classIds[i], confidences[i])
        
        data={}
        data["taskid"]='12345'
        data["time"] = int(time.time())
        data["typeid"]=int(classIds[i])
        data["type"]=classes[classIds[i]]
        boundingbox = {}
        boundingbox["x1"] = int(left)
        boundingbox["y1"] = int(top)
        boundingbox["x2"] = int(left+width)
        boundingbox["y2"] = int(top + height)
        data["box"]=boundingbox
        '''
        print (data,'type of data:',type(data))
        strdata = str(data)
        print (strdata,'type of strdata',type((strdata)))
        evaldata = eval(strdata)
        print (evaldata,'type of evaldata',type((evaldata)))
        '''
        jsondata = json.dumps(data)
        #print (jsondata,type(jsondata))
        publish_message(kafka_producer, 'raw-recipes', 'raw', jsondata.strip())
        
        drawPred(frame, classIds[i], confidences[i], left, top, left + width, top + height)

def publish_message(producer_instance, topic_name, key, value):
	try:
		key_bytes = bytes(key, encoding='utf-8')
		value_bytes = bytes(value, encoding='utf-8')
		producer_instance.send(topic_name, key=key_bytes, value=value_bytes)
		producer_instance.flush()
		print("Message published successfully")

	except Exception as ex:
		print("Exception in publish_message")
		print(str(ex))


def connect_kafka_producer():
	_producer = None
	try:
		_producer = KafkaProducer(bootstrap_servers=['35.187.235.125:9092'], api_version=(0,10))

	except Exception as ex:
		print("Exception while connecting to Kafka")
		print(str(ex))

	finally: 
		return _producer

if __name__ == "__main__":
    kafka_producer = connect_kafka_producer()
    # app.on_shutdown.append(on_shutdown)
    app.router.add_get("/", index)
    app.router.add_get("/client.js", javascript)
    app.router.add_post("/offer", offer)
    app.router.add_post("/i_want_an_offer", i_want_an_offer)
    app.router.add_post("/give_back_answer",  give_back_answer)
    app.router.add_post('/destroy_broadcast', destroy_broadcast)
    web.run_app(app, access_log=None, port=1111)

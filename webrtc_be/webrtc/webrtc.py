import argparse
import asyncio
import json
import logging
import os
import ssl
import uuid

from aiohttp import web
from av import VideoFrame

from aiortc import RTCPeerConnection, RTCSessionDescription, VideoStreamTrack
from aiortc.contrib.media import MediaBlackhole, MediaPlayer, MediaRecorder



class RTCPeer():
	def __init__(self):
		super().__init__()
		self.connection = RTCPeerConnection()	

	def test(self):
		print('test fucntioncll')
		return

	def offer(self, sdp, data_type):
		print("calling the right funtion", data_type)
		print("insed", sdp)

		offer = RTCSessionDescription(sdp=sdp, type=data_type)
		


		@self.connection.on('datachannel')
		def on_datachannel(channel):
			@channel.on("message")
			def on_message(message):
				if isinstance(message, str) and message.startswith("ping"):
					channel.send("pong", message[4:])

		@self.connection.on("iceconnectionstatechange")
		async def on_iceconnectionstatechange():
			if pc.iceConnectionState == "failed":
				await self.connection.close()

		@self.connection.on("track")
		def on_track(track):
			if track.kind == "video":
				local_video = VideoTransformTrack(track, transform=params["video_transform"])
				self.connection.addTrack(local_video)

			@track.on('ended')
			async def on_ended():
				return

		# loop = asyncio.get_event_loop()
		# loop.run_until_complete(asyncio.gather(test1(self.connection, offer)))
		self.connection.setRemoteDescription(offer)
		answer = self.connection.createAnswer()
		print(type(answer))
		

		# answer = asyncio.gather(test2(connection()))		
		# loop.run_until_complete(answer)

		# loop.run_until_complete(asyncio.gather(test3(self.connection, answer)))
		
		res = {}
		# res = "lde"
		res["sdp"] = self.connection.localDescription.type
		res["type"] = self.connection.localDescription.type

		return res


async def test1(connection, offer):
	return await connection.setRemoteDescription(offer)

async def test2(connection):
	return await connection.createAnswer()

async def test3(connection, answer):
	return await connection.setLocalDescription(answer)



async def offer(sdp, request):
	# print("we are in", await request.body)

	# sdp = request.form['sdp']
	print("runnign inside offer")
	# type1 = request.form['type']
	params = await request.json()
	print(params)
	offer = RTCSessionDescription(sdp=sdp, type=request)

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





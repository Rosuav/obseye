import asyncio
import base64
import json
import hashlib
import os
import sys
import websockets
import cv2
import numpy

if not os.path.exists("../GazeTracking"):
	print("Need https://github.com/antoinelame/GazeTracking or equivalent", file=sys.stderr)
	sys.exit(1)

sys.path.append("../GazeTracking")
from gaze_tracking import GazeTracking

config = {
	"server": "localhost",
	"port": 4455,
	"password": "",
	"source": "Webcam",
}
try:
	with open(".config.json") as f:
		config.update(json.load(f))
except FileNotFoundError:
	pass

gaze = GazeTracking()

async def main():
	async with websockets.connect("ws://%s:%d/" % (config["server"], config["port"])) as conn:
		async for data in conn:
			msg = json.loads(data)
			if msg.get("op") == 0: # Hello
				if msg.get("d")["authentication"]:
					challenge = msg.get("d")["authentication"]["challenge"].encode()
					salt = msg.get("d")["authentication"]["salt"].encode()
					auth_key = base64.b64encode(hashlib.sha256(base64.b64encode(hashlib.sha256(config["password"].encode() + salt).digest()) + challenge).digest())
				ident = {"op": 1, "d": {"rpcVersion": 1, "authentication": auth_key.decode(), "eventSubscriptions": 0}}
				await conn.send(json.dumps(ident))
			elif msg.get("op") == 2: # Identified
				# TODO: Do this twice a second (or on some other repeating period)
				request = {"op": 6, "d": {"requestType": "GetSourceScreenshot", "requestId": "shoot", "requestData": {
					"sourceName": config["source"],
					#"imageWidth": 32,
					"imageFormat": "png",
				}}}
				await conn.send(json.dumps(request))
			elif msg.get("op") == 7: # RequestResponse
				if msg["d"]["requestId"] == "shoot":
					uri = msg["d"]["responseData"]["imageData"]
					png = base64.b64decode(uri.removeprefix("data:image/png;base64,"))
					img = cv2.imdecode(numpy.frombuffer(png, dtype=numpy.uint8), cv2.IMREAD_ANYCOLOR)
					gaze.refresh(img)
					# Don't do this normally. Waiting 100ms in an event loop, not a good idea.
					# I have no idea if imshow can be made to play nicely with asyncio but let's not bother.
					# cv2.imshow("preview", img)
					cv2.imshow("preview", gaze.annotated_frame())
					cv2.waitKey(100)

asyncio.run(main())

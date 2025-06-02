import asyncio
import base64
import json
import hashlib
import os
import sys
import traceback
import websockets
import cv2
import numpy
from eyeGestures import EyeGestures_v3

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

gestures = EyeGestures_v3()

def handle_errors(task):
	try:
		exc = task.exception() # Also marks that the exception has been handled
		if exc: traceback.print_exception(type(exc), exc, exc.__traceback__)
	except asyncio.exceptions.CancelledError:
		pass

all_tasks = [] # kinda like threading.all_threads()

def task_done(task):
	all_tasks.remove(task)
	handle_errors(task)

def spawn(awaitable):
	"""Spawn an awaitable as a stand-alone task"""
	task = asyncio.create_task(awaitable)
	all_tasks.append(task)
	task.add_done_callback(task_done)
	return task

halt = False
async def request_frames(conn):
	while "TODO: conn still open":
		request = {"op": 6, "d": {"requestType": "GetSourceScreenshot", "requestId": "shoot", "requestData": {
			"sourceName": config["source"],
			#"imageWidth": 32,
			"imageFormat": "png",
		}}}
		await conn.send(json.dumps(request))
		await asyncio.sleep(1/2)

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
				spawn(request_frames(conn))
			elif msg.get("op") == 7: # RequestResponse
				if msg["d"]["requestId"] == "shoot":
					uri = msg["d"]["responseData"]["imageData"]
					png = base64.b64decode(uri.removeprefix("data:image/png;base64,"))
					img = cv2.imdecode(numpy.frombuffer(png, dtype=numpy.uint8), cv2.IMREAD_ANYCOLOR)
					# Don't do this normally. Waiting 100ms in an event loop, not a good idea.
					# I have no idea if imshow can be made to play nicely with asyncio but let's not bother.
					# key_points, blink, subframe = gestures.getLandmarks(img)
					cv2.imshow("preview", img)
					# cv2.imshow("preview", subframe)
					event, cevent = gestures.step(img, True, 1920, 1080)
					# print(event, cevent)
					if event:
						cursor_x, cursor_y = event.point[0], event.point[1]
						fixation = event.fixation
						print(cursor_x, cursor_y, fixation)
					if cv2.waitKey(10) == ord("q"): break

asyncio.run(main())

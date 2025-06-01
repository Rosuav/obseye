import asyncio
import os
import sys
import websockets
import cv2

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

async def main():
	pass

asyncio.run(main())

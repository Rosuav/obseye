Eye tracking for OBS
====================

Intent:

* Calibrate by looking all around your chat window
* New chat messages get highlighted in green (need browser extension)
* When you look at chat, the highlight flicks in colour to acknowledge, then fades out over 30s
* Fetches webcam directly from OBS and thus requires that you have facecam
  - If someone wants to make a vtuber version of this, the problem is that
    webcams don't share, and so we have to ask the current owner of the cam
    to give us a frame. That may or may not be possible with different software.

Problems:

* It's hard to test things while live-streaming. May be necessary to do some
  initial development off-stream so the webcam is not in use, and default
  "fetch frames from camera" code will work.
* There seems to be a need for calibration. Investigate.
* Fetching 30FPS from OBS may overload things??
* Operating at 30FPS may be too much for one CPU core??? Unlikely on Sikorsky
  but possible on other computers. May need an FPS limit on frame fetching.
* Operating at 2FPS may be too little for the gesture detection algorithm.
  This makes low-load testing tricky.
* The biggest problem, as always, is that I have no clue what I'm doing. Can
  we find any sort of documentation?

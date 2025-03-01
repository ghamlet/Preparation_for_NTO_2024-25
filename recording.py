from USEFULL_SCRIPTS import VideoRecorder


CAMERA_ID = 0
OUTPUT_VIDEO = "output_video.mp4"

recorder = VideoRecorder(camera_index=CAMERA_ID, output_file=OUTPUT_VIDEO)
recorder.start_recording()
import cv2
import numpy as np
import time
import PoseModule as pm
from flask import Flask, render_template, Response, redirect, request, send_from_directory
import json

app = Flask(__name__, template_folder='templates')

cap = cv2.VideoCapture(1)
img = cv2.imread("videos/dips.jpg")
detector = pm.poseDetector()

def generate_frames():
    global curlCount
    curlCount = 0
    count = 0
    direction = 0
    pTime = 0
    while True:

        # Read the camera frame
        success, frame = cap.read()
        if not success:
            break
        frame = detector.findPose(frame, False)
        lmList = detector.findPosition(frame, False)
        if len(lmList) != 0:
            # Right Arm
            angle = detector.findAngle(frame, 12, 14, 16)
            # Left Arm
            # detector.findAngle(frame, 11, 13, 15)
            # bar = np.interp(angle, (220, 310), (650, 100))
            percentage = np.interp(angle, (180, 40), (0, 100))
            percentageAlt = np.interp(angle, (360, 220), (0, 100))
            print(angle, percentage)

            # Check for dumbbell curls
            color = (255, 0, 0)
            if percentage == 100 or percentageAlt == 100:
                color = (0, 255, 0)

                if direction == 0:
                    count += 0.5
                    curlCount += 0.5
                    direction = 1
            if percentage == 0 or percentageAlt == 0:
                color = (0, 255, 0)
                if direction == 1:
                    count += 0.5
                    curlCount += 0.5
                    direction = 0
            print(count)
            # print("direction" + direction)
            # Draw bar
            cv2.rectangle(frame, (1100, 100), (1175, 650), color, 3)
            # cv2.rectangle(frame, (1100, int(bar)), (1175, 650), color, cv2.FILLED)
            # cv2.putText(frame, f'{int(percentage)}%', (1100, 75), cv2.FONT_HERSHEY_PLAIN, 4, color, 4)

            # Draw reps
            # cv2.rectangle(frame, (0, 450), (250, 720), (0, 255, 0), cv2.FILLED)
            # cv2.putText(frame, str(int(count)), (45, 670), cv2.FONT_HERSHEY_PLAIN, 15, (255, 0, 0), 25)

            # cv2.putText(img, str(int(count)), (50, 150), cv2.FONT_HERSHEY_PLAIN, 10, (255, 0, 0), 5)
        cTime = time.time()
        fps = 1 / (cTime - pTime)
        pTime = cTime
        cv2.putText(frame, f'FPS:{int(fps)}', (50, 100), cv2.FONT_HERSHEY_PLAIN, 5, (255, 0, 0), 3)

        cv2.imshow("Let's get into shape!", frame)
        cv2.waitKey(1)

        if not success:
            break
        else:
            ret, buffer = cv2.imencode('.jpg', frame)
            frame = buffer.tobytes()
        yield b'--frame\r\n' b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n'
# def returnCount():
#     count = 0
#     countList = []
#     direction = 0
#     while True:
#
#         # Read the camera frame
#         success, frame = cap.read()
#         if not success:
#             break
#         frame = detector.findPose(frame, False)
#         lmList = detector.findPosition(frame, False)
#         if len(lmList) != 0:
#             # Right Arm
#             angle = detector.findAngle(frame, 12, 14, 16)
#             # Left Arm
#             detector.findAngle(frame, 11, 13, 15)
#             # bar = np.interp(angle, (220, 310), (650, 100))
#             percentage = np.interp(angle, (210, 310), (0, 100))
#             print(angle, percentage)
#
#             # Check for dumbbell curls
#             color = (255, 0, 0)
#             if percentage == 100:
#                 color = (0, 255, 0)
#                 if direction == 0:
#                     count += 0.5
#                     direction = 1
#             if percentage == 0:
#                 color = (0, 255, 0)
#                 if direction == 1:
#                     count += 0.5
#                     direction = 0
#
#             # return json.dumps({'count': count})
#             return count
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/curls')
def curls():
    return render_template('curls.html')
@app.route('/stop')
def stop():
    return render_template('stop.html', curlCount=curlCount)
@app.route('/video')
def video():
    return Response(generate_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')
# @app.route('/get_count')
# def get_count():
#     return Response(returnCount(), mimetype='application/json')



if __name__ == "__main__":
    app.run(debug=True)

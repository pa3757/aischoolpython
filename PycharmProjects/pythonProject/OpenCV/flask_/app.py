# from flask import *
#
# app = Flask(__name__)
#
# @app.route('/')
# def hello():
#     return 'Hello Flask!'
#
# if __name__ == '__main__':
#     app.run()

from flask import Flask, render_template, Response
import cv2

app = Flask(__name__)
cam = cv2.VideoCapture(0)

def gen_frames():
    while True:
        _, frame = cam.read()


        ret, buffer = cv2.imencode('.jpg', frame)
        frame = buffer.tobytes()
        yield (b'--frame\r\n'b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n')

@app.route('/video_feed')

def video_feed():
    return Response(gen_frames(), mimetype='multipart/x-mixed-replace; boundary=frame')

@app.route('/')
def index():
    return render_template('profile.html')

if __name__ == '__main__':
    app.run(debug=True)
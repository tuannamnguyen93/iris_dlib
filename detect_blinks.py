# -*- coding:utf8 -*-
# !/usr/bin/env python
from scipy.spatial import distance as dist
from imutils.video import FileVideoStream
# from imutils.video import VideoStream
from imutils import face_utils
import numpy as np
import imutils
import time
import dlib
import cv2


def eye_aspect_ratio(eye):
    '''
    references: http://vision.fe.uni-lj.si/cvww2016/proceedings/papers/05.pdf
    :param eye:
    :return: eye_aspect_ratio
    '''
    A = dist.euclidean(eye[1], eye[5])
    B = dist.euclidean(eye[2], eye[4])
    C = dist.euclidean(eye[0], eye[3])
    ear = (A + B) / (2.0 * C)
    return ear

def rotate_bound(image, angle):
    '''
    :param image:
    :param angle:
    :return: #Xoay clip nếu clip dọc
    '''
    (h, w) = image.shape[:2]
    (cX, cY) = (w // 2, h // 2)

    M = cv2.getRotationMatrix2D((cX, cY), -angle, 1.0)
    cos = np.abs(M[0, 0])
    sin = np.abs(M[0, 1])

    nW = int((h * sin) + (w * cos))
    nH = int((h * cos) + (w * sin))

    M[0, 2] += (nW / 2) - cX
    M[1, 2] += (nH / 2) - cY

    return cv2.warpAffine(image, M, (nW, nH))


def eye_blink_counter(EYE_AR_THRESH = 0.18,EYE_AR_CONSEC_FRAMES = 3):
    '''

    :param EYE_AR_THRESH:
    :param EYE_AR_CONSEC_FRAMES:
    :return: Số lần chớp mắt
    '''
    COUNTER = 0
    TOTAL = 0

    video_path = "/Users/phamtuan/PycharmProjects/IRIS/tuan.mp4"
    print("[INFO] loading facial landmark predictor...")
    detector = dlib.get_frontal_face_detector()

    predictor = dlib.shape_predictor("models/shape_predictor_68_face_landmarks.dat")

    (lStart, lEnd) = face_utils.FACIAL_LANDMARKS_IDXS["left_eye"]
    (rStart, rEnd) = face_utils.FACIAL_LANDMARKS_IDXS["right_eye"]

    vs = FileVideoStream(video_path).start()
    fileStream = True
    # vs = VideoStream(src=0).start()
    # vs = VideoStream(usePiCamera=True).start()
    # fileStream = False
    time.sleep(1.0)

    while True:
        if fileStream and not vs.more():
            break
        frame = vs.read()
        frame = rotate_bound(frame,90)
        frame = imutils.resize(frame, width=500)
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        rects = detector(gray, 0)
        if len(rects)==0:
            my_rect = rects
        if len(rects) != 0:
            for rect in rects:
                shape = predictor(gray, rect)
        else:
                shape = predictor(gray,my_rect[0])
        # for rect in rects:
        #     shape = predictor(gray, rect)

        shape = face_utils.shape_to_np(shape)

        leftEye = shape[lStart:lEnd]
        rightEye = shape[rStart:rEnd]
        leftEAR = eye_aspect_ratio(leftEye)
        rightEAR = eye_aspect_ratio(rightEye)

        ear = (leftEAR + rightEAR) / 2.0

        # leftEyeHull = cv2.convexHull(leftEye)
        # rightEyeHull = cv2.convexHull(rightEye)
        # cv2.drawContours(frame, [leftEyeHull], -1, (0, 255, 0), 1)
        # cv2.drawContours(frame, [rightEyeHull], -1, (0, 255, 0), 1)

        if ear < EYE_AR_THRESH:
            COUNTER += 1

        else:
            if COUNTER >= EYE_AR_CONSEC_FRAMES:
                TOTAL += 1

            COUNTER = 0

        # cv2.putText(frame, "Blinks: {}".format(TOTAL), (10, 30),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        # cv2.putText(frame, "ratio: {:.2f}".format(ear), (300, 30),
        #             cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 0, 255), 2)
        #
        # cv2.imshow("Frame", frame)
        # key = cv2.waitKey(1) & 0xFF

        # if key == ord("q"):
        #     break
    # cv2.destroyAllWindows()
    # vs.stop()
    return TOTAL

def save_csv():
    '''
    :return: File CSV
    '''
    import csv
    frames = [1,2,3,4,5]
    blink_counter = eye_blink_counter()
    iris_size = 100
    writer = csv.writer(open("CSVs/IRIS_data.csv", 'w'))
    row = ['Frame','left_eye_pos','left_pupil_size','right_eye_pos','right_pupil_size']
    writer.writerow(row)
    for index in range(len(frames)):
        left_eye_pos = ('NA','NA')
        left_pupil_size = 'NA'
        right_eye_pos = ('NA','NA')
        right_pupil_size = 'NA'
        row = [index,left_eye_pos,left_pupil_size,right_eye_pos,right_pupil_size]
        writer.writerow(row)
    writer.writerow([blink_counter])
    writer.writerow([iris_size])
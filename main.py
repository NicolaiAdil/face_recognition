import face_recognition
import cv2
import numpy as np
import os
import time
from threading import Thread
from os import listdir
from utils import people_list, FreshestFrame
from Confidential import USERNAME, PASSWORD, IP_ADRESS
from bot import send_image

def look_for_unknown_faces(face_names, frame):
    counter = 0
    for element in face_names:
        if element == "Unknown":
            counter += 1
    if counter > 0:
        os.remove("unknown.jpg")
        cv2.imwrite(f"unknown.jpg", frame)
        send_image("unknown.jpg", counter)
        time.sleep(15)

def main():
    camera_stream = f"rtsp://{USERNAME}:{PASSWORD}@{IP_ADRESS}:554/cam/realmonitor?channel=1&subtype=0"

    # video_capture = cv2.VideoCapture(0)
    video_capture = cv2.VideoCapture(camera_stream)
    video_capture.set(cv2.CAP_PROP_FPS, 30) #Caps FPS to 30

    video_capture = FreshestFrame(video_capture) #Uses only the freshest frame

    known_face_encodings = list()
    known_face_names = list()

    ### Main ###

    #Adding relevant people
    for name in people_list:
        for image in os.listdir(f"pictures/{name}"):
            name_image = face_recognition.load_image_file(f"pictures/{name}/{image}")
            known_face_encodings.append(face_recognition.face_encodings(name_image)[0])
            known_face_names.append(name)

    #Continously checking for faces
    face_locations = []
    face_encodings = []
    face_names = []
    process_this_frame = True

    while True:
        # Grab a single frame of video
        ret, frame = video_capture.read()

        # Only process every other frame of video to save time
        if process_this_frame:

            # Resize frame of video to 1/4 size for faster face recognition processing
            small_frame = cv2.resize(frame, (0, 0), fx=0.25, fy=0.25)

            # Convert the image from BGR color (which OpenCV uses) to RGB color (which face_recognition uses)
            rgb_small_frame = small_frame[:, :, ::-1]

            # Find all the faces and face encodings in the current frame of video
            face_locations = face_recognition.face_locations(rgb_small_frame)
            face_encodings = face_recognition.face_encodings(rgb_small_frame, face_locations)

            face_names = []
            for face_encoding in face_encodings:
                # See if the face is a match for the known face(s)
                matches = face_recognition.compare_faces(known_face_encodings, face_encoding)
                name = "Unknown"

                # If a match was found in known_face_encodings, just use the first one.
                
                if True in matches:
                    first_match_index = matches.index(True)
                    name = known_face_names[first_match_index]

                face_names.append(name)

                #Display accuracy
                # face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                # for i, face_distance in enumerate(face_distances):
                #     accuracy = face_distance
        process_this_frame = not process_this_frame


        # Display the results
        for (top, right, bottom, left), name in zip(face_locations, face_names):
            # Scale back up face locations since the frame we detected in was scaled to 1/4 size
            top *= 4
            right *= 4
            bottom *= 4
            left *= 4

            # Draw a box around the face
            cv2.rectangle(frame, (left, top), (right, bottom), (0, 0, 255), 2)

            # Draw a label with a name below the face
            cv2.rectangle(frame, (left, bottom - 35), (right, bottom), (0, 0, 255), cv2.FILLED)
            font = cv2.FONT_HERSHEY_DUPLEX
            cv2.putText(frame, name, (left + 6, bottom - 6), font, 1.0, (255, 255, 255), 1)
        
        # Display the resulting image
            
        cv2.namedWindow('Video', cv2.WINDOW_NORMAL)
        cv2.imshow('Video', frame)

        # Checks if there are unknown faces in the frame
        look_for_unknown_faces(face_names, frame)
        face_names = []

        # Hit 'q' on the keyboard to quit!
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break

    video_capture.release()
    cv2.destroyAllWindows()

if __name__ == "__main__":
    main()

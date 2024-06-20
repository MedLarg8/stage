import face_recognition
import cv2
import numpy as np
import os
import threading
from pygame import time


delay = False

def waitfunction():
    global delay
    time.delay(5000)
    delay = True


t1 = threading.Thread(target= waitfunction)

UPLOAD_FOLDER = "usersImages"

video_capture = cv2.VideoCapture(0)

dirs = os.listdir(UPLOAD_FOLDER)

known_faces_images = []

for dir in dirs:
    image = os.listdir(os.path.join(UPLOAD_FOLDER,dir))[0]
    known_faces_images.append(image)

known_face_encodings = []

for image in known_faces_images:
    encoding = face_recognition.face_encodings(image)[0]
    known_face_encodings.append(encoding)

known_face_names = dirs

face_locations = []
face_encodings = []
face_names = []
process_this_frame = True


t1.start()




# Release handle to the webcam
video_capture.release()
cv2.destroyAllWindows()

def get_face_names():
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

                # # If a match was found in known_face_encodings, just use the first one.
                # if True in matches:
                #     first_match_index = matches.index(True)
                #     name = known_face_names[first_match_index]

                # Or instead, use the known face with the smallest distance to the new face
                face_distances = face_recognition.face_distance(known_face_encodings, face_encoding)
                best_match_index = np.argmin(face_distances)
                if matches[best_match_index]:
                    name = known_face_names[best_match_index]
                    
                face_names.append(name)

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
        cv2.imshow('Video', frame)

        # Hit 'q' on the keyboard to quit!
        if (cv2.waitKey(1) & 0xFF == ord('q') or delay):
            break

        face_names = list(set(face_names))

        return face_names

        
def check_name(names_list, name):
    if name in names_list:
        return True
    else:
        return False
    
def start_recognition():
    t1.start()
    names_list = get_face_names()
    return names_list
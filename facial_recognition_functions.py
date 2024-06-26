import threading
import cv2
from deepface import DeepFace

cap = cv2.VideoCapture(0, cv2.CAP_DSHOW)

cap.set(cv2.CAP_PROP_FRAME_WIDTH, 640)
cap.set(cv2.CAP_PROP_FRAME_HEIGHT, 480)

counter = 0
face_match = False
match_duration = 0  # Duration counter for face match
match_threshold = 20  # Number of frames to consider as 1 second (assuming 20 frames per second)

reference_img = cv2.imread("test.jpg")

def check_face(frame, ref):
    global face_match
    try:
        if DeepFace.verify(frame, ref.copy())['verified']:
            face_match = True
        else:
            face_match = False
    except ValueError:
        face_match = False

def run_application():
    global match_duration

    while True:
        ret, frame = cap.read()

        if ret:
            if counter % 20 == 0:
                try:
                    threading.Thread(target=check_face, args=(frame.copy(), reference_img,)).start()
                except ValueError:
                    pass

            if face_match:
                match_duration += 1
                if match_duration >= match_threshold:
                    break  # Exit the loop and close the application

                cv2.putText(frame, "MATCH for {} sec".format(match_duration / 20), (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 255, 0), 2)
            else:
                match_duration = 0
                cv2.putText(frame, "no MATCH", (20, 450), cv2.FONT_HERSHEY_SIMPLEX, 1, (0, 0, 255), 2)

            cv2.imshow("video", frame)

        key = cv2.waitKey(1)
        if key == ord('q'):
            break

        counter += 1

    cv2.destroyAllWindows()

if __name__ == "__main__":
    run_application()

import face_recognition
from numpy import linalg, add
obama_picture = face_recognition.load_image_file("téléchargé.png")
#face_locations = face_recognition.face_locations(obama_picture)

obama_encoding = face_recognition.face_encodings(obama_picture)[0]

#print(obama_encoding)

unknown_picture = face_recognition.load_image_file("bJordan.png")
unknown_picture_encoding = face_recognition.face_encodings(unknown_picture)[0]


face_distance = face_recognition.face_distance([obama_encoding],unknown_picture_encoding)

print("face distance : ",face_distance)

results = face_recognition.compare_faces([obama_encoding], unknown_picture_encoding)[0]

print(results)




def face_recognition_function(saved_image, input_image, show_distance = False):
    saved_image_encoding = face_recognition.face_encodings(saved_image)
    input_image_encoding = face_recognition.face_encodings(input_image)

    results = face_recognition.compare_faces([saved_image_encoding], input_image_encoding)[0]

    if show_distance:
        face_distance = face_recognition.face_distance([saved_image_encoding],input_image_encoding)
        return[results,face_distance]
    else:
        return[results]
    




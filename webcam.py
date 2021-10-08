# Classe da Webcam
import cv2
from EmotionRecognition import EmotionRecognition
import numpy as np

# Este ficheiro permite detectar faces de pessoas
facec = cv2.CascadeClassifier('haarcascade_frontalface_default.xml')
# Variável da classe Emotion Recognition
model = EmotionRecognition("model.json", "model.h5")
font = cv2.FONT_HERSHEY_SIMPLEX


# Váriavel que irá ser utilizada para retornar as previsões das emoções
pred = ""


class Webcam(object):

    def __init__(self):
        self.video = cv2.VideoCapture(0)

    def __del__(self):
        self.video.release()

    # retornar frames da webcam juntamente com as caixas delimitadoras e as previsões

    def get_frame(self):

        global pred
        _, fr = self.video.read()
        gray_fr = cv2.cvtColor(fr, cv2.COLOR_BGR2GRAY)
        faces = facec.detectMultiScale(gray_fr, 1.3, 5)
        for (x, y, w, h) in faces:
            fc = gray_fr[y:y+h, x:x+w]

            img = cv2.resize(fc, (48, 48))
            pred = model.predict_emotion(img[np.newaxis, :, :, np.newaxis])

            cv2.putText(fr, pred, (x, y), font, 1, (255, 255, 0), 2)
            cv2.rectangle(fr, (x, y), (x+w, y+h), (255, 0, 0), 2)

        _, jpeg = cv2.imencode('.jpg', fr)
 # Retorna a previsão e a imagem obtida
        return pred, jpeg.tobytes()

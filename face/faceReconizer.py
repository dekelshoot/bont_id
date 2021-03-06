from keras.models import Sequential
from keras.layers import Conv2D, ZeroPadding2D, Activation, Input, concatenate
from keras.models import Model
from tensorflow.keras.layers import BatchNormalization
from keras.layers.pooling import MaxPooling2D, AveragePooling2D
from keras.layers.merge import Concatenate
from keras.layers.core import Lambda, Flatten, Dense
from tensorflow.keras.layers import Layer
from keras import backend as K
import glob
import cv2
import os
import numpy as np
from numpy import genfromtxt
import pandas as pd
import tensorflow as tf
from face.utils import LRN2D, load_weights
import face.utils as utils
# Import essential libraries
import requests
import imutils
  

np.set_printoptions(2**31-1)
#cette référence devrait probablement simplement utiliser une valeur raisonnable pour le seuil

def createModel():
    myInput = Input(shape=(96, 96, 3)) # Une image de taille 96*96*3

    x = ZeroPadding2D(padding=(3, 3), input_shape=(96, 96, 3))(myInput)
    # Création d'un tenseur

    x = Conv2D(64, (7, 7), strides=(2, 2), name='conv1')(x)
    # On fait la convolution avec 64 caractéristiques(filtres) (On utilise toujours les puissances de 2 de taille) 7*7 et le nombre de pixels de déplacement 
    # Noter qu'ici on se déplace en taille d'un morceau dont la valeur est 2*2 

    x = BatchNormalization(axis=3, epsilon=0.00001, name='bn1')(x) 
    # On normalise les vecteurs d'activation des  couches cachées, epsilon est utilisé pour la stabilité numérique 

    x = Activation('relu')(x)
    # Après la convolution, on applique la fonction ReLU qui va remplacer les valeurs négatives pas 0 et concerver 
    #les valeurs positives

    x = ZeroPadding2D(padding=(1, 1))(x)
    # Création d'un autre tenseur de hauteur 1pixel et de largeur 1pixel avec le x obtenue précédement 

    x = MaxPooling2D(pool_size=3, strides=2)(x) 
    # On fait le max-pooling  avec la taille de la caractéristique qui est 3*3 et le nombre de pixels de déplacement qui est 2 sur x

    x = Lambda(LRN2D, name='lrn_1')(x)
    # Normalisation de telle sorte que ce soit près à entrer dans le réseau de neurones


    x = Conv2D(64, (1, 1), name='conv2')(x)
    # On applique au meme x une convolution avec 64 caractériques de taille 1*1 donc pixels par pixels c'est donc trivial que le 
    # déplacement se fera avec 1 pixel
    x = BatchNormalization(axis=3, epsilon=0.00001, name='bn2')(x)
    # La normalisation sur le 3ème axe 

    x = Activation('relu')(x)
    # On applique directement la fonction ReLU au resultat de la convolution 

    x = ZeroPadding2D(padding=(1, 1))(x)
    # Création d'un nouveay tenseur avec le x obtenu

    x = Conv2D(192, (3, 3), name='conv3')(x)
    # Application de la convolution
    x = BatchNormalization(axis=3, epsilon=0.00001, name='bn3')(x)
    # Normalisation
    x = Activation('relu')(x)
    # Fonction d'activation ReLU

    x = Lambda(LRN2D, name='lrn_2')(x)
    # Normalisation de telle sorte que ce soit près à entrer dans le réseau de neurones

    x = ZeroPadding2D(padding=(1, 1))(x)
    x = MaxPooling2D(pool_size=3, strides=2)(x)
    # Une dernière 

    # Inception3a
    # On crée le réseau de neurone après les transformations qu'on a fait sur le tenseur plus haut
    inception_3a_3x3 = Conv2D(96, (1, 1), name='inception_3a_3x3_conv1')(x)
    inception_3a_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_3x3_bn1')(inception_3a_3x3)
    inception_3a_3x3 = Activation('relu')(inception_3a_3x3)
    inception_3a_3x3 = ZeroPadding2D(padding=(1, 1))(inception_3a_3x3)
    inception_3a_3x3 = Conv2D(128, (3, 3), name='inception_3a_3x3_conv2')(inception_3a_3x3)
    inception_3a_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_3x3_bn2')(inception_3a_3x3)
    inception_3a_3x3 = Activation('relu')(inception_3a_3x3)

    inception_3a_5x5 = Conv2D(16, (1, 1), name='inception_3a_5x5_conv1')(x)
    inception_3a_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_5x5_bn1')(inception_3a_5x5)
    inception_3a_5x5 = Activation('relu')(inception_3a_5x5)
    inception_3a_5x5 = ZeroPadding2D(padding=(2, 2))(inception_3a_5x5)
    inception_3a_5x5 = Conv2D(32, (5, 5), name='inception_3a_5x5_conv2')(inception_3a_5x5)
    inception_3a_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_5x5_bn2')(inception_3a_5x5)
    inception_3a_5x5 = Activation('relu')(inception_3a_5x5)

    inception_3a_pool = MaxPooling2D(pool_size=3, strides=2)(x)
    inception_3a_pool = Conv2D(32, (1, 1), name='inception_3a_pool_conv')(inception_3a_pool)
    inception_3a_pool = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_pool_bn')(inception_3a_pool)
    inception_3a_pool = Activation('relu')(inception_3a_pool)
    inception_3a_pool = ZeroPadding2D(padding=((3, 4), (3, 4)))(inception_3a_pool)

    inception_3a_1x1 = Conv2D(64, (1, 1), name='inception_3a_1x1_conv')(x)
    inception_3a_1x1 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3a_1x1_bn')(inception_3a_1x1)
    inception_3a_1x1 = Activation('relu')(inception_3a_1x1)

    inception_3a = concatenate([inception_3a_3x3, inception_3a_5x5, inception_3a_pool, inception_3a_1x1], axis=3)

    # Inception3b
    inception_3b_3x3 = Conv2D(96, (1, 1), name='inception_3b_3x3_conv1')(inception_3a)
    inception_3b_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_3x3_bn1')(inception_3b_3x3)
    inception_3b_3x3 = Activation('relu')(inception_3b_3x3)
    inception_3b_3x3 = ZeroPadding2D(padding=(1, 1))(inception_3b_3x3)
    inception_3b_3x3 = Conv2D(128, (3, 3), name='inception_3b_3x3_conv2')(inception_3b_3x3)
    inception_3b_3x3 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_3x3_bn2')(inception_3b_3x3)
    inception_3b_3x3 = Activation('relu')(inception_3b_3x3)

    inception_3b_5x5 = Conv2D(32, (1, 1), name='inception_3b_5x5_conv1')(inception_3a)
    inception_3b_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_5x5_bn1')(inception_3b_5x5)
    inception_3b_5x5 = Activation('relu')(inception_3b_5x5)
    inception_3b_5x5 = ZeroPadding2D(padding=(2, 2))(inception_3b_5x5)
    inception_3b_5x5 = Conv2D(64, (5, 5), name='inception_3b_5x5_conv2')(inception_3b_5x5)
    inception_3b_5x5 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_5x5_bn2')(inception_3b_5x5)
    inception_3b_5x5 = Activation('relu')(inception_3b_5x5)

    inception_3b_pool = Lambda(lambda x: x**2, name='power2_3b')(inception_3a)
    inception_3b_pool = AveragePooling2D(pool_size=(3, 3), strides=(3, 3))(inception_3b_pool)
    inception_3b_pool = Lambda(lambda x: x*9, name='mult9_3b')(inception_3b_pool)
    inception_3b_pool = Lambda(lambda x: K.sqrt(x), name='sqrt_3b')(inception_3b_pool)
    inception_3b_pool = Conv2D(64, (1, 1), name='inception_3b_pool_conv')(inception_3b_pool)
    inception_3b_pool = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_pool_bn')(inception_3b_pool)
    inception_3b_pool = Activation('relu')(inception_3b_pool)
    inception_3b_pool = ZeroPadding2D(padding=(4, 4))(inception_3b_pool)

    inception_3b_1x1 = Conv2D(64, (1, 1), name='inception_3b_1x1_conv')(inception_3a)
    inception_3b_1x1 = BatchNormalization(axis=3, epsilon=0.00001, name='inception_3b_1x1_bn')(inception_3b_1x1)
    inception_3b_1x1 = Activation('relu')(inception_3b_1x1)

    inception_3b = concatenate([inception_3b_3x3, inception_3b_5x5, inception_3b_pool, inception_3b_1x1], axis=3)

    # Inception3c
    inception_3c_3x3 = utils.conv2d_bn(inception_3b,
                                    layer='inception_3c_3x3',
                                    cv1_out=128,
                                    cv1_filter=(1, 1),
                                    cv2_out=256,
                                    cv2_filter=(3, 3),
                                    cv2_strides=(2, 2),
                                    padding=(1, 1))

    inception_3c_5x5 = utils.conv2d_bn(inception_3b,
                                    layer='inception_3c_5x5',
                                    cv1_out=32,
                                    cv1_filter=(1, 1),
                                    cv2_out=64,
                                    cv2_filter=(5, 5),
                                    cv2_strides=(2, 2),
                                    padding=(2, 2))

    inception_3c_pool = MaxPooling2D(pool_size=3, strides=2)(inception_3b)
    inception_3c_pool = ZeroPadding2D(padding=((0, 1), (0, 1)))(inception_3c_pool)

    inception_3c = concatenate([inception_3c_3x3, inception_3c_5x5, inception_3c_pool], axis=3)

    #inception 4a
    inception_4a_3x3 = utils.conv2d_bn(inception_3c,
                                    layer='inception_4a_3x3',
                                    cv1_out=96,
                                    cv1_filter=(1, 1),
                                    cv2_out=192,
                                    cv2_filter=(3, 3),
                                    cv2_strides=(1, 1),
                                    padding=(1, 1))
    inception_4a_5x5 = utils.conv2d_bn(inception_3c,
                                    layer='inception_4a_5x5',
                                    cv1_out=32,
                                    cv1_filter=(1, 1),
                                    cv2_out=64,
                                    cv2_filter=(5, 5),
                                    cv2_strides=(1, 1),
                                    padding=(2, 2))

    inception_4a_pool = Lambda(lambda x: x**2, name='power2_4a')(inception_3c)
    inception_4a_pool = AveragePooling2D(pool_size=(3, 3), strides=(3, 3))(inception_4a_pool)
    inception_4a_pool = Lambda(lambda x: x*9, name='mult9_4a')(inception_4a_pool)
    inception_4a_pool = Lambda(lambda x: K.sqrt(x), name='sqrt_4a')(inception_4a_pool)
    inception_4a_pool = utils.conv2d_bn(inception_4a_pool,
                                    layer='inception_4a_pool',
                                    cv1_out=128,
                                    cv1_filter=(1, 1),
                                    padding=(2, 2))
    inception_4a_1x1 = utils.conv2d_bn(inception_3c,
                                    layer='inception_4a_1x1',
                                    cv1_out=256,
                                    cv1_filter=(1, 1))
    inception_4a = concatenate([inception_4a_3x3, inception_4a_5x5, inception_4a_pool, inception_4a_1x1], axis=3)

    #inception4e
    inception_4e_3x3 = utils.conv2d_bn(inception_4a,
                                    layer='inception_4e_3x3',
                                    cv1_out=160,
                                    cv1_filter=(1, 1),
                                    cv2_out=256,
                                    cv2_filter=(3, 3),
                                    cv2_strides=(2, 2),
                                    padding=(1, 1))
    inception_4e_5x5 = utils.conv2d_bn(inception_4a,
                                    layer='inception_4e_5x5',
                                    cv1_out=64,
                                    cv1_filter=(1, 1),
                                    cv2_out=128,
                                    cv2_filter=(5, 5),
                                    cv2_strides=(2, 2),
                                    padding=(2, 2))
    inception_4e_pool = MaxPooling2D(pool_size=3, strides=2)(inception_4a)
    inception_4e_pool = ZeroPadding2D(padding=((0, 1), (0, 1)))(inception_4e_pool)

    inception_4e = concatenate([inception_4e_3x3, inception_4e_5x5, inception_4e_pool], axis=3)

    #inception5a
    inception_5a_3x3 = utils.conv2d_bn(inception_4e,
                                    layer='inception_5a_3x3',
                                    cv1_out=96,
                                    cv1_filter=(1, 1),
                                    cv2_out=384,
                                    cv2_filter=(3, 3),
                                    cv2_strides=(1, 1),
                                    padding=(1, 1))

    inception_5a_pool = Lambda(lambda x: x**2, name='power2_5a')(inception_4e)
    inception_5a_pool = AveragePooling2D(pool_size=(3, 3), strides=(3, 3))(inception_5a_pool)
    inception_5a_pool = Lambda(lambda x: x*9, name='mult9_5a')(inception_5a_pool)
    inception_5a_pool = Lambda(lambda x: K.sqrt(x), name='sqrt_5a')(inception_5a_pool)
    inception_5a_pool = utils.conv2d_bn(inception_5a_pool,
                                    layer='inception_5a_pool',
                                    cv1_out=96,
                                    cv1_filter=(1, 1),
                                    padding=(1, 1))
    inception_5a_1x1 = utils.conv2d_bn(inception_4e,
                                    layer='inception_5a_1x1',
                                    cv1_out=256,
                                    cv1_filter=(1, 1))

    inception_5a = concatenate([inception_5a_3x3, inception_5a_pool, inception_5a_1x1], axis=3)

    #inception_5b
    inception_5b_3x3 = utils.conv2d_bn(inception_5a,
                                    layer='inception_5b_3x3',
                                    cv1_out=96,
                                    cv1_filter=(1, 1),
                                    cv2_out=384,
                                    cv2_filter=(3, 3),
                                    cv2_strides=(1, 1),
                                    padding=(1, 1))
    inception_5b_pool = MaxPooling2D(pool_size=3, strides=2)(inception_5a)
    inception_5b_pool = utils.conv2d_bn(inception_5b_pool,
                                    layer='inception_5b_pool',
                                    cv1_out=96,
                                    cv1_filter=(1, 1))
    inception_5b_pool = ZeroPadding2D(padding=(1, 1))(inception_5b_pool)

    inception_5b_1x1 = utils.conv2d_bn(inception_5a,
                                    layer='inception_5b_1x1',
                                    cv1_out=256,
                                    cv1_filter=(1, 1))
    inception_5b = concatenate([inception_5b_3x3, inception_5b_pool, inception_5b_1x1], axis=3)

    av_pool = AveragePooling2D(pool_size=(3, 3), strides=(1, 1))(inception_5b)
    reshape_layer = Flatten()(av_pool)
    dense_layer = Dense(128, name='dense_layer')(reshape_layer)
    norm_layer = Lambda(lambda  x: K.l2_normalize(x, axis=1), name='norm_layer')(dense_layer)


    # Final Model
    model = Model(inputs=[myInput], outputs=norm_layer)
    print('model cree')
    return model



def loadWeights(model):
    # Load weights from csv files (which was exported from Openface torch model)
    weights = utils.weights
    weights_dict = utils.load_weights()

    # Set layer weights of the model
    for name in weights:
        if model.get_layer(name) != None:
            model.get_layer(name).set_weights(weights_dict[name])
        elif model.get_layer(name) != None: ## Possibilité d'erreurs
            model.get_layer(name).set_weights(weights_dict[name])
    print('poids charges')

def image_to_embedding(image, model):
    #image = cv2.resize(image, (96, 96), interpolation=cv2.INTER_AREA) 
    image = cv2.resize(image, (96, 96)) 
    img = image[...,::-1]
    img = np.around(np.transpose(img, (0,1,2))/255.0, decimals=12)
    x_train = np.array([img])
    embedding = model.predict_on_batch(x_train)
    return embedding

def recognize_face(face_image, input_embeddings, model):

    embedding = image_to_embedding(face_image, model)
    
    minimum_distance = 200
    name = None
    
    # Loop over  names and encodings.
    for (input_name, input_embedding) in input_embeddings.items():
        
       
        euclidean_distance = np.linalg.norm(embedding-input_embedding)
        

        print('Euclidean distance from %s is %s' %(input_name, euclidean_distance))

        
        if euclidean_distance < minimum_distance:
            minimum_distance = euclidean_distance
            name = input_name
    
    if minimum_distance < 0.3:
        return str(name)
    else:
        return None


def create_input_image_embeddings(model):
    input_embeddings = {}

    for file in glob.glob("media/images/*"):
        person_name = os.path.splitext(os.path.basename(file))[0]
        image_file = cv2.imread(file, 1)
        input_embeddings[person_name] = image_to_embedding(image_file, model)

    return input_embeddings

def recognize_faces_in_cam(input_embeddings,model):
    

    # cv2.namedWindow("Face Recognizer")
    vc = cv2.VideoCapture(0)
   

    font = cv2.FONT_HERSHEY_SIMPLEX # Le type de police pour écrire sur une image 
    
    face_cascade = cv2.CascadeClassifier('face/static/assets/model/haarcascade_frontalface_default.xml')
    # Chargement d'un fichier de classifieur .xml
    
    
    while vc.isOpened():
        _, frame = vc.read()
        img = frame
        height, width, channels = frame.shape

        
        
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)

        # Loop through all the faces detected 
        identities = []
        for (x, y, w, h) in faces:
            x1 = x
            y1 = y
            x2 = x+w
            y2 = y+h

           
            loading = "loading..."
            face_image = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]    
            identity = recognize_face(face_image, input_embeddings, model)
            img = cv2.rectangle(frame,(x1, y1),(x2, y2),(255,255,255),2)
            cv2.putText(img, str(loading), (x1+5,y1-5), font, 1, (255,255,255), 2)

            if identity is not None:
                # img = cv2.rectangle(frame,(x1, y1),(x2, y2),(255,255,255),2)
                # cv2.putText(img, str(identity), (x1+5,y1-5), font, 1, (255,255,255), 2)
                vc.release()
                cv2.destroyAllWindows()
                return identity
        
        key = cv2.waitKey(100)
        cv2.imshow("reconnaissance faciale", img)

        if key == 27: # exit on ESC
            break
    vc.release()
    cv2.destroyAllWindows()

def streamVideo(input_embeddings,model,src):
    cv2.namedWindow("reconnaissance faciale")
    vc = cv2.VideoCapture(src)
    face_cascade=cv2.CascadeClassifier('face/static/assets/model/haarcascade_frontalface_default.xml')
    font = cv2.FONT_HERSHEY_SIMPLEX # Le type de police pour écrire sur une image 
    while True:
        ret , frame = vc.read()
        if ret == False:
            vc.release()
            break
        img = frame
        height, width, channels = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        # Loop through all the faces detected 
        identities = []
        for (x, y, w, h) in faces:
            x1 = x
            y1 = y
            x2 = x+w
            y2 = y+h
            loading = "loading..."
            face_image = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]    
            identity = recognize_face(face_image, input_embeddings, model)
            img = cv2.rectangle(frame,(x1, y1),(x2, y2),(255,255,255),2)
            cv2.putText(img, str(loading), (x1+5,y1-5), font, 1, (255,255,255), 2)
            if identity is not None:
                # img = cv2.rectangle(frame,(x1, y1),(x2, y2),(255,255,255),2)
                # cv2.putText(img, str(identity), (x1+5,y1-5), font, 1, (255,255,255), 2)
                vc.release()
                cv2.destroyAllWindows()
                return identity
        # frame = cv2.resize(frame, (600, 300))     
        cv2.imshow('reconnaissance faciale',cv2.pyrDown(frame))
        key = cv2.waitKey(10)
        if key == 27: # exit on ESC
            break
    vc.release()
    cv2.destroyAllWindows()


def streamImage(input_embeddings,model,src):
    cv2.namedWindow("reconnaissance faciale")
    frame = cv2.imread(src)
    face_cascade=cv2.CascadeClassifier('face/static/assets/model/haarcascade_frontalface_default.xml')
    font = cv2.FONT_HERSHEY_SIMPLEX # Le type de police pour écrire sur une image 
    while True:
        img = frame
        height, width, channels = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        # Loop through all the faces detected 
        identities = []
        for (x, y, w, h) in faces:
            x1 = x
            y1 = y
            x2 = x+w
            y2 = y+h
            loading = "loading..."
            face_image = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]    
            identity = recognize_face(face_image, input_embeddings, model)
            img = cv2.rectangle(frame,(x1, y1),(x2, y2),(255,255,255),2)
            cv2.putText(img, str(loading), (x1+5,y1-5), font, 1, (255,255,255), 2)
            if identity is not None:
                # img = cv2.rectangle(frame,(x1, y1),(x2, y2),(255,255,255),2)
                # cv2.putText(img, str(identity), (x1+5,y1-5), font, 1, (255,255,255), 2)

                cv2.destroyAllWindows()
                return identity
        # frame = cv2.resize(frame, (600, 300))     
        cv2.imshow('reconnaissance faciale',cv2.pyrDown(frame))
        key = cv2.waitKey(10)
        if key == 27: # exit on ESC
            break

    cv2.destroyAllWindows()


def streamVideoPhone(input_embeddings,model):
    cv2.namedWindow("reconnaissance faciale")
    face_cascade=cv2.CascadeClassifier('face/static/assets/model/haarcascade_frontalface_default.xml')
    font = cv2.FONT_HERSHEY_SIMPLEX # Le type de police pour écrire sur une image 
    # Replace the below URL with your own. Make sure to add "/shot.jpg" at last.
    url = "http://192.168.195.98:8080/shot.jpg"
    while True:
        img_resp = requests.get(url)
        img_arr = np.array(bytearray(img_resp.content), dtype=np.uint8)
        img = cv2.imdecode(img_arr, -1)
        frame = img
        height, width, channels = frame.shape
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = face_cascade.detectMultiScale(gray, 1.3, 5)
        # Loop through all the faces detected 
        identities = []
        for (x, y, w, h) in faces:
            x1 = x
            y1 = y
            x2 = x+w
            y2 = y+h
            loading = "loading..."
            face_image = frame[max(0, y1):min(height, y2), max(0, x1):min(width, x2)]    
            identity = recognize_face(face_image, input_embeddings, model)
            img = cv2.rectangle(frame,(x1, y1),(x2, y2),(255,255,255),2)
            cv2.putText(img, str(loading), (x1+5,y1-5), font, 1, (255,255,255), 2)
            if identity is not None:
                # img = cv2.rectangle(frame,(x1, y1),(x2, y2),(255,255,255),2)
                # cv2.putText(img, str(identity), (x1+5,y1-5), font, 1, (255,255,255), 2)
                cv2.destroyAllWindows()
                return identity
        # frame = cv2.resize(frame, (600, 300))     
        cv2.imshow('reconnaissance faciale',cv2.pyrDown(frame))
        key = cv2.waitKey(10)
        if key == 27: # exit on ESC
            break
    cv2.destroyAllWindows()

print("creation du modele")
model = createModel()
print("modele cree")
print("chargement des poids")
loadweights = loadWeights(model)
print("poids chargés")
print("creation des vecteur d'intégration")
input_embeddings = create_input_image_embeddings(model)
print("fin de création")
def main(src="",type=""):
    print("----------------------------start------------------------------------------")
    # print("creation du modele")
    # model = createModel()
    # print("modele cree")
    # print("chargement des poids")
    # loadweights = loadWeights(model)
    # print("poids chargés")
    # print("creation des vecteur d'intégration")
    # input_embeddings = create_input_image_embeddings(model)
    # print("fin de création")
    print("face reconition")
    if src!="" and type=="video":
        return streamVideo(input_embeddings,model,src)
    else:
        if src!="" and type=="image":
            return streamImage(input_embeddings,model,src)
        else:
            if src!="" and type=="phone":
                return streamVideoPhone(input_embeddings,model)
            else:
                return recognize_faces_in_cam(input_embeddings,model)

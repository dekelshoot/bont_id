from cgitb import reset
from genericpath import exists
import re
from tkinter import Frame
from django.shortcuts import render,redirect
import cv2
import shutil
# Create your views here.

from django.http import HttpResponse
from django.shortcuts import render
from matplotlib import image
from numpy import identity
from .models import *
from django.core.mail import EmailMessage
from django.views.decorators import gzip
from django.http import StreamingHttpResponse
from face.models import *
from django.contrib.staticfiles.storage import staticfiles_storage  
import cv2
import os
import threading
from face.forms import IdForm
from face.models import Identite
import face.faceReconizer as fr


def start(request):
    identite = Identite.objects.all()
    if request.method == 'POST':
        name=request.POST['name']
        identite = Identite.objects.filter(name=name).get()   
        return render(request,'result.html',{'identite':identite})
    return render(request, 'start.html',{'identite':identite})

def choice(request):
    if request.method == 'POST':
        dic = request.POST
        print(request.POST)
        if 'video' in dic:
            name=fr.main(src=str(request.POST['video']),type='video')
            if name!=None:
                name=name[:-1].split("_")
                name= " ".join(name)
                identite = Identite.objects.filter(name=name).get()
                    #image= identite.image1    
                return render(request,'result.html',{'identite':identite})
        else:
            if 'image' in dic:
                name=fr.main(src=str(request.POST['image']),type='image')
                if name!=None:
                    name=name[:-1].split("_")
                    name= " ".join(name)
                    identite = Identite.objects.filter(name=name).get()
                    #image= identite.image1    
                    return render(request,'result.html',{'identite':identite})
            else:
                if 'phone' in dic:
                    name=fr.main(src="phone",type='phone')
                    if name!=None:
                        name=name[:-1].split("_")
                        name= " ".join(name)
                        identite = Identite.objects.filter(name=name).get()
                        #image= identite.image1    
                        return render(request,'result.html',{'identite':identite})
                else:
                    name=fr.main() 
                    if name!=None:
                        name=name[:-1].split("_")
                        name= " ".join(name)
                        identite = Identite.objects.filter(name=name).get()
                        #image= identite.image1        
                    return render(request,'result.html',{'identite':identite})

    # if request.method == 'POST':
    #     name=fr.main() 
    #     name=name[:-1].split("_")
    #     name= " ".join(name)
    #     identite = Identite.objects.filter(name=name).get()
    #     #image= identite.image1    
    #     return render(request,'result.html',{'identite':identite})
    # fr.main(src="E:/tuto/angular/1.mp4")
    return render(request, 'choice.html')


def add(request):
    if request.method == 'POST':
        # for f in request.FILES.getlist('image'):
            # print(f)
        form = IdForm(request.POST, request.FILES)
        # print(request.FILES)
        if form.is_valid():
            identite = form.save()
            id=identite.id
            source=[]
            if(identite.image1):
                saveProfil(identite.image1.path,identite.name)
                source.append('media/'+str(identite.image1))
            if(identite.image2):
                source.append('media/'+str(identite.image2))
            if(identite.image3):
                source.append('media/'+str(identite.image3))
            extraction(source)
            newidentite = Identite.objects.filter(id=id).update(
            image1= rename(identite,identite.image1,1),
            image2= rename(identite,identite.image2,2),
            image3= rename(identite,identite.image3,3),
            )
            fr.input_embeddings=fr.create_input_image_embeddings(fr.model)
            return redirect("start")
        print(form.errors)
    return render(request, 'add.html')

def rename(identite,image,id):
    name=identite.name+str(id)+"."+image.path.split(".")[-1]
    nametemp = name.split()
    name="_".join(nametemp)
    dir_path=os.path.dirname(os.path.realpath(image.path))
    a= os.path.join(dir_path,name)
    os.rename(image.path, a)
    return "images/"+name

def renameProfil(name,src,id):
    name=name+str(id)+"."+src.split(".")[-1]
    name=name+str(1)
    dir_path=os.path.dirname(os.path.realpath(image.path))
    a= os.path.join(dir_path,name)
    os.rename(image.path, a)
    return "images/"+name

def get_image_path(self, filename):
    prefix = 'images/'
    name = self.name 
    extension = os.path.splitext(filename)[-1]
    return prefix + name + extension

def saveProfil(src,name):
    name=name+"1"
    name= "_".join(name.split())
    src2= src.split("media")
    newsrc=src2[0]+'face\static`\`'+src2[-1].split("media")[-1]
    newsrc = newsrc.replace("`","")
    shutil.copy2(src, newsrc)
    dir_path=os.path.dirname(os.path.realpath(newsrc))
    a= os.path.join(dir_path,name+"."+newsrc.split(".")[-1])
    os.rename(newsrc, a)

def scanface():
    cap=cv2.VideoCapture(0)
    face=cv2.CascadeClassifier('face/static/assets/model/haarcascade_frontalface_default.xml')
    while True:
        #read the image from the cam
        _,image=cap.read()
        #now i convert the image into grayscale
        image_gray=cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        #detect all faces in the image
        faces=face.detectMultiScale(image_gray,1.3,5)
        #for every face draw a rectangle
        for x,y, width,height in faces:
            cv2.rectangle(image,(x,y),(x+width,y+height),color=(255,0,0),thickness=1)
            #cv2.putText(image,'dekelshoot',(10,500),font,1,(0,0,255),2)
        cv2.imshow('bont_ID',image)
    #     cv2.imshow('',)
        if cv2.waitKey(1)==ord('q'):
            break
    cap.release()
    cv2.destroyAllWindows()

def extraction(imagesrc):
    face=cv2.CascadeClassifier('face/static/assets/model/haarcascade_frontalface_default.xml')
    for src in imagesrc:
        image = cv2.imread(src)
        image_gray = cv2.cvtColor(image,cv2.COLOR_BGR2GRAY)
        faces = face.detectMultiScale(image_gray, 1.3, 5)
        for  x,y, width,height in faces:
            cv2.rectangle(image,(x,y),(x+width,y+height),color=(255,0,0),thickness=1)
            cv2.imwrite(src, image[y:y+height,x:x+width])
    
@gzip.gzip_page
def Home(request):
    try:
        cam = VideoCamera()
        print(gen(cam))
        return StreamingHttpResponse(gen(cam), content_type="multipart/x-mixed-replace;boundary=frame")
    except:
        pass
    return render(request, 'app1.html')

#to capture video class
class VideoCamera(object):
    def __init__(self):
        self.video = cv2.VideoCapture(0)
        (self.grabbed, self.frame) = self.video.read()
        threading.Thread(target=self.update, args=()).start()

    def __del__(self):
        self.video.release()

    def get_frame(self):
        image = self.frame
        _, jpeg = cv2.imencode('.jpg', image)
        return jpeg.tobytes()

    def update(self):
        while True:
            (self.grabbed, self.frame) = self.video.read()

def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')
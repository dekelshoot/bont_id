from django import forms
from face.models import Identite, Images
import cv2

class IdForm(forms.Form):
     name = forms.CharField(required=False)
     email = forms.EmailField()
     tel= forms.IntegerField()
     detail= forms.CharField(max_length=10000)
     image1 = forms.ImageField()
     image2 = forms.ImageField()
     image3 = forms.ImageField()
     address = forms.fields.CharField(max_length=100)

     def save(self):
          name = self.cleaned_data['name']
          email = self.cleaned_data['email']
          tel = self.cleaned_data['tel']
          detail = self.cleaned_data['detail']
          address = self.cleaned_data['address']
          image1 = self.cleaned_data['image1']
          image2= self.cleaned_data['image2']
          image3 = self.cleaned_data['image3']
          return Identite.objects.create(name=name,email=email,tel=tel
                                        ,detail=detail,address=address,image1=image1,image2=image2,image3=image3)


class Image(forms.Form):
     image = forms.ImageField()
     def save(self):
          image = self.cleaned_data['image']
          return Images.objects.create(image=image)
     

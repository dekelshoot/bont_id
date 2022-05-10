from django.contrib import admin

# Register your models here.
from face.models import Identite, Images

class identiteAdmin(admin.ModelAdmin):# nous insérons ces deux lignes..
    list_display = ('name', 'email', 'tel') 

admin.site.register(Identite,identiteAdmin)
admin.site.register(Images)
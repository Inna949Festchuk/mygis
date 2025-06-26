from django.contrib import admin
from .models import ValuesPoints, OSMPoint, OSMLine, OSMPolygon

admin.site.register(ValuesPoints)

admin.site.register(OSMPoint)
admin.site.register(OSMLine)
admin.site.register(OSMPolygon)

# class WorldLineForm(forms.ModelForm):
#     class Meta:
#         model = WorldLine
#         fields = '__all__'
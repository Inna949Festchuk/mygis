from django.contrib import admin
from .models import ValuesPoints

admin.site.register(ValuesPoints)

# class WorldLineForm(forms.ModelForm):
#     class Meta:
#         model = WorldLine
#         fields = '__all__'
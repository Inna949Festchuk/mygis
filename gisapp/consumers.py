# from channels.generic.websocket import AsyncWebsocketConsumer
# from .models import ValuesPoints
# import json
# from django.core.serializers import serialize

# class IndexConsumer(AsyncWebsocketConsumer):
#     async def connect(self):
#         await self.accept()

#     async def receive(self, text_data):
#         pass

#     async def send_data(self, data):
#         await self.send(text_data=json.dumps(data))

#     async def disconnect(self, close_code):
#         pass

#     async def update_map(self):
#         points = ValuesPoints.objects.all()
#         data = serialize('geojson', points, geometry_field='geom', fields=('f3',))
#         await self.send_data(data)
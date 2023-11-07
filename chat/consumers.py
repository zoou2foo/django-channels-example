import json

from asgiref.sync import async_to_sync
from channels.generic.websocket import WebsocketConsumer

from .models import Room, Message #now import Message as I'm working on to block non-authenticated users from sending messages & display user's username.

# WebsocketConsumer is a class that has methods that are called when a client connects to the websocket
class ChatConsumer(WebsocketConsumer): #ChatConsumer inherits from WebsocketConsumer(we called 3 methods from it connect(), disconnect() and receive())
	# when a client connects to the websocket
	def __init__(self, *args, **kwards):
		super().__init__(args, kwards)
		self.room_name = None
		self.room_group_name = None
		self.room = None
		self.user = None #new; starting to block non-authenticated users from sending messages & display user's username.
	
	# when a client connects to the websocket
	def connect(self):
		self.room_name = self.scope['url_route']['kwargs']['room_name']
		self.room_group_name = f'chat_{self.room_name}'
		self.room = Room.objects.get(name=self.room_name)
		self.user = self.scope['user'] #working on blocking non-auth users

		#connection has to be accepted
		self.accept()

		# join room group
		async_to_sync(self.channel_layer.group_add)(
			self.room_group_name,
			self.channel_name,
		)

		# send user list to the newly joined user
		self.send(json.dumps({
			'type': 'user_list',
			'users': [user.username for user in self.room.online.all()],
		}))

		if self.user.is_authenticated:
			#send the join event to the room
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'user_join',
					'user': self.user.username,
				}
			)
			self.room.online.add(self.user) #add the user to the online list

	# when a client disconnects from the websocket
	def disconnect(self, close_code):
		async_to_sync(self.channel_layer.group_discard)(
			self.room_group_name,
			self.channel_name,
		)

		if self.user.is_authenticated:
			#send the leave event to the room
			async_to_sync(self.channel_layer.group_send)(
				self.room_group_name,
				{
					'type': 'user_leave',
					'user': self.user.username,
				}
			)
			self.room.online.remove(self.user) #remove the user from the online list

	# when a client sends a message to the websocket
	def receive(self, text_data=None, bytes_data=None):
		text_data_json = json.loads(text_data)
		message = text_data_json['message']
		
		# is_authenticated is a boolean attribute of the user object to check if the user is authenticated or not
		if not self.user.is_authenticated:
			return

		# send chat message event to the room
		async_to_sync(self.channel_layer.group_send)(
			self.room_group_name,
			{
				'type': 'chat_message',
				'user': self.user.username,
				'message': message,
			}
		)
		Message.objects.create(user=self.user, room=self.room, content=message)

	def chat_message(self, event):
		self.send(text_data=json.dumps(event))

	def user_join(self, event):
		self.send(text_data=json.dumps(event))

	def user_leave(self, event):
		self.send(text_data=json.dumps(event))
#!/usr/bin/python3
import telepot
import time
import sys
import threading
import messages
from sql import DatabaseQuery
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton

token = sys.argv[1] # python3 run.py "token_bot"
bot = telepot.Bot(token)
stage  = {}

F = "setting.db"

s = DatabaseQuery(F)

s.create_table()

def searching(msg, message):
	content_type, chat_type, chat_id = telepot.glance(msg)
	i = 0
	dot = ['.', '..', '...', '']
	while True:
		status = s.get_chat_status(chat_id)
		if status == 'occuped':
			stage[chat_id] = s.get_user_to_chat(chat_id)
			bot.editMessageText(telepot.message_identifier(message), messages.STATUS_CONNECT)
			break
		else:
			if i is 3: i = 0
			else: i += 1
			bot.editMessageText(telepot.message_identifier(message), "{}{}".format(messages.STATUS_SEARCH, dot[i]))
			time.sleep(0.7)

def start(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)

	# TODO: fix reply
	# try: reply = msg['reply_to_message']['message_id']
	# except: reply = None
	reply = None

	if chat_id not in stage: stage[chat_id] = s.get_user_to_chat(chat_id)

	s.register_user(chat_id)

	if content_type == 'text' and msg['text'] == '/start':
		stage[chat_id] == 'start'
		s.active_user(chat_id) # set active user to chat
		check_connect = s.check_connect(chat_id) # check if user can connect
		if check_connect:
			stage[chat_id] = s.get_user_to_chat(chat_id)
			bot.sendMessage(chat_id, messages.STATUS_CONNECT)
		else:
			# wait an other user
			message = bot.sendMessage(chat_id, messages.STATUS_SEARCH)
			t = threading.Thread(target=searching, args=(msg, message,))
			t.start()

	elif content_type == 'text' and msg['text'] == '/nopics':
		s.set_pics(chat_id, "FALSE")

	elif content_type == 'text' and msg['text'] == '/pics':
		s.set_pics(chat_id, "TRUE")

	elif content_type == 'text' and stage[chat_id] != 0:
		if content_type == 'text' and msg['text'] == '/end':
			s.end_conversation(chat_id) # end conversation
			bot.sendMessage(stage[chat_id], messages.END_STRANGE)
			bot.sendMessage(chat_id, messages.END)
		else:
			bot.sendMessage(stage[chat_id], msg['text'], reply_to_message_id=reply) # send text

	elif content_type == 'photo' and stage[chat_id] != 0:
		check = s.check_pics(stage[chat_id])
		if check == 'TRUE': bot.sendPhoto(stage[chat_id], msg['photo'][0]['file_id'], reply_to_message_id=reply) # send photos
		else: bot.sendMessage(chat_id, messages.BLOCK_PICS)

	elif content_type == 'voice' and stage[chat_id] != 0:
		bot.sendVoice(stage[chat_id], msg['voice']['file_id'], reply_to_message_id=reply) # send voice

	elif content_type == 'sticker' and stage[chat_id] != 0:
		bot.sendSticker(stage[chat_id], msg['sticker']['file_id'], reply_to_message_id=reply) # send sticker

	elif content_type == 'location' and stage[chat_id] != 0:
		bot.sendLocation(stage[chat_id], msg['location']['latitude'], msg['location']['longitude'], reply_to_message_id=reply) # send location

	elif content_type == 'document' and stage[chat_id] != 0:
		bot.sendDocument(stage[chat_id], msg['document']['file_id'], reply_to_message_id=reply) # send document

	elif content_type == 'contact' and stage[chat_id] != 0:
		bot.sendContact(stage[chat_id], msg['contact']['phone_number'], msg['contact']['first_name'], reply_to_message_id=reply) # send contact

	elif content_type == 'audio' and stage[chat_id] != 0:
		bot.sendAudio(stage[chat_id], msg['audio']['file_id'], reply_to_message_id=reply) # send audio

	elif content_type == 'video' and stage[chat_id] != 0:
		bot.sendVideo(stage[chat_id], msg['video']['file_id'], reply_to_message_id=reply) # send video

	elif content_type == 'video_note' and stage[chat_id] != 0:
		bot.sendVideoNote(stage[chat_id], msg['video_note']['file_id'], reply_to_message_id=reply) # send video_note

bot.message_loop(start)
print("Bot started")
try:
	while True:
		time.sleep(8)
except KeyboardInterrupt:
	print("\nBot Stopped")
	sys.exit(0)

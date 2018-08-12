#!/usr/bin/python3
import telepot
import time
import sys
from telepot.namedtuple import ReplyKeyboardMarkup, KeyboardButton
import sqlite3
import threading
import sys

token = sys.argv[1] # token bot
bot = telepot.Bot(token)
stage  = {}

conn = sqlite3.connect('setting.db') # select database file to connect
c = conn.cursor() 
# check if 'users' table exist
try:
	c.execute('SELECT * FROM users')
except sqlite3.OperationalError:
	c.execute('CREATE table users ( userid VARCHAR(8) NOT NULL, status VARCHAR(8) NOT NULL DEFAULT "clean", userToChat VARCHAR(8), chatStatus VARCHAR(20) NOT NULL DEFAULT "not active");')
	conn.commit() # save modify
conn.close() # close connection

def query(query):
	conn = sqlite3.connect('setting.db')
	c = conn.cursor()
	res = c.execute(query)
	conn.commit()
	conn.close()

def searching(msg, message):
	content_type, chat_type, chat_id = telepot.glance(msg)
	i = 0
	while True:
		try:
			dot = ['', '.', '..', '...']
			conn = sqlite3.connect('setting.db')
			c = conn.cursor()
			check = c.execute("SELECT chatStatus FROM users WHERE userid = '" + str(chat_id) + "'").fetchone()[0]
			userToChat = c.execute("SELECT userToChat FROM users WHERE userid = '" + str(chat_id) + "'").fetchone()[0]
			conn.close()
			if check == 'occuped':
				stage[chat_id] = userToChat
				bot.editMessageText(telepot.message_identifier(message), "status: connected")
				break
			else:
				if i == 3:
					i = 0
				else:
					i += 1
				bot.editMessageText(telepot.message_identifier(message), "status: search" + dot[i])
				time.sleep(0.7)
		except:
			pass

def start(msg):
	content_type, chat_type, chat_id = telepot.glance(msg)
	try:
		reply = msg['reply_to_message']['message_id']
	except:
		reply = None
	try:
		stage[chat_id]
	except:
		conn = sqlite3.connect('setting.db')
		c = conn.cursor()
		try:
			stage[chat_id] = c.execute("SELECT userToChat FROM users WHERE userid = '" + str(chat_id) + "'").fetchone()[0]
		except:
			stage[chat_id] = 0
		finally:
			conn.close()
	try:
		conn = sqlite3.connect('setting.db')
		c = conn.cursor()
		c.execute("SELECT * FROM users WHERE userid = '" + str(chat_id) + "'").fetchone()[0]
		conn.close()
	except:
		query("INSERT INTO users (userid) VALUES ('" + str(chat_id) + "')")
	
	if content_type == 'text' and msg['text'] == '/start':
		stage[chat_id] = 'start'
		conn = sqlite3.connect('setting.db')
		c = conn.cursor()
		c.execute("UPDATE users SET chatStatus = 'active' WHERE userid = '" + str(chat_id) + "'")
		conn.commit()
		conn.close()
		try:
			conn = sqlite3.connect('setting.db')
			c = conn.cursor()
			userToChat = c.execute("SELECT userid FROM users WHERE chatStatus = 'active' AND NOT userid = '" + str(chat_id) + "'").fetchone()[0]
			conn.close()
			query("UPDATE users SET chatStatus = 'occuped', userToChat = '" + str(userToChat) + "'  WHERE userid = '" + str(chat_id) + "'")
			query("UPDATE users SET chatStatus = 'occuped', userToChat = '" + str(chat_id) + "'  WHERE userid = '" + str(userToChat) + "'")
			stage[chat_id] = userToChat
			bot.sendMessage(chat_id, 'status: connected')
		except:
			message = bot.sendMessage(chat_id, 'status: serching...')
			t = threading.Thread(target=searching, args=(msg, message,))
			t.start()
			# search an other user
	elif content_type == 'text' and stage[chat_id] != 0:
		if content_type == 'text' and msg['text'] == '/end':
			# end conversation
			query("UPDATE users SET chatStatus = 'not active', userToChat = 'NULL'  WHERE userid = '" + str(chat_id) + "'")
			query("UPDATE users SET chatStatus = 'not active', userToChat = 'NULL'  WHERE userid = '" + str(stage[chat_id]) + "'")
			bot.sendMessage(stage[chat_id], "your stranger ending conversetion, type /start to starting a new conversation")
			bot.sendMessage(chat_id, "ending conversetion, type /start to starting a new conversation")
		else:
			bot.sendMessage(stage[chat_id], msg['text'], reply_to_message_id=reply) # send text
	elif content_type == 'photo' and stage[chat_id] != 0:
		bot.sendPhoto(stage[chat_id], msg['photo'][0]['file_id'], reply_to_message_id=reply) # send photos
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

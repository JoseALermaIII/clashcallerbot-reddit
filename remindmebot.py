#! /usr/bin/python -O
import praw
import re
import MySQLdb
from datetime import date, datetime, timedelta
import time
import ConfigParser


config = ConfigParser.ConfigParser()
config.read("remindmebot.cfg")


user_agent = ("RemindMeBot v1.0 by /u/RemindMeBotWrangler")
reddit = praw.Reddit(user_agent = user_agent)
reddit_user = config.get("Reddit", "username")
reddit_pass = config.get("Reddit", "password")
host = config.get("SQL", "host")
user = config.get("SQL", "user")
password = config.get("SQL", "passwd")
db = config.get("SQL", "db")
reddit.login(reddit_user, reddit_pass)

commented = []

class Connect:
	connection = None
	cursor = None

	def __init__(self):
		try:
			self.connection = MySQLdb.connect(host= host, user = user, passwd= password, db= db)
			self.cursor = self.connection.cursor()
		except Exception, e:
			print e
	def execute(self, command):
		try:
			self.cursor.execute(command)
		except Exception, e:
			print e
	def fetchall(self):
		try:
			return self.cursor.fetchall()
		except Exception, e:
			print e
	def commit(self):
		try:
			self.connection.commit()
		except Exception, e:
			print e
	def close(self):
		try:
			self.connection.close()
		except Exception, e:
			print e
def parse_comment(comment):
	if (comment not in commented):

		#defaults
		time_day_int = 1
		time_hour_int = 0
		message_input = '"Hello, I\'m here to remind you to see the parent comment!"'



		#check for hours
		#regex: 4.0 or 4 "hour | hours" ONLY
		time_hour = re.search("(?:\d+)?\.*(?:\d+ [hH][oO][uU][rR]([sS]|))", comment.body)
		if time_hour:
			#regex: ignores ".0" and non numbers
			time_hour = re.search("\d*", time_hour.group(0))
			time_hour_int = int(time_hour.group(0))
			#no longer than a 24 hour day
			if time_hour_int >= 24:
				time_hour_int = 24



		#check for days
		#regex: 4.0 or 4 "day | days" ONLY
		time_day = re.search("(?:\d+)?\.*(?:\d+ [dD][aA][yY]([sS]|))", comment.body)
		if time_day:
			time_day = re.search("\d*", time_day.group(0))
			time_day_int = int(time_day.group(0))
			#no longer than a seven day week
			if time_day_int >= 7.0:
				time_day_int = 7
				time_hour_int = 0
		#cases where the user inputs hours but not days
		elif not time_day and time_hour_int > 0 :
			time_day_int = 0



		#check for comments
		#regex: Only text around quotes, avoids long messages
		message_user = re.search('(["].{0,10000}["])', comment.body)
		if message_user:
			message_input = message_user.group(0)


		save_to_db(comment, time_day_int, time_hour_int, message_input)
def save_to_db(comment, day, hour, message):
	#connect to DB
	save_to_db = Connect()
	save_to_db.connect()
	
	#setting up time and adding
	reply_date = datetime.utcnow() + timedelta(days=day) + timedelta(hours=hour)
	#9999/12/31 HH/MM/SS
	reply_date = format(reply_date, '%Y-%m-%d %H:%M:%S')

	save_to_db.execute("INSERT INTO messages_table VALUES('%s', '%s', '%s')" %(comment.permalink , message , reply_date))
	save_to_db.commit()
	save_to_db.close()	
def reply_to_original(comment, reply_date, message):
	try:
		comment_to_user = "Hello, I'll message you on {0} UTC to remind you about this post with the message {1}"
		comment.reply(comment_to_user.format(reply_date, message))
	except Exception, e:
			print e
def time_to_reply():
	#connection to DB
	query_db = Connect()
	
	#get current time to compare
	current_time = datetime.utcnow()
	current_time = format(current_time, '%Y-%m-%d %H:%M:%S')
	query_db.execute("SELECT * FROM messages_table WHERE reply_date > '%s'" %(current_time))

	data = query_db.fetchall()
	#row[0] is the permalink to reply to
	for row in data:
		print row[0]
def new_reply(permalink):
	try:
		comment_to_user = "It's time"
		comment = reddit.get_submission(permalink).comments[0]
		comment.reply(comment_to_user.format(comment_to_user))
	except Exception, e:
		print e



def main():
	while True:
		try:
			print "started loop", t0
			for comment in reddit.get_comments("all", limit=None):
				if "RemindMeBot!" in comment.body:
					parse_comment(comment)
			time.sleep(5)
			time_to_reply()
			time.sleep(25)
		except Exception, e:
			print e

main()



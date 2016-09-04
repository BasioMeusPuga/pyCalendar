#!/usr/bin/python

import sys
import sqlite3
import datetime
from os.path import realpath, dirname, exists

calendar_path = dirname(realpath(__file__)) + "/calendar.db"
if not exists(calendar_path):
	database = sqlite3.connect(calendar_path)
	database.execute("CREATE TABLE events (id INTEGER PRIMARY KEY,Name TEXT,Date TEXT,Repeat TEXT)")
	database.execute("CREATE TABLE status (id INTEGER PRIMARY KEY,Date TEXT)")

database = sqlite3.connect(calendar_path)
today = datetime.date.today()


class colors:
	GREEN = '\033[92m'
	RED = '\033[91m'
	WHITE = '\033[97m'
	ENDC = '\033[0m'


def calendar_show():

	events = database.execute("SELECT Name,Date,Repeat FROM events WHERE Date LIKE '%s'" % ('%' + str(today.day).zfill(2) + "-" + str(today.month).zfill(2) + '%')).fetchall()
	events_to_show = []
	for i in events:
		date_object = datetime.datetime.strptime(i[1], '%d-%m-%Y')
		event_year = int(date_object.strftime('%Y'))
		event_repeat = i[2]

		if event_repeat == "yes" or (event_repeat == "no" and event_year == today.year):
			events_to_show.append(i[0])

	print(", ".join(events_to_show))


def calendar_add():

	event_name = input("Name: ")
	event_date = input("Date DD-MM-YYYY: ")
	try:
		datetime.datetime.strptime(event_date, '%d-%m-%Y')
	except:
		print(colors.RED + "Invalid date." + colors.ENDC)
		exit()
	event_repeat = input("Repeat? (Y/no) ")
	if event_repeat != "no":
		event_repeat = "yes"

	event_insert = input("Insert into Database? (yes/N) ")
	if event_insert == "yes":
		database.execute("INSERT INTO events (Name,Date,Repeat) VALUES ('{0}','{1}','{2}')".format(event_name, event_date, event_repeat))
		database.commit()


def calendar_seen():

	today_formatted = str(today.day).zfill(2) + "-" + str(today.month).zfill(2) + "-" + str(today.year)
	status = database.execute("SELECT Date FROM status WHERE Date = '%s'" % (today_formatted)).fetchone()
	if status is not None:
		print("Today's events are marked " + colors.GREEN + "unseen" + colors.ENDC)
	else:
		print("Today's events are marked " + colors.RED + "seen" + colors.ENDC)
	events_seen = input("Toggle? (Y/no) ")
	if events_seen != "no":
		if status is None:
			database.execute("INSERT INTO status (Date) VALUES ('{0}')".format(today_formatted))
			database.commit()
		else:
			database.execute("DELETE FROM status")
			database.execute("VACUUM")


def main():
	try:
		if sys.argv[1] == "--show":
			calendar_show()
		elif sys.argv[1] == "--add":
			calendar_add()
		elif sys.argv[1] == "--seen":
			calendar_seen()
	except IndexError:
		print(colors.WHITE + "Usage: --show / --add / --seen")

main()
database.close()

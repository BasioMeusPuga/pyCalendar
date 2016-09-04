#!/usr/bin/python

import sqlite3
import datetime
import argparse
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


def calendar_show(timeframe):

	events_to_show = []

	# Display all events that occur today
	if timeframe == "BlankForAllIntensivePurposes":
		events = database.execute("SELECT Name,Date,Repeat FROM events WHERE Date LIKE '%s'" % ('%' + str(today.day).zfill(2) + "-" + str(today.month).zfill(2) + '%')).fetchall()
		for i in events:
			date_object = datetime.datetime.strptime(i[1], '%d-%m-%Y')
			event_year = int(date_object.strftime('%Y'))
			event_repeat = i[2]

			if event_repeat == "yes" or (event_repeat == "no" and event_year == today.year):
				events_to_show.append(i[0])

		print(", ".join(events_to_show))

	# Display all events in the provided timeframe
	else:
		if timeframe.isdigit() is True:
			tf_pf = "+"
			tf_days = int(timeframe)
		else:
			tf_pf = timeframe[0]
			tf_days = int(timeframe[1:])

		valid_dates = []
		valid_dates_cfr = []
		for i in range(tf_days + 1):
			my_timedelta = datetime.timedelta(days=i)
			if tf_pf == "+":
				next_valid_date = str(today + my_timedelta)
			elif tf_pf == "-":
				next_valid_date = str(today - my_timedelta)

			date_object = datetime.datetime.strptime(next_valid_date, '%Y-%m-%d')
			next_valid_date = date_object.strftime('%d-%m-%Y')
			valid_dates.append(next_valid_date)
			next_valid_date_cfr = date_object.strftime('%d-%m')
			valid_dates_cfr.append(next_valid_date_cfr)

		events = database.execute("SELECT Name,Date,Repeat FROM events").fetchall()
		for j in events:
			if j[1] in valid_dates or (j[1][:5] in valid_dates_cfr and j[2] == "yes"):
				date_object = datetime.datetime.strptime(j[1][:5], '%d-%m')
				sexy_date = date_object.strftime('%A, %d %B')
				days_away = abs(today - datetime.date(today.year, int(j[1][3:5]), int(j[1][:2])))
				events_to_show.append([j[0], sexy_date, days_away.days])
				events_to_show = sorted(events_to_show, key=lambda x: x[2])

		template = "{0:20}{1:30}{2:10}"
		print()
		print(template.format(colors.GREEN + "Name", "Date".rjust(35), "±Days".rjust(10) + colors.ENDC))
		for k in events_to_show:
			print(template.format(k[0], k[1].rjust(30), k[2]))


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
	parser = argparse.ArgumentParser(description='A CLI CALENDAR. IT\'S THE FUTURE.', add_help=False)
	parser.add_argument('--add', action='store_true', help='Add date to calendar', required=False)
	parser.add_argument('--help', help='This helpful message', action='help')
	parser.add_argument('--seen', action='store_true', help='Toggle seen status for today\'s events', required=False)
	parser.add_argument('--show', type=str, nargs='?', const='BlankForAllIntensivePurposes', help='Show calendar events', metavar="±days", required=False)
	args = parser.parse_args()

	if args.add:
		calendar_add()
	elif args.seen:
		calendar_seen()
	elif args.show:
		calendar_show(args.show)
	else:
		parser.print_help()

main()
database.close()

#!/usr/bin/python3
import json
import os
import pymysql

import flask
app = flask.Flask(__name__)

# Database connection parameters - update as needed
DB_USER=os.getenv('DB_USER') or 'root'
DB_PSWD=os.getenv('DB_PSWD') or None
DB_NAME=os.getenv('DB_NAME') or 'task_logger'
DB_SOCKET=os.getenv('DB_SOCKET') or None

db = pymysql.connect(unix_socket=DB_SOCKET, 
										 user=DB_USER, 
										 password=DB_PSWD, 
										 database=DB_NAME, 
										 cursorclass=pymysql.cursors.DictCursor)
cursor = db.cursor()

# Create a new task
def create_task(title):
	try:
		cursor.execute("INSERT INTO tasks (title) VALUES (%s)", title)
		db.commit()
		cursor.execute("SELECT MAX(id) AS id FROM tasks")
		row = cursor.fetchone()
		resp = get_task(row['id'])
		return (resp[0], 201)
	except Exception as e:
		return (str(e), 500)

# Get all tasks
def get_tasks():
	try:
		cursor.execute("SELECT id, title, date_format(created, '%Y-%m-%d %H:%i') as created FROM tasks")
		return (cursor.fetchall(), 200)
	except Exception as e:
		return (str(e), 500)

# Get an individual task
def get_task(id):
	try:
		cursor.execute("SELECT id, title, date_format(created, '%Y-%m-%d %H:%i') as created \
										FROM tasks WHERE id="+str(id))
		row = cursor.fetchone()
		return (row if row is not None else '', 200 if row is not None else 404)
	except Exception as e:
		return ('', 404)
		
# Update an existing task
def update_task(id, title):
	try:
		cursor.execute("UPDATE tasks SET title=%s WHERE id=%s", (title, id))
		db.commit()
		return get_task(id)
	except Exception as e:
		return (str(e), 500)
		
# Delete an existing task
def delete_task(id):
	try:
		resp = get_task(id)
		if resp[1] == 200:
			cursor.execute("DELETE FROM tasks WHERE id=%s", id)
			db.commit()
			return ('', 200)
		else:
			return resp
	except Exception as e:
		return (str(e), 500)

# Returns the HTTP request method
def get_method():
	return flask.request.method or 'GET'

# Returns the query string	
def get_query_string():
	query_string = flask.request.query_string.decode() or ''
	return query_string.replace('+', ' ')

# Returns the task ID if set in the request query string
def get_task_id():
	query_string = get_query_string()
	qs_parts = query_string.split('/')
	return qs_parts[0] if qs_parts[0].isnumeric() else None

# Returns the task title from the query string if set
def get_task_title():
	title = None
	query_string = get_query_string()
	if query_string != '':
		qs_parts = query_string.split('/')
		title = qs_parts[1] if len(qs_parts) > 1 else qs_parts[0]
		title = None if title.isnumeric() else title
	return title

# Returns True if title is valid, False otherwise
def title_is_valid(title):
	return True if isinstance(title, str) and len(title) >= 6 and len(title) <= 255 else False


# Entrypoint
@app.route('/', methods=['GET', 'POST', 'PUT', 'DELETE'])
def entrypoint():
	method = get_method()
	id = get_task_id()
	title = get_task_title()

	if method == 'GET' and not id is None:
		resp = get_task(id)
	elif method == 'GET':
		resp = get_tasks()
	elif method == 'DELETE':
		resp = delete_task(id)
	elif not title_is_valid(title):
		resp = ('', 400)
	elif method == 'POST':
		resp = create_task(title)
	elif method == 'PUT':
		resp = update_task(id, title)

	return(json.dumps(resp[0]), resp[1], {'Content-Type': 'application/json'})

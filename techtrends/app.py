import sqlite3

from flask import Flask, jsonify, json, render_template, request, url_for, redirect, flash
from werkzeug.exceptions import abort
from datetime import datetime
import logging


# Global variable for maintaining the connection count
connection_count = 0

# Function to get a database connection.
# This function connects to database with the name `database.db`
def get_db_connection():
    global connection_count
    connection = sqlite3.connect('database.db')
    connection.row_factory = sqlite3.Row
    connection_count += 1
    return connection

# Function to get a post using its ID
def get_post(post_id):
    connection = get_db_connection()
    post = connection.execute('SELECT * FROM posts WHERE id = ?',
                        (post_id,)).fetchone()
    connection.close()
    return post

# Define the Flask application
app = Flask(__name__)
app.config['SECRET_KEY'] = 'your secret key'

# Define the main route of the web application 
@app.route('/')
def index():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    return render_template('index.html', posts=posts)

# Define how each individual article is rendered 
# If the post ID is not found a 404 page is shown
@app.route('/<int:post_id>')
def post(post_id):
    post = get_post(post_id)
    if post is None:
        logger_error_msg('Article with id "{}", does not exist.'.format(post_id))        
        return render_template('404.html'), 404
    else:
        logger_info_msg('Retrieved article with title "{}"'.format(post['title']))
        return render_template('post.html', post=post)

# Define the About Us page
@app.route('/about')
def about():
    logger_info_msg("About page rendered")
    return render_template('about.html')

# Define the post creation functionality 
@app.route('/create', methods=('GET', 'POST'))
def create():
    if request.method == 'POST':
        title = request.form['title']
        content = request.form['content']

        if not title:
            flash('Title is required!')
        else:
            connection = get_db_connection()
            connection.execute('INSERT INTO posts (title, content) VALUES (?, ?)',
                         (title, content))
            connection.commit()
            connection.close()
            
            logger_info_msg('Article "{}" created.'.format(title))

            return redirect(url_for('index'))

    return render_template('create.html')

# Hardcoded healthz endpoint
@app.route('/healthz')
def healthz():
    response = app.response_class(
        response=json.dumps({"result":"OK - healthy"}),
        status=200,
        mimetype='application/json')

    return response

@app.route('/metrics')
def metrics():
    connection = get_db_connection()
    posts = connection.execute('SELECT * FROM posts').fetchall()
    connection.close()
    post_count = len(posts)

    response = app.response_class(
        response=json.dumps({"db_connection_count": connection_count, "post_count": post_count}),
        status=200,
        mimetype='application/json'
    
    )
    return response

# Helper function for logging
def logger_info_msg(msg):
    app.logger.info(msg)

def logger_error_msg(msg):
    app.logger.error(msg)

# start the application on port 3111
if __name__ == "__main__":
    # Configuring the level of logging parameter 
    # and format for the logs to be generated
    # logger will log to STDOUT
    logging.basicConfig(
        level=logging.DEBUG, 
        format= '[%(asctime)s] {%(pathname)s:%(lineno)d} %(levelname)s - %(message)s',
        datefmt='%H:%M:%S')
        
    app.run(host='0.0.0.0', port='3111')

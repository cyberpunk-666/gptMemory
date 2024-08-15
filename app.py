from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2 import Error
import json
import os
import logging
from logging.config import dictConfig

app = Flask(__name__)

# Configure logging
dictConfig({
    'version': 1,
    'formatters': {'default': {
        'format': '[%(asctime)s] %(levelname)s in %(module)s: %(message)s',
    }},
    'handlers': {'wsgi': {
        'class': 'logging.StreamHandler',
        'stream': 'ext://flask.logging.wsgi_errors_stream',
        'formatter': 'default'
    }},
    'root': {
        'level': 'INFO',
        'handlers': ['wsgi']
    }
})

# Get the database connection details from environment variables
DATABASE_URL = os.getenv('DATABASE_URL')  # Full connection URL if provided
PGDATABASE = os.getenv('PGDATABASE')
PGHOST = os.getenv('PGHOST')
PGPORT = os.getenv('PGPORT')
PGUSER = os.getenv('PGUSER')
PGPASSWORD = os.getenv('PGPASSWORD')

# Database connection
def create_connection():
    conn = None
    try:
        if DATABASE_URL:
            app.logger.info("Connecting to PostgreSQL using DATABASE_URL")
            conn = psycopg2.connect(DATABASE_URL)  # Use DATABASE_URL if available
        else:
            app.logger.info("Connecting to PostgreSQL using individual parameters")
            conn = psycopg2.connect(
                database=PGDATABASE,
                user=PGUSER,
                password=PGPASSWORD,
                host=PGHOST,
                port=PGPORT
            )
        app.logger.info("Connected to the database successfully")
    except Error as e:
        app.logger.error(f"Error connecting to PostgreSQL: {e}")
    return conn

def create_table():
    conn = create_connection()
    try:
        sql_create_memory_table = """ CREATE TABLE IF NOT EXISTS memory (
                                        id SERIAL PRIMARY KEY,
                                        memory_data JSONB NOT NULL
                                    ); """
        cur = conn.cursor()
        cur.execute(sql_create_memory_table)
        conn.commit()
        app.logger.info("Table 'memory' created successfully or already exists")
    except Error as e:
        app.logger.error(f"Error creating table: {e}")
    finally:
        if conn:
            cur.close()
            conn.close()

create_table()

# Store memory endpoint
@app.route('/store-memory', methods=['POST'])
def store_memory():
    memory_data = request.json.get('memory_data')
    conn = create_connection()
    try:
        sql_insert_memory = ''' INSERT INTO memory(memory_data)
                                VALUES(%s) RETURNING id; '''
        cur = conn.cursor()
        cur.execute(sql_insert_memory, (json.dumps(memory_data),))  # Store as JSONB
        memory_id = cur.fetchone()[0]
        conn.commit()
        app.logger.info(f"Memory stored successfully with ID: {memory_id}")
        return jsonify({"message": "Memory stored successfully!", "id": memory_id}), 201
    except Error as e:
        app.logger.error(f"Error storing memory: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

# Retrieve memory endpoint
@app.route('/retrieve-memory', methods=['GET'])
def retrieve_memory():
    conn = create_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT id, memory_data FROM memory")
        rows = cur.fetchall()
        memories = [{"id": row[0], "memory_data": row[1]} for row in rows]
        app.logger.info("Retrieved all memories successfully")
        return jsonify(memories), 200
    except Error as e:
        app.logger.error(f"Error retrieving memories: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

# Update memory endpoint
@app.route('/update-memory/<int:id>', methods=['PUT'])
def update_memory(id):
    memory_data = request.json.get('memory_data')
    conn = create_connection()
    try:
        sql_update_memory = ''' UPDATE memory
                                SET memory_data = %s
                                WHERE id = %s; '''
        cur = conn.cursor()
        cur.execute(sql_update_memory, (json.dumps(memory_data), id))
        conn.commit()
        app.logger.info(f"Memory with ID: {id} updated successfully")
        return jsonify({"message": "Memory updated successfully!"}), 200
    except Error as e:
        app.logger.error(f"Error updating memory with ID {id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

# Delete memory endpoint
@app.route('/delete-memory/<int:id>', methods=['DELETE'])
def delete_memory(id):
    conn = create_connection()
    try:
        sql_delete_memory = 'DELETE FROM memory WHERE id=%s;'
        cur = conn.cursor()
        cur.execute(sql_delete_memory, (id,))
        conn.commit()
        app.logger.info(f"Memory with ID: {id} deleted successfully")
        return jsonify({"message": "Memory deleted successfully!"}), 200
    except Error as e:
        app.logger.error(f"Error deleting memory with ID {id}: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

# Web interface
@app.route('/')
def index():
    app.logger.info("Rendering index page")
    return render_template('index.html')

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')  # Default to 127.0.0.1 if FLASK_HOST is not set
    port = int(os.getenv('FLASK_PORT', 5000))    # Default to port 5000 if FLASK_PORT is not set
    app.logger.info(f"Starting Flask app on {host}:{port}")
    app.run(debug=True, host=host, port=port)

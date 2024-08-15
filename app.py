from flask import Flask, request, jsonify, render_template
import sqlite3
from sqlite3 import Error
import json
import os

app = Flask(__name__)

# Get the database path from an environment variable or use a default path
DATABASE_PATH = os.getenv('DATABASE_PATH', 'memory.db')

# Database setup
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect(DATABASE_PATH)
    except Error as e:
        print(e)
    return conn

def create_table():
    conn = create_connection()
    try:
        sql_create_memory_table = """ CREATE TABLE IF NOT EXISTS memory (
                                        id integer PRIMARY KEY,
                                        memory_data text NOT NULL
                                    ); """
        c = conn.cursor()
        c.execute(sql_create_memory_table)
    except Error as e:
        print(e)
    finally:
        if conn:
            conn.close()

create_table()

# Store memory endpoint
@app.route('/store-memory', methods=['POST'])
def store_memory():
    memory_data = request.json.get('memory_data')
    conn = create_connection()
    try:
        sql = ''' INSERT INTO memory(memory_data)
                  VALUES(?) '''
        cur = conn.cursor()
        cur.execute(sql, (json.dumps(memory_data),))  # Convert dictionary to JSON string
        conn.commit()
        return jsonify({"message": "Memory stored successfully!"}), 201
    except Error as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# Retrieve memory endpoint
@app.route('/retrieve-memory', methods=['GET'])
def retrieve_memory():
    conn = create_connection()
    try:
        cur = conn.cursor()
        cur.execute("SELECT * FROM memory")
        rows = cur.fetchall()
        memories = []
        for row in rows:
            memories.append({"id": row[0], "memory_data": json.loads(row[1])})  # Convert JSON string back to dictionary
        return jsonify(memories), 200
    except Error as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# Update memory endpoint
@app.route('/update-memory/<int:id>', methods=['PUT'])
def update_memory(id):
    memory_data = request.json.get('memory_data')
    conn = create_connection()
    try:
        sql = ''' UPDATE memory
                  SET memory_data = ?
                  WHERE id = ?'''
        cur = conn.cursor()
        cur.execute(sql, (json.dumps(memory_data), id))
        conn.commit()
        return jsonify({"message": "Memory updated successfully!"}), 200
    except Error as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# Delete memory endpoint
@app.route('/delete-memory/<int:id>', methods=['DELETE'])
def delete_memory(id):
    conn = create_connection()
    try:
        sql = 'DELETE FROM memory WHERE id=?'
        cur = conn.cursor()
        cur.execute(sql, (id,))
        conn.commit()
        return jsonify({"message": "Memory deleted successfully!"}), 200
    except Error as e:
        print(e)
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            conn.close()

# Web interface
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')  # Default to 127.0.0.1 if FLASK_HOST is not set
    port = int(os.getenv('FLASK_PORT', 5000))    # Default to port 5000 if FLASK_PORT is not set
    app.run(debug=True, host=host, port=port)

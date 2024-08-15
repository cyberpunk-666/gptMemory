from flask import Flask, request, jsonify, render_template
import psycopg2
from psycopg2 import Error
import json
import os

app = Flask(__name__)

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
            conn = psycopg2.connect(DATABASE_URL)  # Use DATABASE_URL if available
        else:
            conn = psycopg2.connect(
                database=PGDATABASE,
                user=PGUSER,
                password=PGPASSWORD,
                host=PGHOST,
                port=PGPORT
            )
    except Error as e:
        print(f"Error connecting to PostgreSQL: {e}")
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
    except Error as e:
        print(f"Error creating table: {e}")
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
        return jsonify({"message": "Memory stored successfully!", "id": memory_id}), 201
    except Error as e:
        print(f"Error storing memory: {e}")
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
        return jsonify(memories), 200
    except Error as e:
        print(f"Error retrieving memories: {e}")
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
        return jsonify({"message": "Memory updated successfully!"}), 200
    except Error as e:
        print(f"Error updating memory: {e}")
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
        return jsonify({"message": "Memory deleted successfully!"}), 200
    except Error as e:
        print(f"Error deleting memory: {e}")
        return jsonify({"error": str(e)}), 500
    finally:
        if conn:
            cur.close()
            conn.close()

# Web interface
@app.route('/')
def index():
    return render_template('index.html')

if __name__ == '__main__':
    host = os.getenv('FLASK_HOST', '127.0.0.1')  # Default to 127.0.0.1 if FLASK_HOST is not set
    port = int(os.getenv('FLASK_PORT', 5000))    # Default to port 5000 if FLASK_PORT is not set
    app.run(debug=True, host=host, port=port)

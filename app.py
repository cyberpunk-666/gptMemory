from flask import Flask, request, jsonify
import sqlite3
from sqlite3 import Error
import json

app = Flask(__name__)

# Database setup
def create_connection():
    conn = None
    try:
        conn = sqlite3.connect('memory.db')
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

if __name__ == '__main__':
    app.run(debug=True)
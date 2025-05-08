from fastapi import FastAPI, Request
import json
import os
import psycopg2

app = FastAPI()

def get_db_connection():
    return psycopg2.connect(
        dbname=os.getenv("POSTGRES_DB", "notasParcial"),
        user=os.getenv("POSTGRES_USER", "usuario"),
        password=os.getenv("POSTGRES_PASSWORD", "password123"),
        host=os.getenv("DB_HOST", "db"),
    )


def init_db():
    conn = get_db_connection()
    cursor = conn.cursor()
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS notes (
            id SERIAL PRIMARY KEY,
            title TEXT NOT NULL,
            content TEXT NOT NULL
        );
    """)
    conn.commit()
    cursor.close()
    conn.close()

init_db()


@app.get("/")
async def root():
    return {
        "message": "Welcome to the FastAPI application! "
        "You can use this API to manage your notes."
    }


@app.get("/notes")
async def get_notes():
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT id, title, content FROM notes")
        rows = cursor.fetchall()
        cursor.close()
        conn.close()

        notes = [{"id": row[0], "title": row[1], "content": row[2]} for row in rows]
        return {"notes": notes}
    except Exception as e:
        return {"error": f"Error retrieving notes: {str(e)}"
                }


@app.post("/notes")
async def create_note(request: Request):
    data = await request.json()
    title = data.get("title")
    content = data.get("content")

    if not title or not content:
        return {"error": "Nombre y título son requeridos"}

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute("INSERT INTO notes (title, content) VALUES (%s, %s)", (title, content))
        conn.commit()
        cursor.close()
        conn.close()
        return {"message": "Note created successfully!"}
    except Exception as e:
        return {"error": str(e)}


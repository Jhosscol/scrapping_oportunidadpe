import sqlite3
import os
from datetime import datetime

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DB_PATH = os.path.join(BASE_DIR, 'noticias.db')

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS noticias (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            titulo TEXT NOT NULL,
            url TEXT UNIQUE NOT NULL,
            fuente TEXT,
            sector TEXT,
            fecha_publicacion TEXT,
            fecha_creacion TEXT,
            activo INTEGER DEFAULT 1
        )
    ''')
    conn.commit()
    conn.close()

def insert_noticias(noticias_list):
    """
    Inserta una lista de noticias dict en la DB. Usamos IGNORE para 
    no sobreescribir ni tirar error si la URL ya existe (deduplicación por DB).
    Retorna la cantidad de noticias insertadas nuevas.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    inserted_count = 0
    now_str = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    for n in noticias_list:
        try:
            cursor.execute('''
                INSERT INTO noticias (titulo, url, fuente, sector, fecha_publicacion, fecha_creacion, activo)
                VALUES (?, ?, ?, ?, ?, ?, 1)
            ''', (n.get("titulo"), n.get("url"), n.get("fuente"), n.get("sector"), n.get("fecha"), now_str))
            inserted_count += 1
        except sqlite3.IntegrityError:
            # Significa que ya existe una noticia con esta URL (Deduplicación instantánea)
            pass
            
    conn.commit()
    conn.close()
    return inserted_count

def get_active_noticias():
    """
    Recupera todas las noticias activas ordenadas por fecha de creación desc.
    """
    conn = sqlite3.connect(DB_PATH)
    conn.row_factory = sqlite3.Row
    cursor = conn.cursor()
    cursor.execute('''
        SELECT titulo, url, fuente, sector, fecha_publicacion as fecha
        FROM noticias
        WHERE activo = 1
        ORDER BY id DESC
    ''')
    rows = cursor.fetchall()
    conn.close()
    return [dict(row) for row in rows]

def soft_delete_old_noticias(days=30):
    """
    Desactiva las noticias cuya fecha de creación es anterior a "days" días.
    """
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    # SQLite datetime calculation
    cursor.execute(f'''
        UPDATE noticias 
        SET activo = 0 
        WHERE activo = 1 AND fecha_creacion <= datetime('now', '-{days} days')
    ''')
    modified = cursor.rowcount
    conn.commit()
    conn.close()
    return modified

# Initialize when the module loads
init_db()

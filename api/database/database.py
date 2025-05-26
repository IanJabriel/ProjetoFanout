import sqlite3
from datetime import datetime

DB_PATH = "promocoes.db"

def init_db():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS promocoes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            marca TEXT NOT NULL,
            nome TEXT NOT NULL,
            produto_id INTEGER NOT NULL,
            porcentagem INTEGER NOT NULL,
            data_inicio TEXT NOT NULL,
            data_fim TEXT NOT NULL,
            data_registro TEXT DEFAULT CURRENT_TIMESTAMP,
            UNIQUE(marca, produto_id, data_inicio)
        )
    ''') 
    conn.commit()
    conn.close()

def insert_promocao(marca: str, produto: dict):
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    try:
        cursor.execute('''
            INSERT INTO promocoes 
            (marca, nome, produto_id, porcentagem, data_inicio, data_fim)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', (
            marca,
            produto['nome'],
            produto['id'],
            produto['porcentagem'],
            produto['dataInicio'],
            produto['dataFim']
        ))
        conn.commit()
        return True
    except sqlite3.IntegrityError:
        return False 
    finally:
        conn.close()

def get_all_promocoes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, marca, nome, produto_id, porcentagem, data_inicio, data_fim, data_registro FROM promocoes')
    rows = cursor.fetchall()
    conn.close()

    promocoes = []
    for row in rows:
        promocoes.append({
            "id": row[0],
            "marca": row[1],
            "nome": row[2],
            "produto_id": row[3],
            "porcentagem": row[4],
            "data_inicio": row[5],
            "data_fim": row[6],
            "data_registro": row[7],
        })
    return promocoes
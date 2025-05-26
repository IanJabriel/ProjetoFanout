import sqlite3

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
            UNIQUE(marca, produto_id, data_inicio),
            CHECK(data_inicio < data_fim)
        )
    ''') 
    conn.commit()
    conn.close()

def insert_promocao(marca: str, produto: dict):
    if sobreposicao_promocao(produto['id'], produto['dataInicio'], produto['dataFim']):
        return False
        
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
    except sqlite3.IntegrityError as e:
        print(f"Erro de integridade: {e}")
        return False
    finally:
        conn.close()

def get_all_promocoes():
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute('SELECT id, marca, nome, produto_id, porcentagem, data_inicio, data_fim FROM promocoes')
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
            "data_fim": row[6]
        })
    return promocoes

def ja_processado(produto_id: int) -> bool:
    """Verifica se o produto já foi processado"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    cursor.execute("SELECT 1 FROM promocoes WHERE produto_id = ?", (produto_id,))
    exists = cursor.fetchone() is not None
    conn.close()
    return exists

def sobreposicao_promocao(produto_id: int, data_inicio: str, data_fim: str) -> bool:
    """Verifica se já existe promoção para o mesmo produto com datas sobrepostas"""
    conn = sqlite3.connect(DB_PATH)
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT 1 FROM promocoes 
        WHERE produto_id = ? 
        AND data_inicio < ? 
        AND data_fim > ?
    ''', (produto_id, data_fim, data_inicio))
    
    exists = cursor.fetchone() is not None
    conn.close()
    return exists
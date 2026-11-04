# app/create_db.py

from app.database import get_connection

conn = get_connection()

cursor = conn.cursor()


cursor.execute("""
CREATE TABLE IF NOT EXISTS movimentacoes (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    ticker TEXT NOT NULL,

    tipo TEXT NOT NULL,

    quantidade REAL NOT NULL,

    preco REAL NOT NULL,

    data_operacao DATETIME DEFAULT CURRENT_TIMESTAMP

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS ativos (

    ticker TEXT PRIMARY KEY,

    nome TEXT,

    tipo TEXT,

    ativo INTEGER DEFAULT 1,

    data_cadastro DATETIME DEFAULT CURRENT_TIMESTAMP

)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS gauss_curve (

    ticker TEXT NOT NULL,

    retorno REAL NOT NULL,

    densidade REAL NOT NULL,

    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS analytics_estatistica (
    
    ticker TEXT PRIMARY KEY,
    
    media_retorno REAL,
    
    desvio_padrao REAL,
    
    retorno_atual REAL,
    
    z_score REAL,
    
    percentil REAL,
    
    faixa_1_sigma_inf REAL,
    
    faixa_1_sigma_sup REAL,
    
    faixa_2_sigma_inf REAL,
    
    faixa_2_sigma_sup REAL,
    
    faixa_3_sigma_inf REAL,
    
    faixa_3_sigma_sup REAL,
    
    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS histograma_retorno (

    ticker TEXT NOT NULL,

    faixa_retorno REAL NOT NULL,

    frequencia INTEGER NOT NULL,

    percentual_ocorrencia REAL NOT NULL,

    data_calculo DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS portfolio_resumo (

    id INTEGER PRIMARY KEY AUTOINCREMENT,

    data_referencia DATETIME DEFAULT CURRENT_TIMESTAMP,

    total_investido REAL NOT NULL,

    patrimonio_atual REAL NOT NULL,

    lucro_total REAL NOT NULL,

    rentabilidade_total REAL NOT NULL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS portfolio_snapshot (

    ticker TEXT PRIMARY KEY,

    quantidade REAL NOT NULL,

    preco_medio REAL NOT NULL,

    preco_atual REAL NOT NULL,

    valor_investido REAL NOT NULL,

    valor_atual REAL NOT NULL,

    lucro REAL NOT NULL,

    rentabilidade REAL NOT NULL,

    ultima_atualizacao DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS carteira (
    ticker TEXT PRIMARY KEY,
    quantidade REAL NOT NULL,
    preco_medio REAL NOT NULL,
    data_compra DATE
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS historico_diario (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    data_pregao DATE NOT NULL,
    abertura REAL NOT NULL,
    maxima REAL NOT NULL,
    minima REAL NOT NULL,
    fechamento REAL NOT NULL,
    variacao_percentual REAL NOT NULL,
    volume REAL,
    UNIQUE(ticker, data_pregao)
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS cotacoes(
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ticker TEXT NOT NULL,
    preco REAL NOT NULL,
    minima_dia REAL,
    maxima_dia REAL,
    abertura REAL,
    fechamento_anterior REAL,
    variacao REAL,
    variacao_percentual REAL,
    data_hora DATETIME DEFAULT CURRENT_TIMESTAMP
)
""")


conn.commit()

print("Banco criado com sucesso.")
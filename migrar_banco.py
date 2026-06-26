import sqlite3

conn = sqlite3.connect('data/thirdsys.db')

colunas = [
    "ALTER TABLE empresas ADD COLUMN tipo_empresa VARCHAR(20) DEFAULT 'fixa'",
    "ALTER TABLE empresas ADD COLUMN pgr_periodo_dias INTEGER DEFAULT 365",
    "ALTER TABLE empresas ADD COLUMN pgr_bienal BOOLEAN DEFAULT 0",
    "ALTER TABLE empresas ADD COLUMN pcmso_periodo_dias INTEGER DEFAULT 365",
    "ALTER TABLE empresas ADD COLUMN apolice_periodo_dias INTEGER DEFAULT 365",
]

for sql in colunas:
    try:
        conn.execute(sql)
        nome = sql.split("COLUMN")[1].strip().split()[0]
        print(f"OK: {nome}")
    except Exception as e:
        print(f"Ja existe ou erro: {e}")

conn.commit()
conn.close()
print("Migracao concluida!")
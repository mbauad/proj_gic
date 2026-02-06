
import os
import json
import csv
from datetime import datetime
from supabase import create_client, Client
from dotenv import load_dotenv

# Carregar variáveis de ambiente
load_dotenv()

# Configuração
URL = os.environ.get("SUPABASE_URL")
KEY = os.environ.get("SUPABASE_KEY")

if not URL or not KEY:
    print("Erro: Crie um arquivo .env com SUPABASE_URL e SUPABASE_KEY")
    exit(1)

supabase: Client = create_client(URL, KEY)

# Tabelas para backup
TABLES = [
    "atendimento_cadastro",
    "cadastro_equipe",
    "secretaries",
    "dti_room_status"
]

def backup_table(table_name, backup_dir):
    print(f"Baixando tabela: {table_name}...")
    try:
        # Baixar dados (limite alto para garantir tudo, ou paginação se fosse gigante)
        # O Supabase limita a 1000 rows por padrão sem offset, mas para backup simples vamos tentar pegar tudo
        # Se crescer muito, precisaria de paginação.
        response = supabase.table(table_name).select("*").execute()
        data = response.data
        
        if not data:
            print(f"  - Tabela vazia ou não encontrada.")
            return

        # Salvar JSON
        json_path = os.path.join(backup_dir, f"{table_name}.json")
        with open(json_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=4, ensure_ascii=False)
        print(f"  - Salvo JSON: {json_path} ({len(data)} registros)")

        # Salvar CSV (Opcional, mas útil para Excel)
        if len(data) > 0:
            csv_path = os.path.join(backup_dir, f"{table_name}.csv")
            keys = data[0].keys()
            with open(csv_path, 'w', newline='', encoding='utf-8') as f:
                writer = csv.DictWriter(f, fieldnames=keys)
                writer.writeheader()
                writer.writerows(data)
            print(f"  - Salvo CSV:  {csv_path}")

    except Exception as e:
        print(f"  - Erro ao baixar {table_name}: {str(e)}")

def main():
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_dir = os.path.join("backups", timestamp)
    os.makedirs(backup_dir, exist_ok=True)

    print(f"=== Iniciando Backup Supabase ===")
    print(f"Diretório: {backup_dir}")
    print(f"URL: {URL}")
    
    for table in TABLES:
        backup_table(table, backup_dir)
    
    print("\nBackup concluído!")

if __name__ == "__main__":
    main()

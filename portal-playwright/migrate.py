#!/usr/bin/env python3
"""Migra dados do banco legado para o schema v2.

Lê DB_* (destino) e LEGACY_DB_* (origem) do .env.
Preserva IDs para manter os relacionamentos N:N.
"""

from __future__ import annotations

import argparse
import sys
from pathlib import Path

import mysql.connector
from dotenv import load_dotenv
import os

ROOT = Path(__file__).resolve().parent
SCHEMA_FILE = ROOT / "database" / "schema_tables.sql"


def load_env() -> None:
  env_path = ROOT / ".env"
  if not env_path.exists():
    raise FileNotFoundError(f".env não encontrado em {env_path}")
  load_dotenv(env_path)


def db_config(prefix: str = "") -> dict:
  if prefix:
    return {
      "host": os.environ[f"{prefix}HOST"],
      "port": int(os.getenv(f"{prefix}PORT", "3306")),
      "user": os.environ[f"{prefix}USER"],
      "password": os.environ[f"{prefix}PASSWORD"],
      "database": os.environ[f"{prefix}NAME"],
      "connection_timeout": 30,
    }
  return {
    "host": os.environ["DB_HOST"],
    "port": int(os.getenv("DB_PORT", "3306")),
    "user": os.environ["DB_USER"],
    "password": os.environ["DB_PASSWORD"],
    "database": os.environ["DB_NAME"],
    "connection_timeout": 30,
  }


def connect(prefix: str = ""):
  return mysql.connector.connect(**db_config(prefix))


def table_exists(cursor, table_name: str) -> bool:
  cursor.execute(
    """
    SELECT 1 FROM information_schema.TABLES
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
    """,
    (table_name,),
  )
  return cursor.fetchone() is not None


def column_names(cursor, table_name: str) -> set:
  cursor.execute(
    """
    SELECT COLUMN_NAME FROM information_schema.COLUMNS
    WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s
    """,
    (table_name,),
  )
  rows = cursor.fetchall()
  names = set()
  for row in rows:
    if isinstance(row, dict):
      names.add(next(iter(row.values())))
    else:
      names.add(row[0])
  return names


def apply_schema(destino) -> None:
  print(f"Aplicando schema em {db_config()['database']}...")
  sql = SCHEMA_FILE.read_text(encoding="utf-8")
  cursor = destino.cursor()
  for statement in sql.split(";"):
    statement = statement.strip()
    if not statement or statement.startswith("--"):
      continue
    cursor.execute(statement)

  # Banco legado tem nomes duplicados / só difere capitalização — remove UNIQUE antigo se existir
  for tabela, indice in (
    ("origens", "uq_origens_nome"),
    ("destinos", "uq_destinos_nome"),
    ("tipo_veiculo", "uq_tipo_veiculo_nome"),
  ):
    cursor.execute(
      """
      SELECT 1 FROM information_schema.STATISTICS
      WHERE TABLE_SCHEMA = DATABASE() AND TABLE_NAME = %s AND INDEX_NAME = %s
      LIMIT 1
      """,
      (tabela, indice),
    )
    if cursor.fetchone():
      cursor.execute(f"ALTER TABLE `{tabela}` DROP INDEX `{indice}`")
      print(f"  removido índice UNIQUE {indice}")

  destino.commit()
  cursor.close()
  print("Schema OK.")


def truncate_target(destino, limpar: bool) -> None:
  if not limpar:
    return
  print("Limpando tabelas do destino (--limpar)...")
  cursor = destino.cursor()
  cursor.execute("SET FOREIGN_KEY_CHECKS = 0")
  for tabela in (
    "rotas_processadas",
    "relatorios",
    "rotas",
    "motorista_tipo_veiculo_carreta",
    "motorista_tipo_veiculo",
    "motorista_destino",
    "motorista_origem",
    "motoristas",
    "tipo_veiculo",
    "destinos",
    "origens",
    "parametros",
    "login",
  ):
    cursor.execute(f"TRUNCATE TABLE `{tabela}`")
  cursor.execute("SET FOREIGN_KEY_CHECKS = 1")
  destino.commit()
  cursor.close()


def fetchall_dict(cursor, query: str, params=None):
  cursor.execute(query, params or ())
  rows = cursor.fetchall()
  if not rows:
    return []
  if isinstance(rows[0], dict):
    return rows
  colunas = [desc[0] for desc in cursor.description]
  return [dict(zip(colunas, row)) for row in rows]


def inserir_muitos(cursor, tabela: str, colunas: list, linhas: list) -> int:
  if not linhas:
    return 0
  # created_at/updated_at ficam com DEFAULT do schema (legado pode ter NULL)
  colunas_validas = [coluna for coluna in colunas if coluna not in ("created_at", "updated_at")]
  placeholders = ", ".join(["%s"] * len(colunas_validas))
  cols_sql = ", ".join(f"`{coluna}`" for coluna in colunas_validas)
  query = f"INSERT INTO `{tabela}` ({cols_sql}) VALUES ({placeholders})"
  valores = [tuple(linha[coluna] for coluna in colunas_validas) for linha in linhas]
  cursor.executemany(query, valores)
  return len(valores)


def migrar_login(origem_cur, destino_cur) -> int:
  rows = fetchall_dict(origem_cur, "SELECT * FROM login")
  mapeados = []
  for row in rows:
    mapeados.append(
      {
        "id": row["id"],
        "usuario": row.get("login") or row.get("usuario") or "",
        "senha": row.get("senha") or "",
        "ativo": True,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
      }
    )
  return inserir_muitos(
    destino_cur,
    "login",
    ["id", "usuario", "senha", "ativo", "created_at", "updated_at"],
    mapeados,
  )


def migrar_parametros(origem_cur, destino_cur) -> int:
  rows = fetchall_dict(origem_cur, "SELECT * FROM parametros")
  mapeados = []
  for row in rows:
    modo = row.get("moto_teste", row.get("modo_teste", 1))
    mapeados.append(
      {
        "id": row["id"],
        "limite_valor_truck": row.get("valor_maximo_carga_truck") or 0,
        "limite_valor_toco": row.get("valor_maximo_carga_bi_truck") or 0,
        "limite_valor_carreta": row.get("valor_maximo_carga_carreta_truck") or 0,
        "modo_teste": bool(modo),
        "email_notificacao": row.get("emails_notificacao") or row.get("email_notificacao") or "",
        "intervalo_espera_seg": 30,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
      }
    )
  return inserir_muitos(
    destino_cur,
    "parametros",
    [
      "id",
      "limite_valor_truck",
      "limite_valor_toco",
      "limite_valor_carreta",
      "modo_teste",
      "email_notificacao",
      "intervalo_espera_seg",
      "created_at",
      "updated_at",
    ],
    mapeados,
  )


def migrar_catalogo(origem_cur, destino_cur, tabela: str, coluna_nome: str) -> int:
  rows = fetchall_dict(origem_cur, f"SELECT * FROM `{tabela}`")
  mapeados = []
  for row in rows:
    item = {
      "id": row["id"],
      coluna_nome: (row.get(coluna_nome) or "")[:255],
      "created_at": row.get("created_at"),
    }
    if tabela in ("origens", "destinos"):
      item["ativo"] = True
    mapeados.append(item)

  if tabela in ("origens", "destinos"):
    colunas = ["id", coluna_nome, "ativo", "created_at"]
  else:
    colunas = ["id", coluna_nome, "created_at"]
  return inserir_muitos(destino_cur, tabela, colunas, mapeados)


def migrar_motoristas(origem_cur, destino_cur) -> int:
  cols = column_names(origem_cur, "motoristas")
  rows = fetchall_dict(origem_cur, "SELECT * FROM motoristas")
  mapeados = []
  for row in rows:
    mapeados.append(
      {
        "id": row["id"],
        "placa": (row.get("placa") or "")[:20],
        "cpf": (row.get("cpf") or "")[:20],
        "nome": (row.get("nome") or "")[:200],
        "aceita_bobina": bool(row.get("aceita_bobina") or 0),
        "situacao": bool(row.get("situacao") if row.get("situacao") is not None else 1),
        "ordem_motorista": row.get("ordem_motorista") if row.get("ordem_motorista") is not None else 100,
        "placa_carreta": (row.get("placa_carreta") or None) if "placa_carreta" in cols else None,
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
      }
    )
  return inserir_muitos(
    destino_cur,
    "motoristas",
    [
      "id",
      "placa",
      "cpf",
      "nome",
      "aceita_bobina",
      "situacao",
      "ordem_motorista",
      "placa_carreta",
      "created_at",
      "updated_at",
    ],
    mapeados,
  )


def migrar_nn(
  origem_cur,
  destino_cur,
  tabela: str,
  col_a: str,
  col_b: str,
  ids_a: set,
  ids_b: set,
) -> int:
  if not table_exists(origem_cur, tabela):
    return 0
  rows = fetchall_dict(origem_cur, f"SELECT `{col_a}`, `{col_b}` FROM `{tabela}`")
  mapeados = []
  ignorados = 0
  for row in rows:
    id_a = row[col_a]
    id_b = row[col_b]
    if id_a not in ids_a or id_b not in ids_b:
      ignorados += 1
      continue
    mapeados.append({col_a: id_a, col_b: id_b})
  # remove duplicatas
  unicos = {(item[col_a], item[col_b]): item for item in mapeados}
  inseridos = inserir_muitos(destino_cur, tabela, [col_a, col_b], list(unicos.values()))
  if ignorados:
    print(f"  aviso: {ignorados} vínculos órfãos ignorados em {tabela}")
  return inseridos


def _deduplicar_por_doc(linhas: list) -> list:
  """Mantém o registro de maior id para cada doc_transporte."""
  por_doc = {}
  vazios = []
  for linha in linhas:
    doc = (linha.get("doc_transporte") or "").strip()
    if not doc:
      vazios.append(linha)
      continue
    atual = por_doc.get(doc)
    if atual is None or (linha.get("id") or 0) > (atual.get("id") or 0):
      por_doc[doc] = linha
  resultado = list(por_doc.values()) + vazios
  ignorados = len(linhas) - len(resultado)
  if ignorados:
    print(f"  aviso: {ignorados} docs duplicados ignorados", end=" ")
  return resultado


def migrar_rotas(origem_cur, destino_cur) -> int:
  rows = fetchall_dict(origem_cur, "SELECT * FROM rotas")
  mapeados = []
  for row in rows:
    mapeados.append(
      {
        "id": row["id"],
        "origem_rota": (row.get("origem_rota") or "")[:255],
        "destino_rota": (row.get("destino_rota") or "")[:255],
        "doc_transporte": (row.get("doc_transporte") or "")[:100],
        "data_hora_chegada": (row.get("data_hora_chegada") or "")[:100],
        "valor_carga": (row.get("valor_carga") or "")[:50],
        "motorista_rota": (row.get("motorista_rota") or "")[:255],
        "tipo_veiculo": (row.get("tipo_veiculo") or "")[:100],
        "situacao": bool(row.get("situacao") if row.get("situacao") is not None else 1),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
      }
    )
  mapeados = _deduplicar_por_doc(mapeados)
  return inserir_muitos(
    destino_cur,
    "rotas",
    [
      "id",
      "origem_rota",
      "destino_rota",
      "doc_transporte",
      "data_hora_chegada",
      "valor_carga",
      "motorista_rota",
      "tipo_veiculo",
      "situacao",
      "created_at",
      "updated_at",
    ],
    mapeados,
  )


def migrar_relatorios(origem_cur, destino_cur) -> int:
  rows = fetchall_dict(origem_cur, "SELECT * FROM relatorios")
  mapeados = []
  for row in rows:
    mapeados.append(
      {
        "id": row["id"],
        "origem_rota": (row.get("origem_rota") or "")[:255],
        "destino_rota": (row.get("destino_rota") or "")[:255],
        "doc_transporte": (row.get("doc_transporte") or "")[:100],
        "data_hora_chegada": (row.get("data_hora_chegada") or "")[:100],
        "valor_carga": (row.get("valor_carga") or "")[:50],
        "peso_total": (row.get("pesoTotal") or row.get("peso_total") or "")[:50],
        "tipo_veiculo": (row.get("tipo_veiculo") or "")[:100],
        "observacoes_rota": row.get("observacoesRota") or row.get("observacoes_rota") or "",
        "prioridade": (row.get("prioridade") or "")[:100],
        "clientes": row.get("clientes") or "",
        "mais_de_um_cliente": bool(row.get("maisDeUmCliente") or row.get("mais_de_um_cliente") or 0),
        "motivo": (row.get("motivo") or "sem motivo"),
        "created_at": row.get("created_at"),
        "updated_at": row.get("updated_at"),
      }
    )
  mapeados = _deduplicar_por_doc(mapeados)
  return inserir_muitos(
    destino_cur,
    "relatorios",
    [
      "id",
      "origem_rota",
      "destino_rota",
      "doc_transporte",
      "data_hora_chegada",
      "valor_carga",
      "peso_total",
      "tipo_veiculo",
      "observacoes_rota",
      "prioridade",
      "clientes",
      "mais_de_um_cliente",
      "motivo",
      "created_at",
      "updated_at",
    ],
    mapeados,
  )


def ids_de(cursor, tabela: str) -> set:
  cursor.execute(f"SELECT id FROM `{tabela}`")
  rows = cursor.fetchall()
  ids = set()
  for row in rows:
    if isinstance(row, dict):
      ids.add(row["id"])
    else:
      ids.add(row[0])
  return ids


def main() -> int:
  parser = argparse.ArgumentParser(description="Migra banco legado → schema v2")
  parser.add_argument(
    "--limpar",
    action="store_true",
    help="TRUNCATE nas tabelas do destino antes de migrar",
  )
  parser.add_argument(
    "--sem-historico",
    action="store_true",
    help="Não migra rotas e relatorios (só cadastros)",
  )
  args = parser.parse_args()

  load_env()
  print(f"Origem : {db_config('LEGACY_DB_')['database']} @ {db_config('LEGACY_DB_')['host']}")
  print(f"Destino: {db_config()['database']} @ {db_config()['host']}")

  origem = connect("LEGACY_DB_")
  destino = connect("")
  origem_cur = origem.cursor(dictionary=True)
  destino_cur = destino.cursor()

  try:
    apply_schema(destino)
    truncate_target(destino, args.limpar)

    destino_cur.execute("SET FOREIGN_KEY_CHECKS = 0")

    print("Migrando login...", end=" ")
    print(migrar_login(origem_cur, destino_cur))

    print("Migrando parametros...", end=" ")
    print(migrar_parametros(origem_cur, destino_cur))

    print("Migrando origens...", end=" ")
    print(migrar_catalogo(origem_cur, destino_cur, "origens", "nome_origem"))

    print("Migrando destinos...", end=" ")
    print(migrar_catalogo(origem_cur, destino_cur, "destinos", "nome_destino"))

    print("Migrando tipo_veiculo...", end=" ")
    print(migrar_catalogo(origem_cur, destino_cur, "tipo_veiculo", "nome_tipo_veiculo"))

    print("Migrando motoristas...", end=" ")
    print(migrar_motoristas(origem_cur, destino_cur))

    ids_motoristas = ids_de(destino_cur, "motoristas")
    ids_origens = ids_de(destino_cur, "origens")
    ids_destinos = ids_de(destino_cur, "destinos")
    ids_tipos = ids_de(destino_cur, "tipo_veiculo")

    print("Migrando motorista_origem...", end=" ")
    print(migrar_nn(origem_cur, destino_cur, "motorista_origem", "motorista_id", "origem_id", ids_motoristas, ids_origens))

    print("Migrando motorista_destino...", end=" ")
    print(migrar_nn(origem_cur, destino_cur, "motorista_destino", "motorista_id", "destino_id", ids_motoristas, ids_destinos))

    print("Migrando motorista_tipo_veiculo...", end=" ")
    print(migrar_nn(origem_cur, destino_cur, "motorista_tipo_veiculo", "motorista_id", "tipo_veiculo_id", ids_motoristas, ids_tipos))

    print("Migrando motorista_tipo_veiculo_carreta...", end=" ")
    print(migrar_nn(origem_cur, destino_cur, "motorista_tipo_veiculo_carreta", "motorista_id", "tipo_veiculo_id", ids_motoristas, ids_tipos))

    if not args.sem_historico:
      print("Migrando rotas...", end=" ")
      print(migrar_rotas(origem_cur, destino_cur))
      print("Migrando relatorios...", end=" ")
      print(migrar_relatorios(origem_cur, destino_cur))
    else:
      print("Histórico (rotas/relatorios) pulado.")

    destino_cur.execute("SET FOREIGN_KEY_CHECKS = 1")
    destino.commit()
    print("\nMigração concluída com sucesso.")
    return 0
  except Exception as erro:
    destino.rollback()
    print(f"\nERRO na migração: {erro}", file=sys.stderr)
    raise
  finally:
    origem_cur.close()
    destino_cur.close()
    origem.close()
    destino.close()


if __name__ == "__main__":
  sys.exit(main())

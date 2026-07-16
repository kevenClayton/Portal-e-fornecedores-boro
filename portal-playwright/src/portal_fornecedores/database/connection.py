from contextlib import contextmanager
from typing import Generator

import mysql.connector
from mysql.connector import MySQLConnection

from portal_fornecedores.config.settings import get_settings


class DatabaseConnection:
  def __init__(self):
    self._settings = get_settings()

  def connect(self) -> MySQLConnection:
    return mysql.connector.connect(**self._settings.db_config)

  @contextmanager
  def cursor(self, dictionary: bool = False) -> Generator:
    connection = self.connect()
    cursor = connection.cursor(dictionary=dictionary)
    try:
      yield cursor
      connection.commit()
    except Exception:
      connection.rollback()
      raise
    finally:
      cursor.close()
      connection.close()

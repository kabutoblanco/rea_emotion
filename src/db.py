import sqlite3


class ConexionSQLite:
    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._conexion = sqlite3.connect('db-sqlite.db', check_same_thread=False)
        return cls._instance

    def get_cursor(self):
        return self._conexion.cursor()

    def close(self):
        self._conexion.close()

    def insert(self, query, data, multiply=False):
        cursor = self.get_cursor()
        if multiply:
            cursor.executemany(query, data)
        else:
            cursor.execute(query, data)
        self._conexion.commit()
        id = cursor.lastrowid
        cursor.close()
        return id

    def get(self, query, params=()):
        cursor = self.get_cursor()
        cursor.execute(query, params)
        result = cursor.fetchall()
        self._conexion.commit()
        cursor.close()
        return result
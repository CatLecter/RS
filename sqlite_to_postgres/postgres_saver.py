import dataclasses

from psycopg2.extensions import connection as _connection
from psycopg2.extras import execute_values


class PostgresSaver:
    """Загрузка данных в БД postgres."""

    def __init__(self, pg_conn: _connection):
        self.conn = pg_conn
        self.cursor = self.conn.cursor()
        self.counter = 0

    def save_all_data(self, data: dataclasses):
        """Функция сохранения всех данных из таблиц
        в БД postgres пачками по 100 записей.
        """

        for table_name, table_data in data.items():
            execute_values(
                self.cursor,
                f"""INSERT INTO content.{table_name}
                VALUES %s ON CONFLICT (id) DO NOTHING""",
                (dataclasses.astuple(row) for row in table_data),
                page_size=100,
            )
        self.conn.commit()

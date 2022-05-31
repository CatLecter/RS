from datetime import datetime, timedelta

from clickhouse_driver import Client


class EventGetter:
    def __init__(self, client: Client):
        self.client = client

    def get_for_period(self, period: int, table_name: str):
        date = datetime.today() - timedelta(period)
        f_date = date.strftime("%Y-%m-%d %H:%M:%S")
        return self.client.execute(
            f"SELECT * FROM default.{table_name} \
            WHERE datetime >= '{f_date}' ORDER BY datetime",
        )

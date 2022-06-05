from typing import Optional

import click

from event_generator.interface import generate_events


@click.command()
@click.option("-U", "--users", default=10, help="Number of users for events generator")
@click.option("-E", "--events", default=10, help="Number of events per film")
@click.option(
    "-F",
    "--films",
    default=None,
    type=int,
    help="Count of films for events generator or ALL",
)
def cli_generator_events(users: int, events: int, films: Optional[int]):
    assert events <= 500
    generate_events(number_users=users, number_events=events, numbers_films=films)


if __name__ == "__main__":
    cli_generator_events()

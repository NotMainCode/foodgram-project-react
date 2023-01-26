"""Import test data into db from /static/data/*.csv."""

import csv
import os.path
import sqlite3

from django.core import management
from django.core.management.base import BaseCommand

from api_foodgram import settings


class Command(BaseCommand):
    """Import test data in database."""

    def handle(self, *args, **options):
        management.call_command("migrate")
        fill_test_data(self)
        self.stdout.write("All test data loaded success.")


def fill_table_from_csv(self, db, cursor, filename):
    """Clear table and fill data."""
    try:
        csv_data = open(
            os.path.join(settings.STATICFILES_DIRS_DATA, filename),
            "r",
            encoding="utf8",
        )
    except IOError:
        self.stdout.write(f"File '{filename}' open error.")
    else:
        table = filename.split(".")[0]
        cursor.execute(f"DELETE FROM {table}")
        dr = csv.DictReader(csv_data, delimiter=",")
        values = []
        for i in dr:
            keys = ",".join(i.keys())
            values.append(tuple(i.values()))
        fields = ",".join("?" * len(values[0]))
        cursor.executemany(
            f"INSERT INTO {table} ({keys}) VALUES ({fields})", values
        )
        db.commit()
        self.stdout.write(
            f"Data from file '{filename}' imported in table '{table}'."
        )


def fill_test_data(self):
    """Iterate for all tables, call funcs to prepare and fill data in db."""
    db = sqlite3.connect(os.path.join(settings.BASE_DIR, "db.sqlite3"))
    cursor = db.cursor()
    for filename in os.listdir(settings.STATICFILES_DIRS_DATA):
        fill_table_from_csv(self, db, cursor, filename)

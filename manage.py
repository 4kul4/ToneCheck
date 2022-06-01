#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
import sqlite3

db = sqlite3.connect('../db.sqlite3')
c = db.cursor()    # create cursor

# c.execute("""CREATE TABLE request (           # создание и добавление bd
#     author text,
#     title text,
#     value integer
# )""")

# c.execute("INSERT INTO request VALUES ('Margarita', 'Nice day', 100)")

# c.execute("SELECT * FROM request")
# print(c.fetchall())
db.commit()

db.close()


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'django_example.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()

import os
import sys

import psycopg2 as dbapi2
import ssl
import certifi
import requests
from bs4 import BeautifulSoup

INIT_STATEMENTS = [
    """
    CREATE TABLE if not exists event (
        event_id SERIAL NOT NULL,
        event_name VARCHAR (250) UNIQUE NOT NULL ,
        event_type_number INTEGER NOT NULL,
        location VARCHAR (250) NOT NULL,
        date1 VARCHAR (100) NOT NULL,
        PRIMARY KEY (event_ID),
        FOREIGN KEY (event_type_number) REFERENCES event_type_id (event_type_id)

);
    """,
    """
    CREATE TABLE if not exists comment (
        comment_id SERIAL NOT NULL,
        event_number INTEGER NOT NULL,
        user_number INTEGER NOT NULL,
        comment TEXT NOT NULL,
        PRIMARY KEY (comment_id),
        FOREIGN KEY (user_number) REFERENCES user_info(user_id),
        FOREIGN KEY (event_number) REFERENCES event(event_id)
);
    """,
    """
    CREATE TABLE if not exists user_info (
        user_id SERIAL NOT NULL,
        username VARCHAR (250) UNIQUE NOT NULL,
        password VARCHAR (150) NOT NULL,
        email VARCHAR (150) UNIQUE NOT NULL,
        name VARCHAR (250) NOT NULL,
        age INTEGER,
        gender VARCHAR (50),
        role VARCHAR (50) NOT NULL,
        PRIMARY KEY (user_ID)
);
    """,
    """
    CREATE TABLE if not exists session (
        session_id VARCHAR(250) NOT NULL,
        userid INTEGER NOT NULL,
        PRIMARY KEY (session_ID),
        FOREIGN KEY (userid) REFERENCES user_info(user_id)
);
    """,
    """
    CREATE TABLE if not exists event_type_id (
        event_type_id SERIAL NOT NULL,
        event_type VARCHAR (150) NOT NULL,
        PRIMARY KEY (event_type_id)
);
    """,
    """
    CREATE TABLE if not exists like_info (
        user_num INTEGER REFERENCES user_info(user_id) NOT NULL,
        event_num INTEGER REFERENCES event(event_id) NOT NULL,
        PRIMARY KEY (event_num, user_num)
);
    """,
    """
    CREATE TABLE if not exists favorite_type (
        user_info INTEGER REFERENCES user_info(user_id) NOT NULL,
        event_type_number INTEGER REFERENCES event_type_id (event_type_id) NOT NULL,
        PRIMARY KEY (event_type_number, user_info)
);
    """



]


"""
      IF NOT EXISTS (SELECT username FROM user_info WHERE (username='melisgunseber') ) ;
      BEGIN;
      INSERT INTO user_info( username,password,email,name,age,gender,role) VALUES ('melisgunseber',12345,'melis.gunseber@email.com','melis',21,'female','admin') ;
      END
      """


def initialize(url):
    with dbapi2.connect(url) as connection:
        cursor = connection.cursor()
        for statement in INIT_STATEMENTS:
            cursor.execute(statement)

        cursor.close()


if __name__ == "__main__":
    url = os.getenv("DATABASE_URL")
    if url is None:
        print("Usage: DATABASE_URL=url python dbinit.py", file=sys.stderr)
        sys.exit(1)
    initialize(url)

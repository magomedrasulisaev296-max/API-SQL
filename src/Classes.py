import psycopg2

from abc import ABC, abstractmethod


class DBmanager(ABC):
    @abstractmethod
    def conn_to_BD(self):
        conn = psycopg2.connect(
            host="localhost",
            port="5432",
            database="postgres",
            user="postgres",
            password="your_password"
        )

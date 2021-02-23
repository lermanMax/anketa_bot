import psycopg2
from psycopg2.extras import DictCursor
from psycopg2.sql import SQL

from config import DB_HOST, DB_NAME, DB_PASS, DB_USER

'''
CREATE ROLE [role_name] WITH LOGIN CREATEDB PASSWORD '[password]';


comands for create Database in postgres for this bot:
    
sudo -i -u postgres
CREATE database [db_name]


'''


TABLE_users ="""CREATE TABLE users ( 
                id BIGINT PRIMARY KEY, 
                first_name varchar(80), 
                last_name varchar(80), 
                username varchar(80), 
                language_code varchar(80), 
                phone varchar(80)
                );"""

    
TABLE_answer_loyalty="""CREATE TABLE answer_loyalty ( 
                        id serial PRIMARY KEY, 
                        user_id BIGINT references users(id),
                        answering_date DATE,
                        loyalty INT,
                        manager INT, 
                        delivery INT,
                        cooking INT,
                        dietetics INT,
                        review text                
                        );""" 


with psycopg2.connect(
    host = DB_HOST,
    database = DB_NAME,
    user = DB_USER,
    password = DB_PASS,
    ) as conn:
    
    with conn.cursor(cursor_factory=DictCursor) as cur:
                        
        cur.execute(SQL(TABLE_users))
        print('TABLE_users created')
        cur.execute(SQL(TABLE_answer_loyalty))
        print('TABLE_answer_loyalty created')
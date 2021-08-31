import os
import psycopg2
from psycopg2 import Error
from notd.chain_utils import normalize_address

try:
    # Connect to an existing database
    connection = psycopg2.connect(user=os.environ['DB_USERNAME'],
                                  password=os.environ['DB_PASSWORD'],
                                  host=os.environ['DB_HOST'],
                                  port=os.environ['DB_PORT'],
                                  database=os.environ['DB_NAME'])

    cursor = connection.cursor()
    postgreSQLselectQuery =  "SELECT to_address,from_address,id FROM tbl_token_transfers"  # pylint: disable=invalid-name
    cursor.execute(postgreSQLselectQuery)
    db = cursor.fetchall()
    print("Print each row and it's columns values")
    for row in db:
        if len(row[0])>42:
            fixedAddress="'"+(normalize_address(row[0]))+"'"  # pylint: disable=invalid-name
            query = 'update tbl_token_transfers set to_address = {} where id = {}'.format(fixedAddress,row[2])  # pylint: disable=invalid-name
            cursor.execute(query)
            connection.commit()
        if len(row[1])>42:
            fixedAddress="'"+(normalize_address(row[1]))+"'"  # pylint: disable=invalid-name
            query = 'update tbl_token_transfers set from_address = {} where id = {}'.format(fixedAddress,row[2])  # pylint: disable=invalid-name
            cursor.execute(query)
            connection.commit()
        else:
            pass
except (Exception, Error) as error:
    print("Error while connecting to PostgreSQL", error)
finally:
    if connection:
        cursor.close()
        connection.close()
        print("PostgreSQL connection is closed")

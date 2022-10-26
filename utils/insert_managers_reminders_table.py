#Importing necessary libraries
import psycopg2
import os

#Getting environment variables
PG_USERNAME = os.getenv('PG_USERNAME')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DB = os.getenv('PG_DB')

def insert_manager_on_reminders_table(manager):
    ''''
    Inserts manager on table of reminders.
    @param - manager => Dictionary with email and naame
    example: manager={"name":"John Doe","email":"john@doe.com"}
    '''

    try:
        #Connecting to PostgreeSQL
        connection = psycopg2.connect(user=PG_USERNAME,password=PG_PASSWORD,host=PG_HOST,port=PG_PORT ,database=PG_DB)
        cursor = connection.cursor()
        
        #Creating query to Insert a new manager with "email","name" and reminders count
        insert_query = f""" INSERT INTO public.lembrete_gerentes (email,nome,lembretes_enviados) 
        values ('{manager['email']}', '{manager['name']}' ,1);"""

        #Executing query
        cursor.execute(insert_query)

        #Persisting data on the db
        connection.commit()
    
    except (Exception, psycopg2.Error) as error:
        print("Failed to insert record into table", error)

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")
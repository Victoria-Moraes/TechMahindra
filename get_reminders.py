#Importing necessary libraries
import psycopg2
import os

#Getting environment variables
PG_USERNAME = os.getenv('PG_USERNAME')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DB = os.getenv('PG_DB')

def select_managers_to_be_reminded():
    ''''
   get a list of managers that need to be reminded.
    '''
    try:
        connection = psycopg2.connect(user=PG_USERNAME,
                                      password=PG_PASSWORD,
                                      host=PG_HOST,
                                      port=PG_PORT,
                                      database=PG_DB)

        cursor = connection.cursor()
        
        #Selecting managers who have less than three reminders.
        query = f""" SELECT EMAIL,lembretes_enviados FROM public.lembrete_gerentes WHERE lembretes_enviados<=3;"""
        cursor.execute(query)

        #Storing the results on variable
        records = cursor.fetchall()

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert query table", error)
        return 500

    finally:
        # closing database connection.
        if connection:
            #Persisting data on the db
            connection.commit()
            cursor.close()
            connection.close()
            return records

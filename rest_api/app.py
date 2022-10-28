# Importing necessary libraries
from email import utils
import os
import psycopg2
from crypt import methods
from operator import methodcaller
from flask_cors import CORS, cross_origin
from flask import Flask, request, abort

from utils.insert_managers_reminders_table import insert_manager_on_reminders_table

# Importing mail library
from flask_mail import Mail, Message

# Importing dotenv library
from dotenv import load_dotenv

# Loading Environment Variables
load_dotenv()


# Initializing Flask Application
app = Flask(__name__)

# Initializing mail application
mail = Mail(app)

# Enabling CORS
CORS(app, support_credentials=True)

# Configuring E-mail credentials
app.config['MAIL_SERVER'] = 'smtp.gmail.com'
app.config['MAIL_PORT'] = 465
app.config['MAIL_USERNAME'] = os.getenv('MAIL_USERNAME')
robot_email = app.config['MAIL_USERNAME']
app.config['MAIL_PASSWORD'] = os.getenv('MAIL_PASSWORD')
app.config['MAIL_USE_TLS'] = False
app.config['MAIL_USE_SSL'] = True
mail = Mail(app)

PG_USERNAME = os.getenv('PG_USERNAME')
PG_PASSWORD = os.getenv('PG_PASSWORD')
PG_HOST = os.getenv('PG_HOST')
PG_PORT = os.getenv('PG_PORT')
PG_DB = os.getenv('PG_DB')

# ====== Routes ======

# Index Route -  Test route


@app.route("/")
def hello_world():
    return "<p>Hello, World!</p>"

# POST Route for creating e-mails and adding them to the reminders list
@app.route("/api/v2/create_email", methods=['POST'])
def create_email():
    # Getting request data as JSON object
    data = request.get_json()

    # Getting relevant data.
    data = data['request']

    print(data)

    # Writing e-mail with necessary Data.
    text = f'''
            Dados do requisitante:\n
            Nome: {data['requester']['name']}
            Empresa: {data['requester']['empresa']}
            Centro de custo: {data['requester']['centro_de_custo']}
            Cargo: {data['requester']['cargo']}
            Matrícula: {data['requester']['matricula']}
            E-mail: {data['requester']['email']}
            Localidade: {data['requester']['localidade']}

            Dados do Funcionário:\n
            Nome: {data['employee']['name']}
            Matrícula: {data['employee']['cpf']}
            Fila: {data['employee']['fila']}
            '''

    #Creating mail object
    manager = {
        "name": data['requester']['name'],
        "email": data['requester']['email']
    }

    #Inserting manager on table of reminders
    insert_manager_on_reminders_table(manager)

    #Writing message
    msg = Message(data['subject'], sender=robot_email, recipients=[manager['email'], robot_email])
    msg.body = text
    mail.send(msg)
    return "Enviado", 200

#Get Route to remind managers about confirming their employees e-mail creation.
@app.route("/api/v2/remember_managers")
def remember_managers():

    subject = "Lembrete Aprovação E-mail para funcionário"

    reminder_message = """
                        Boa Tarde, Tudo bem?
                        Seu ticket foi enviado para o setor responsável e será avaliado. Entraremos em contato em breve.
                        Obrigada.

                        """

    #Connecting to DB
    try:
        connection = psycopg2.connect(user=PG_USERNAME,
                                      password=PG_PASSWORD,
                                      host=PG_HOST,
                                      port=PG_PORT,
                                      database=PG_DB)

        cursor = connection.cursor()

        #Selecting managers who have less than three reminders.
        query = f"""delete from public.lembrete_gerentes where lembretes_enviados>=3;"""
        cursor.execute(query)

        #Selecting managers who have less than three reminders.
        query = f""" SELECT EMAIL,lembretes_enviados FROM public.lembrete_gerentes WHERE lembretes_enviados<=3;"""
        cursor.execute(query)

        #Storing the results on variable
        records = cursor.fetchall()

        #Variable for counting how many e-mails were sent
        count = 0

        for manager in records:
            count = count + 1
            manager_email = manager[0]

            #Query for updating manager reminders count
            update_query = f""" update public.lembrete_gerentes SET lembretes_enviados = lembretes_enviados+1 where email='{manager_email}';"""
            
            #Executing Update query
            cursor.execute(update_query)

            #Sending message to manager
            msg = Message(subject, sender=robot_email, recipients=[manager[0], robot_email])
            msg.body = reminder_message
            mail.send(msg)

    except (Exception, psycopg2.Error) as error:
        print("Failed to insert query table", error)
        return "Internal Server Error", 500

    finally:
        # closing database connection.
        if connection:
            cursor.close()
            connection.close()
            print("PostgreSQL connection is closed")

    return f"{count} Ticket enviado", 200

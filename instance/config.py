import os

senha_do_banco = os.getenv('POSTGRES_PASSWORD')
database_host = os.getenv('POSTGRES_CONNECTION')
user_database = os.getenv('USER_DATABASE')

SECRET_KEY = 'pmk*44444**999n<<<<))((($$@@@#1'
SQLALCHEMY_DATABASE_URI = f'postgresql://postgres:{senha_do_banco}@{database_host}/{user_database}'
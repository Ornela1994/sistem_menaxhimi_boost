from pony.orm import delete, db_session, select
from app.modelet import User

class Factory:

    default_email = 'admin@spitali.com'
    default_username = 'admin'
    default_password = 'admin_test'
    default_date = '2021-01-01'

    @classmethod
    def setup(cls):
        cls.create_user()

    @classmethod
    @db_session
    def create_user(cls):
        new_user = User(email=cls.default_email, username=cls.default_username)
        new_user.set_password(cls.default_password)
        new_user.vendos_daten(cls.default_date)




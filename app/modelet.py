from pony.orm import *
from werkzeug.security import generate_password_hash, check_password_hash
from flask_login import UserMixin
from app import login
import datetime


db = Database()


class Punonjes(db.Entity):
    _table_ = 'punonjesit'
    id = PrimaryKey(int, auto=True)
    owner = Required("User", reverse="punonjesit")
    emer = Required(str)
    mbiemer = Required(str)
    pozicion = Required(str)
    paga_per_ore = Optional(int)
    data_regjistrimit = Optional(datetime.date)
    ore_pune = Optional(int)
    paga = Optional(int)

    @db_session
    def vendos_ore_pune(self, ore_pune):
        self.ore_pune = ore_pune

    @db_session
    def vendos_pagen(self):
        self.paga = self.ore_pune*self.paga_per_ore

    


class User(UserMixin, db.Entity):
    _table_ = 'users'
    email = Required(str, unique=True)
    username = Required(str, unique=True)
    password_hash = Optional(str)
    punonjesit = Set('Punonjes', reverse='owner')
    data = Optional(datetime.date)
    
    def __repr__(self):
        return '<User {}>'.format(self.username)
        
    def set_password(self, password):
        self.password_hash = generate_password_hash(password)
        
    def check_password(self, password):
        return check_password_hash(self.password_hash, password)

    @db_session
    def set_data_te_punonjesve(self, data):
        self.emer = data[0]
        self.mbiemer = data[1]
        self.pozicion= data[2]
        self.paga_per_ore = data[3]
        self.data_regjistrimit = data[4]

    @db_session
    def vendos_daten(self, data):
        self.data = data


  


@login.user_loader
@db_session
def load_user(id):
    try:
        return User.get(id=int(id))
    except:
        return

db.bind(provider='sqlite', filename='../dev.db', create_db=True)
db.generate_mapping(create_tables=True)

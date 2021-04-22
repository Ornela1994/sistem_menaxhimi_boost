import sys, os
from factory.factory import Factory
from app.modelet import db


def factory_setup():
        Factory.setup()

def manage():

    commands = {'up': factory_setup}

    if len(sys.argv) == 2:
        commands[sys.argv[1]]()


if __name__ == '__main__':
    manage()



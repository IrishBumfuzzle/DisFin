from os import stat
from time import sleep
import pypresence
from constants import APPLICATION_ID


def connect_presence():
    presence = pypresence.Presence(APPLICATION_ID)
    presence.connect()
    return presence

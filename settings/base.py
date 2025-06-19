import configparser
import pathlib

path = pathlib.Path(__file__).parent.joinpath('config.ini')

parser = configparser.ConfigParser()
parser.read(path)

HASH_ALGORITHM = parser.get('AUTH', 'HASH_ALGORITHM', fallback="HS256")
HASH_SECRET = parser.get('AUTH', 'HASH_SECRET', fallback="secret-key")
ACCESS_TOKEN_EXPIRE_MINUTES = parser.getint('AUTH', 'ACCESS_TOKEN_EXPIRE_MINUTES', fallback=30)
from .server import WebsocketServer
from src.db.main import create_pool
from src.db.dao import get_daos

vm_server = WebsocketServer(get_daos())

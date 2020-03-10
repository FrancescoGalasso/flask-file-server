# from app import app_file_server

from app import app_file_server, db
from app.models import User, ItemFile

# Uselfull using cmd *flask shell* for debug testing
@app_file_server.shell_context_processor
def make_shell_context():
    return {'db': db, 'User': User, 'ItemFile': ItemFile}

# usefull for the cmd *python flask_file_server.py*
app_file_server.run(host="0.0.0.0", port=5000)
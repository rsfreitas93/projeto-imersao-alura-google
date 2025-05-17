from flask import Flask

app = Flask(__name__)

from routes.views import *
from routes.agentes_ia import *

if __name__ == "__main__":
    app.run()
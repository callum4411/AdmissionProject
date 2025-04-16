from flask import Flask

app = Flask(__name__)
app.secret_key = 'your_secret_key_here'  # needed for session

from routes import *

if __name__ == '__main__':
    app.run(debug=True)

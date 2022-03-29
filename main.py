from flask import Flask
from markupsafe import escape
from google.oauth2 import service_account
from steps.reader import ReleaseReader
import pandas as pd

app = Flask(__name__)

credentials = service_account.Credentials.from_service_account_file('key.json')

@app.route('/')
def home():
    return '<p>Welcome to LoL Patch Predict API!</p>'

@app.route('/nextpatch', methods=['GET'])
def nextpatch_all():
    return {
        'buff': ['Aurelion Sol'],
        'nerf': ['Yasuo', 'Yone', 'Master Yi']
    }

@app.route('/nextpatch/<champion>', methods=['GET'])
def nextpatch(champion):
    champion = escape(champion)
    d = ReleaseReader.from_gbq(credentials, as_dict=True)
    if champion not in d:
        return f'Champion not found: {champion}', 400

    return {champion: 'buff'}

if __name__ == '__main__':
    app.run(debug=True)



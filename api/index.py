"""
Vercel Serverless Entry Point - Flask Minimal Test
"""
from flask import Flask

app = Flask(__name__)

@app.route('/')
@app.route('/api')
@app.route('/api/')
def hello():
    return 'Flask is working on Vercel!'

@app.route('/api/<path:path>')
def catch_all(path):
    return f'Flask caught: {path}'


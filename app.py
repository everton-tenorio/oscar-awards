from flask import Flask, render_template, jsonify
from pymongo import MongoClient
from flask_cors import CORS
from environs import Env

app = Flask(__name__)
CORS(app)

env = Env()
env.read_env()

# Conectar ao MongoDB
client = MongoClient(env('MONGODB_URI'))
db = client['oscar_database']

# Rotas
@app.route('/')
def index():
    return render_template('index.html')

@app.route('/vencedores/<ano>')
def vencedores(ano):
    # Consulta MongoDB para vencedores
    resultado = db.cerimonias_oscar.find_one({"ano": int(ano)})
    return jsonify(resultado['categorias']) if resultado else jsonify({})

@app.route('/nao_vencedores/<ano>')
def nao_vencedores(ano):
    # Consulta MongoDB para indicados não vencedores
    resultado = db.cerimonias_oscar_noindicados.find_one({"ano": int(ano)})
    return jsonify(resultado['categorias']) if resultado else jsonify({})

@app.route('/anos')
def obter_anos_disponiveis():
    # Consulta MongoDB para obter todos os anos disponíveis
    anos_disponiveis = db.cerimonias_oscar.distinct("ano")
    return jsonify(anos_disponiveis)

if __name__ == '__main__':
    app.run()

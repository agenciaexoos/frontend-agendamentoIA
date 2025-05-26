from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os

app = Flask(__name__)

# Configuração da URL da API
API_URL = os.environ.get('API_URL', 'http://localhost:8000')

@app.route('/')
def index():
    return redirect(url_for('admin_dashboard'))

@app.route('/admin')
def admin_dashboard():
    return render_template('admin/dashboard.html')

@app.route('/admin/especialidades')
def admin_especialidades():
    return render_template('admin/especialidades.html')

@app.route('/admin/servicos')
def admin_servicos():
    return render_template('admin/servicos.html')

@app.route('/admin/medicos')
def admin_medicos():
    return render_template('admin/medicos.html')

@app.route('/admin/agendamentos')
def admin_agendamentos():
    return render_template('admin/agendamentos.html')

@app.route('/quadro_horarios')
def quadro_horarios():
    return render_template('quadro_horarios.html')

# Rotas de proxy para a API com prefixo /api/
@app.route('/api/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(endpoint):
    url = f"{API_URL}/{endpoint}"
    
    # Encaminhar a requisição para a API
    if request.method == 'GET':
        response = requests.get(url, params=request.args)
    elif request.method == 'POST':
        response = requests.post(url, json=request.json)
    elif request.method == 'PUT':
        response = requests.put(url, json=request.json)
    elif request.method == 'DELETE':
        response = requests.delete(url)
    
    # Retornar a resposta da API
    return jsonify(response.json()), response.status_code

# Rotas de proxy diretas para a API (sem prefixo /api/)
@app.route('/especialidades', methods=['GET', 'POST'])
@app.route('/especialidades/<path:subpath>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/servicos', methods=['GET', 'POST'])
@app.route('/servicos/<path:subpath>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/medicos', methods=['GET', 'POST'])
@app.route('/medicos/<path:subpath>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/agendamentos', methods=['GET', 'POST'])
@app.route('/agendamentos/<path:subpath>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/horarios_disponiveis', methods=['GET'])
def api_proxy_direct(subpath=None):
    endpoint = request.path.lstrip('/')
    url = f"{API_URL}/{endpoint}"
    
    # Encaminhar a requisição para a API
    if request.method == 'GET':
        response = requests.get(url, params=request.args)
    elif request.method == 'POST':
        response = requests.post(url, json=request.json)
    elif request.method == 'PUT':
        response = requests.put(url, json=request.json)
    elif request.method == 'DELETE':
        response = requests.delete(url)
    
    # Retornar a resposta da API
    return jsonify(response.json()), response.status_code

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

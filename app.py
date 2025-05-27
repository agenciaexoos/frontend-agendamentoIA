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

# Rota específica para horarios_disponiveis
@app.route('/horarios_disponiveis', methods=['GET'])
def horarios_disponiveis_proxy():
    # Obter parâmetros da requisição
    params = request.args.to_dict()
    
    # Se não houver médico_id, carregar todos os médicos primeiro
    if 'medico_id' not in params:
        try:
            # Obter lista de médicos
            medicos_response = requests.get(f"{API_URL}/medicos")
            
            # Verificar se a resposta é um JSON válido
            try:
                medicos = medicos_response.json()
            except ValueError:
                print(f"Erro ao decodificar resposta de médicos: {medicos_response.text[:200]}")
                return jsonify({"error": "Erro ao obter lista de médicos"}), 500
            
            # Carregar horários para cada médico
            todos_horarios = []
            for medico in medicos:
                medico_params = {'medico_id': medico['id']}
                if 'data' in params:
                    medico_params['data'] = params['data']
                
                horarios_url = f"{API_URL}/agendamentos/horarios_disponiveis"
                print(f"Consultando horários para médico {medico['id']} em {horarios_url}")
                
                horarios_response = requests.get(horarios_url, params=medico_params)
                
                if horarios_response.status_code == 200:
                    try:
                        horarios_medico = horarios_response.json()
                        todos_horarios.extend(horarios_medico)
                    except ValueError:
                        print(f"Erro ao decodificar resposta de horários para médico {medico['id']}: {horarios_response.text[:200]}")
                else:
                    print(f"Erro ao obter horários para médico {medico['id']}: Status {horarios_response.status_code}")
            
            return jsonify(todos_horarios), 200
        except Exception as e:
            print(f"Erro ao acessar horarios_disponiveis para todos os médicos: {e}")
            return jsonify({"error": str(e)}), 500
    
    # Se houver médico_id, apenas repassar a requisição
    url = f"{API_URL}/agendamentos/horarios_disponiveis"
    try:
        print(f"Consultando horários com parâmetros específicos: {params}")
        response = requests.get(url, params=params)
        
        # Verificar se a resposta é um JSON válido
        try:
            json_data = response.json()
            return jsonify(json_data), response.status_code
        except ValueError:
            print(f"Erro ao decodificar resposta: {response.text[:200]}")
            return jsonify({"error": "Resposta inválida da API"}), 500
    except Exception as e:
        print(f"Erro ao acessar horarios_disponiveis com parâmetros específicos: {e}")
        return jsonify({"error": str(e)}), 500

# Rotas de proxy diretas para a API (sem prefixo /api/)
@app.route('/especialidades', methods=['GET', 'POST'])
@app.route('/especialidades/<path:subpath>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/servicos', methods=['GET', 'POST'])
@app.route('/servicos/<path:subpath>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/medicos', methods=['GET', 'POST'])
@app.route('/medicos/<path:subpath>', methods=['GET', 'PUT', 'DELETE'])
@app.route('/agendamentos', methods=['GET', 'POST'])
@app.route('/agendamentos/<path:subpath>', methods=['GET', 'PUT', 'DELETE'])
def api_proxy_direct(subpath=None):
    endpoint = request.path.lstrip('/')
    url = f"{API_URL}/{endpoint}"
    
    try:
        # Encaminhar a requisição para a API
        if request.method == 'GET':
            response = requests.get(url, params=request.args)
        elif request.method == 'POST':
            data = request.get_json(silent=True)
            response = requests.post(url, json=data)
        elif request.method == 'PUT':
            data = request.get_json(silent=True)
            response = requests.put(url, json=data)
        elif request.method == 'DELETE':
            response = requests.delete(url)
        
        # Verificar se a resposta é um JSON válido
        try:
            json_data = response.json()
            return jsonify(json_data), response.status_code
        except ValueError:
            # Se não for JSON válido, retornar o conteúdo como texto
            return response.text, response.status_code, {'Content-Type': 'text/plain'}
    
    except Exception as e:
        print(f"Erro no proxy direto: {e}")
        print(f"URL: {url}")
        return jsonify({"error": str(e)}), 500

# Rotas de proxy para a API com prefixo /api/
@app.route('/api/<path:endpoint>', methods=['GET', 'POST', 'PUT', 'DELETE'])
def api_proxy(endpoint):
    url = f"{API_URL}/{endpoint}"
    
    try:
        # Encaminhar a requisição para a API
        if request.method == 'GET':
            response = requests.get(url, params=request.args)
        elif request.method == 'POST':
            response = requests.post(url, json=request.json)
        elif request.method == 'PUT':
            response = requests.put(url, json=request.json)
        elif request.method == 'DELETE':
            response = requests.delete(url)
        
        # Verificar se a resposta é um JSON válido
        try:
            json_data = response.json()
            return jsonify(json_data), response.status_code
        except ValueError:
            # Se não for JSON válido, retornar o conteúdo como texto
            return response.text, response.status_code, {'Content-Type': 'text/plain'}
    
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000, debug=True)

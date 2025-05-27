from flask import Flask, render_template, request, redirect, url_for, jsonify
import requests
import os
import re
import json

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

# Rota para reservar agendamento
@app.route('/reservar', methods=['POST'])
def reservar_agendamento_proxy():
    # Obter dados do JSON enviado pelo frontend
    dados = request.get_json(silent=True)
    if not dados:
        print("ERRO: Nenhum dado JSON recebido na requisição")
        return jsonify({"error": "Dados inválidos"}), 400
    
    print(f"[DEBUG] Dados recebidos para reserva: {json.dumps(dados, indent=2)}")
    
    # Extrair os campos necessários do JSON e formatá-los conforme esperado pela API
    try:
        # Campos obrigatórios
        medico_id = int(dados.get('medico_id', 0))
        data = dados.get('data', '')
        hora = dados.get('hora', '')
        nome_cliente = dados.get('nome_cliente', '')
        telefone_cliente = dados.get('telefone_cliente', '')
        
        # Campo opcional
        servico_id = None
        if 'servico_id' in dados and dados['servico_id']:
            servico_id = int(dados['servico_id'])
        
        # Verificar campos obrigatórios
        if not medico_id or not data or not hora or not nome_cliente or not telefone_cliente:
            return jsonify({"error": "Campos obrigatórios ausentes"}), 400
        
        # Construir URL para a API
        url = f"{API_URL}/agendamentos"
        
        # Construir parâmetros no formato esperado pela API
        params = {
            'medico_id': medico_id,
            'data': data,
            'hora': hora,
            'nome_cliente': nome_cliente,
            'telefone_cliente': telefone_cliente
        }
        
        if servico_id:
            params['servico_id'] = servico_id
        
        print(f"[DEBUG] Enviando requisição para criar agendamento: {url}")
        print(f"[DEBUG] Parâmetros: {json.dumps(params, indent=2)}")
        
        # Tentar diferentes métodos de envio para a API
        # Método 1: Form data
        response1 = requests.post(url, data=params)
        if response1.status_code < 400:
            return jsonify(response1.json()), response1.status_code
        
        print(f"[DEBUG] Método 1 falhou. Status: {response1.status_code}")
        print(f"[DEBUG] Resposta: {response1.text[:500]}")
        
        # Método 2: Query string
        response2 = requests.post(url, params=params)
        if response2.status_code < 400:
            return jsonify(response2.json()), response2.status_code
        
        print(f"[DEBUG] Método 2 falhou. Status: {response2.status_code}")
        print(f"[DEBUG] Resposta: {response2.text[:500]}")
        
        # Método 3: JSON
        response3 = requests.post(url, json=params)
        if response3.status_code < 400:
            return jsonify(response3.json()), response3.status_code
        
        print(f"[DEBUG] Método 3 falhou. Status: {response3.status_code}")
        print(f"[DEBUG] Resposta: {response3.text[:500]}")
        
        # Se todos os métodos falharem, retornar o erro do primeiro método
        print(f"[DEBUG] Todos os métodos falharam. Retornando resposta do método 1.")
        
        try:
            return jsonify(response1.json()), response1.status_code
        except ValueError:
            return jsonify({"error": "Erro ao criar agendamento"}), response1.status_code
        
    except Exception as e:
        print(f"[DEBUG] Erro ao processar dados para reserva: {e}")
        return jsonify({"error": str(e)}), 500

# Rota específica para horarios_disponiveis/medico/<id>
@app.route('/horarios_disponiveis/medico/<int:medico_id>', methods=['GET'])
def horarios_disponiveis_medico_proxy(medico_id):
    # Obter parâmetros da requisição
    params = request.args.to_dict()
    
    # Adicionar medico_id aos parâmetros
    params['medico_id'] = medico_id
    
    # Garantir que a URL termine com barra
    url = f"{API_URL}/agendamentos/horarios_disponiveis/"
    try:
        print(f"Consultando horários para médico específico via URL RESTful: {medico_id}")
        print(f"URL completa: {url}")
        print(f"Parâmetros: {params}")
        
        response = requests.get(url, params=params)
        
        print(f"Status da resposta: {response.status_code}")
        print(f"Conteúdo da resposta: {response.text[:200]}")
        
        # Verificar se a resposta é um JSON válido
        try:
            json_data = response.json()
            return jsonify(json_data), response.status_code
        except ValueError:
            print(f"Erro ao decodificar resposta: {response.text[:200]}")
            return jsonify({"error": "Resposta inválida da API"}), 500
    except Exception as e:
        print(f"Erro ao acessar horarios_disponiveis/medico/{medico_id}: {e}")
        return jsonify({"error": str(e)}), 500

# Rota específica para horarios_disponiveis
@app.route('/horarios_disponiveis', methods=['GET'])
def horarios_disponiveis_proxy():
    # Obter parâmetros da requisição
    params = request.args.to_dict()
    
    # Se houver médico_id, apenas repassar a requisição
    if 'medico_id' in params:
        # Garantir que medico_id seja um inteiro
        try:
            medico_id = int(params['medico_id'])
            params['medico_id'] = medico_id  # Substituir com o valor inteiro
        except ValueError:
            print(f"Erro: medico_id não é um número válido: {params['medico_id']}")
            return jsonify({"error": "ID do médico inválido"}), 400
        
        # Garantir que a URL termine com barra
        url = f"{API_URL}/agendamentos/horarios_disponiveis/"
        try:
            print(f"Consultando horários para médico específico: {medico_id}")
            print(f"URL completa: {url}")
            print(f"Parâmetros: {params}")
            
            response = requests.get(url, params=params)
            
            print(f"Status da resposta: {response.status_code}")
            print(f"Conteúdo da resposta: {response.text[:200]}")
            
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
    
    # Se não houver médico_id, carregar todos os médicos e fazer chamadas individuais
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
            # Garantir que medico_id seja um inteiro
            try:
                medico_id = int(medico['id'])
            except (ValueError, TypeError):
                print(f"Erro: ID do médico não é um número válido: {medico['id']}")
                continue
            
            # Garantir que os parâmetros estejam corretos
            medico_params = {'medico_id': medico_id}
            
            # Adicionar data se estiver presente na requisição original
            if 'data' in params:
                medico_params['data'] = params['data']
            
            # Garantir que a URL termine com barra
            horarios_url = f"{API_URL}/agendamentos/horarios_disponiveis/"
            print(f"Consultando horários para médico {medico_id} em {horarios_url}")
            print(f"Parâmetros: {medico_params}")
            
            horarios_response = requests.get(horarios_url, params=medico_params)
            
            print(f"Status da resposta: {horarios_response.status_code}")
            print(f"Conteúdo da resposta: {horarios_response.text[:200]}")
            
            if horarios_response.status_code == 200:
                try:
                    horarios_medico = horarios_response.json()
                    todos_horarios.extend(horarios_medico)
                except ValueError:
                    print(f"Erro ao decodificar resposta de horários para médico {medico_id}: {horarios_response.text[:200]}")
            else:
                print(f"Erro ao obter horários para médico {medico_id}: Status {horarios_response.status_code}, Resposta: {horarios_response.text[:200]}")
        
        return jsonify(todos_horarios), 200
    except Exception as e:
        print(f"Erro ao acessar horarios_disponiveis para todos os médicos: {e}")
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

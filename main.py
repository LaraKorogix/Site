# app.py
from flask import Flask, render_template, request, redirect, url_for, jsonify
# Removido 'from datetime import datetime' pois não é mais usado diretamente aqui

from database import Database 

DATABASE_FILE = "petshop.db"
app = Flask(__name__)
app.secret_key = 'ae91a837b73d8267d03c035e9cfed45fe6652f55711db34b1d5a58d767f8783a'
db_manager = Database(DATABASE_FILE)


# --- Rotas Flask ---

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/login-cadastro')
def logincadastro():
    return render_template('login-cadastro.html')

@app.route('/cadastro')
def exibir_cadastro():
    return render_template('cadastro.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    nome = request.form.get('nome')
    email = request.form.get('email')
    celular = request.form.get('celular')
    # telefone = request.form.get('telefone') # Campo duplicado, usando celular
    genero = request.form.get('genero')
    data_nascimento = request.form.get('data_nascimento')
    cpf = request.form.get('cpf')
    senha = request.form.get('senha')

    if not all([nome, email, celular, cpf, senha]):
        print("Erro: Campos obrigatórios não preenchidos no registro.")
        # Adicionar flash message
        return redirect(url_for('exibir_cadastro'))

    if db_manager.cadastrar_cliente(nome, cpf, celular, email, genero, data_nascimento, senha):
        print(f"Novo cadastro (Flask POO): {nome}, {email}, {cpf}")
        # Adicionar flash message de sucesso
        return redirect(url_for('logincadastro'))
    else:
        print(f"Falha ao registrar usuário {cpf}.")
        # Adicionar flash message de erro
        return redirect(url_for('exibir_cadastro'))

@app.route('/home', endpoint = 'home' )
def home():
    agendamentos_db = db_manager.listar_agendamentos_detalhados()
    return render_template('home.html', agendamentos=agendamentos_db)

@app.route('/servico', endpoint = 'servico')
def servico_page():
    agendamentos_db = db_manager.listar_agendamentos_detalhados()
    pets_db = db_manager.listar_pets_simples()
    servicos_db = db_manager.listar_servicos() # Tipos de serviço
    return render_template('servicos.html', agendamentos=agendamentos_db, pets=pets_db, servicos=servicos_db)

@app.route('/cadastrar-servico', methods=['POST'], endpoint = 'cadastrar_servico')
def cadastrar_servico_agendamento():
    pet_id_str = request.form.get('pet_id')
    servico_id_str = request.form.get('servico_id')
    data = request.form.get('data') # Formato YYYY-MM-DD
    hora = request.form.get('hora') # Formato HH:MM

    # Validação de IDs e data/hora
    pet_id, servico_id = None, None
    try:
        if pet_id_str: pet_id = int(pet_id_str)
        if servico_id_str: servico_id = int(servico_id_str)
    except ValueError:
        print("Erro: ID de Pet ou Serviço inválido.")
        # Adicionar flash message
        return redirect(url_for('servico_page'))

    if not all([pet_id, servico_id, data, hora]):
        print("Erro: Campos obrigatórios não preenchidos para agendamento.")
        # Adicionar flash message
        return redirect(url_for('servico_page'))

    data_hora_str = f"{data} {hora}" # Formato "YYYY-MM-DD HH:MM"

    if db_manager.agendar_servico(pet_id, servico_id, data_hora_str):
        print(f"Serviço agendado via Flask POO para Pet ID {pet_id} em {data_hora_str}")
    else:
        print(f"Falha ao agendar serviço via Flask POO.")
        # Adicionar flash message de erro
    return redirect(url_for('servico_page'))


# --- Rotas para Vacinação (Agora usando o Banco de Dados) ---
@app.route('/vacina', endpoint = 'vacina')
def vacina_page():
    pets_db = db_manager.listar_pets_simples() # Para o dropdown de pets
    # Lista todos os registros de vacinas de todos os pets
    registros_vacinas_db = db_manager.listar_registros_vacinas() 
    return render_template('vacina.html', registros_vacinas=registros_vacinas_db, pets=pets_db)

@app.route('/cadastrar-vacina', methods=['POST'], endpoint = 'cadastrar_vacina')
def cadastrar_vacina_registro(): # Nome da função alterado para clareza
    pet_id_str = request.form.get('pet_id') # Assumindo que o form envia pet_id
    nome_vacina = request.form.get('vacina') # Nome/tipo da vacina
    data_aplicacao = request.form.get('data') # Formato YYYY-MM-DD
    proxima_data_aplicacao = request.form.get('proxima_data') # Formato YYYY-MM-DD, opcional

    pet_id = None
    if not pet_id_str: # Se o formulário ainda envia nome_pet em vez de pet_id
        nome_pet_form = request.form.get('nomePet')
        if nome_pet_form:
            pet_id = db_manager.buscar_pet_por_nome(nome_pet_form) # Busca o ID do pet pelo nome
        if not pet_id:
            print("Erro: Pet não encontrado ou não especificado para vacina.")
            # Adicionar flash message
            return redirect(url_for('vacina'))
    else:
        try:
            pet_id = int(pet_id_str)
        except ValueError:
            print("Erro: ID do Pet inválido para vacina.")
            # Adicionar flash message
            return redirect(url_for('vacina_page'))
            
    if not all([pet_id, nome_vacina, data_aplicacao]):
        print("Erro: Campos Pet, Nome da Vacina e Data de Aplicação são obrigatórios.")
        # Adicionar flash message
        return redirect(url_for('vacina_page'))

    if not proxima_data_aplicacao: # Se o campo vier vazio
        proxima_data_aplicacao = None

    if db_manager.cadastrar_registro_vacina(pet_id, nome_vacina, data_aplicacao, proxima_data_aplicacao):
        print(f"Registro de vacina '{nome_vacina}' para Pet ID {pet_id} cadastrado com sucesso.")
        # Considere também agendar o serviço "Aplicação de Vacina" se houver custo associado
        # Ex: db_manager.agendar_aplicacao_vacina(pet_id, f"{data_aplicacao} 09:00") # Agendar para uma hora padrão
    else:
        print(f"Falha ao cadastrar registro de vacina.")
        # Adicionar flash message
    return redirect(url_for('vacina_page'))

# --- Rotas para Pets e API ---
@app.route('/cadastro-pet', methods=['POST'], endpoint = 'cadastro-pet')
def cadastro_pet_json():
    data_req = request.get_json()
    nome_pet = data_req.get('nome_pet')
    especie = data_req.get('especie')
    raca = data_req.get('raca')
    try:
        if not nome_pet or not especie or not raca:
            return jsonify({'erro': 'Nome, espécie, raça e idade são obrigatórios'}), 400
        
        clientes = db_manager.listar_clientes()
        if not clientes:
            return jsonify({'erro': 'Nenhum cliente cadastrado. Cadastre um cliente antes de adicionar um pet.'}), 400
        cliente_id = clientes[0]['id']

        pet_id = db_manager.adicionar_pet(nome_pet, especie, raca, cliente_id, cliente_id)
        if pet_id:
            return jsonify({
                'mensagem': 'Pet cadastrado com sucesso', 'pet_id': pet_id,
                'nome_pet': nome_pet, 'especie': especie, 'raca': raca
            }), 200
        else:
            return jsonify({'erro': 'Falha ao cadastrar pet no banco de dados'}), 500
    except Exception as e:
        print(e)
        return jsonify({'erro': 'falhaaa'}), 400

@app.route('/api/pets', endpoint = 'api/pets')
def api_listar_pets():
    pets_db = db_manager.listar_pets_simples()
    return jsonify([dict(p) for p in pets_db])


if __name__ == '__main__':
    with app.app_context():
        db_manager.criar_tabelas()
        db_manager.popular_servicos_iniciais()
    app.run(debug=True)
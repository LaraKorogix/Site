from flask import Flask, render_template, request, redirect, url_for, jsonify

app = Flask(__name__)

# "Banco de dados" em memória
vacinas = []
agendamentos = []
pets = []

# Página inicial
@app.route('/')
def index():
    return render_template('index.html')

# Página de login/cadastro
@app.route('/login-cadastro')
def logincadastro():
    return render_template('login-cadastro.html')

# Página de formulário de cadastro
@app.route('/cadastro')
def exibir_cadastro():
    return render_template('cadastro.html')

# Processa cadastro de usuário
@app.route('/registrar', methods=['POST'])
def registrar():
    nome = request.form.get('nome')
    email = request.form.get('email')
    celular = request.form.get('celular')
    telefone = request.form.get('telefone')
    genero = request.form.get('genero')
    data_nascimento = request.form.get('data_nascimento')
    cpf = request.form.get('cpf')
    senha = request.form.get('senha')
    confirmar_senha = request.form.get('confirmar_senha')
    tipo = request.form.get('tipo')
    termos = request.form.get('termos')

    print(f"Novo cadastro: {nome}, {email}, {cpf}")
    return redirect(url_for('home'))

# Página principal
@app.route('/home')
def home():
    return render_template('home.html', agendamentos=agendamentos)

# Página de agendamento de serviços
@app.route('/servico')
def servico():
    return render_template('servicos.html', agendamentos=agendamentos, pets=pets)

# Cadastrar novo serviço
@app.route('/cadastrar-servico', methods=['POST'])
def cadastrar_servico():
    nome_pet = request.form.get('pet')
    servico = request.form.get('servico')
    data = request.form.get('data')
    hora = request.form.get('hora')

    novo_agendamento = {
        'nome_pet': nome_pet,
        'servico': servico,
        'data': data,
        'hora': hora
    }

    agendamentos.append(novo_agendamento)
    print(f"Serviço agendado: {novo_agendamento}")
    return redirect(url_for('servico'))

# Página de vacinação
@app.route('/vacina')
def vacina():
    return render_template('vacina.html', vacinas=vacinas, pets=pets)

# Cadastrar nova vacina
@app.route('/cadastrar-vacina', methods=['POST'])
def cadastrar_vacina():
    nome_pet = request.form.get('nomePet')
    tipo_vacina = request.form.get('vacina')
    data = request.form.get('data')
    proxima_data = request.form.get('proxima_data')

    nova_vacina = {
        'nome_pet': nome_pet,
        'vacina': tipo_vacina,
        'data': data,
        'proxima_data': proxima_data
    }

    vacinas.append(nova_vacina)
    print(f"Vacina cadastrada: {nova_vacina}")
    return redirect(url_for('vacina'))

# Cadastro de pet via modal (com JSON)
@app.route('/cadastro-pet', methods=['POST'])
def cadastro_pet():
    data = request.get_json()
    nome_pet = data.get('nome_pet')
    especie = data.get('especie')
    raca = data.get('raca')

    if not nome_pet or not especie or not raca:
        return jsonify({'erro': 'Todos os campos são obrigatórios'}), 400

    novo_pet = {
        'nome': nome_pet,
        'especie': especie,
        'raca': raca
    }

    pets.append(novo_pet)
    print(f"Pet cadastrado: {novo_pet}")
    return jsonify({'mensagem': 'Pet cadastrado com sucesso'}), 200

# Retorna lista de pets (para uso dinâmico se necessário)
@app.route('/api/pets')
def listar_pets():
    return jsonify(pets)

if __name__ == '__main__':
    app.run(debug=True)

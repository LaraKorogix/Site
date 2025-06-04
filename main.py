# main.py (ou app.py)
from flask import Flask, render_template, request, redirect, url_for, jsonify, session # Adicionado session
from database import Database 

DATABASE_FILE = "petshop.db"
app = Flask(__name__)
# Certifique-se que sua secret_key está configurada para usar sessions
app.secret_key = 'ae91a837b73d8267d03c035e9cfed45fe6652f55711db34b1d5a58d767f8783a' 
db_manager = Database(DATABASE_FILE)

# --- Rotas Flask ---

@app.route('/')
def index():
    return render_template('index.html')
@app.route('/set-test-session')
def set_test_session():
    session['test_key'] = 'Olá Mundo da Sessão!'
    session['user_role'] = 'admin_test'
    print(f"DEBUG: Rota /set-test-session - Dados da sessão definidos: {session.get('test_key')}, {session.get('user_role')}")
    return "Dados de teste definidos na sessão. Vá para /get-test-session para verificar."

@app.route('/get-test-session')
def get_test_session():
    test_value = session.get('test_key')
    role_value = session.get('user_role')
    print(f"DEBUG: Rota /get-test-session - 'test_key': {test_value}, 'user_role': {role_value}")
    return f"Valor de 'test_key' da sessão: {test_value}<br>Valor de 'user_role' da sessão: {role_value}"

@app.route('/clear-all-session-debug')
def clear_all_session_debug():
    session.clear() # Limpa toda a sessão
    print("DEBUG: Rota /clear-all-session-debug - Sessão limpa.")
    return "Toda a sessão foi limpa. Tente logar novamente."

# Exemplo de rota de login (MUITO SIMPLIFICADO - NÃO USE EM PRODUÇÃO)
@app.route('/login-simulado/<int:cliente_id_para_logar>')
def login_simulado(cliente_id_para_logar):
    # Adicione prints para depuração aqui também
    print(f"DEBUG: /login-simulado - Tentando logar cliente ID: {cliente_id_para_logar}")
    session['cliente_id'] = cliente_id_para_logar
    session['logged_in'] = True
    print(f"DEBUG: /login-simulado - Sessão definida: cliente_id={session.get('cliente_id')}, logged_in={session.get('logged_in')}")
    return redirect(url_for('home')) # ou 'servico_page' para testar diretamente

@app.route('/logout-simulado')
def logout_simulado():
    session.pop('cliente_id', None)
    session.pop('logged_in', None)
    return redirect(url_for('index'))

@app.route('/login-cadastro')
def logincadastro():
    return render_template('login-cadastro.html')

@app.route('/cadastro')
def exibir_cadastro():
    return render_template('cadastro.html')

@app.route('/registrar', methods=['POST'])
def registrar():
    # --- ESTA É A PARTE QUE PROVAVELMENTE ESTÁ FALTANDO OU INCOMPLETA ---
    nome = request.form.get('nome')
    email = request.form.get('email')
    celular = request.form.get('celular') 
    # Se você tem um campo 'telefone' separado e quer usá-lo, descomente:
    # telefone_form = request.form.get('telefone') 
    genero = request.form.get('genero')
    data_nascimento = request.form.get('data_nascimento')
    cpf = request.form.get('cpf')
    senha = request.form.get('senha')
    # --------------------------------------------------------------------

    # É uma boa prática validar se os campos essenciais foram preenchidos:
    if not all([nome, email, celular, cpf, senha]): # Verifique se 'celular' é o campo de telefone principal
        print("Erro: Campos obrigatórios não preenchidos no registro.")
        # Adicionar flash message para o usuário aqui seria ideal
        return redirect(url_for('exibir_cadastro'))

    # Agora as variáveis nome, cpf, email, etc., estão definidas
    # e podem ser usadas na chamada abaixo.
    # 'celular' está sendo usado como o telefone principal aqui.
    if db_manager.cadastrar_cliente(nome, cpf, celular, email, genero, data_nascimento, senha):
        print(f"Novo cadastro (Flask POO): {nome}, {email}, {cpf}")
        cliente_cadastrado_id = db_manager.buscar_cliente_id_por_cpf(cpf)
        if cliente_cadastrado_id:
            print(f"DEBUG: /registrar - Cliente ID {cliente_cadastrado_id} encontrado após cadastro.")
            session['cliente_id'] = cliente_cadastrado_id
            session['logged_in'] = True
            print(f"DEBUG: /registrar - Sessão definida: cliente_id={session.get('cliente_id')}, logged_in={session.get('logged_in')}")
        else:
            print(f"DEBUG: /registrar - Cliente ID NÃO encontrado após cadastro para CPF: {cpf}")
        return redirect(url_for('home'))
    else:
        # Este 'else' é acionado se db_manager.cadastrar_cliente retornar False (ex: CPF duplicado)
        print(f"Falha ao registrar usuário {cpf}. Pode ser CPF duplicado ou outro erro no DB.")
        # Adicionar flash message para o usuário aqui seria ideal
        return redirect(url_for('exibir_cadastro'))

@app.route('/home') # Removido endpoint='home' pois é o padrão
def home():
    agendamentos_do_cliente = []
    if session.get('logged_in') and session.get('cliente_id'):
        cliente_id_logado = session['cliente_id']
        # Usando o método modificado que filtra por cliente e retorna data/hora separadas
        agendamentos_do_cliente = db_manager.listar_agendamentos_detalhados(cliente_id=cliente_id_logado)
    else:
        # Opcional: redirecionar para login se não estiver logado
        # return redirect(url_for('logincadastro')) 
        print("Nenhum cliente logado para mostrar agendamentos na home.")
        # Ou pode mostrar uma mensagem "Faça login para ver seus agendamentos" no template

    # O template espera 'agendamentos'. Os dados já vêm formatados.
    # Se o template usa a.servico, e o DB retorna nome_servico, precisa alinhar.
    # Vamos preparar os dados para o template como ele espera:
    agendamentos_para_template = []
    for ag in agendamentos_do_cliente:
        agendamentos_para_template.append({
            'nome_pet': ag['nome_pet'],
            'servico': ag['nome_servico'], # Mapeando nome_servico para servico
            'data': ag['data'],
            'hora': ag['hora'],
            # Adicione outros campos se o template precisar
        })
    return render_template('home.html', agendamentos=agendamentos_para_template)


@app.route('/servico')
def servico_page():
    print(f"DEBUG: Acessando /servico")
    print(f"DEBUG: Sessão 'logged_in': {session.get('logged_in')}")
    print(f"DEBUG: Sessão 'cliente_id': {session.get('cliente_id')}")

    pets_do_cliente = []
    if session.get('logged_in') and session.get('cliente_id'):
        cliente_id_logado = session['cliente_id']
        print(f"DEBUG: Tentando buscar pets para cliente_id: {cliente_id_logado}")
        pets_do_cliente = db_manager.listar_pets_simples(cliente_id=cliente_id_logado)
        print(f"DEBUG: Pets encontrados para o cliente: {pets_do_cliente}")
    else:
        print("DEBUG: Cliente não logado ou sem cliente_id na sessão. Nenhum pet será listado.")
    
    servicos_db = db_manager.listar_servicos()
    
    # Supondo que você tem uma lógica para agendamentos_para_template
    agendamentos_do_cliente_atual = []
    if session.get('logged_in') and session.get('cliente_id'):
       agendamentos_do_cliente_atual = db_manager.listar_agendamentos_detalhados(cliente_id=session['cliente_id'])
    
    agendamentos_para_template_atual = []
    for ag_atual in agendamentos_do_cliente_atual:
        agendamentos_para_template_atual.append({
            'nome_pet': ag_atual['nome_pet'],
            'servico': ag_atual['nome_servico'],
            'data': ag_atual['data'],
            'hora': ag_atual['hora'],
        })

    return render_template('servicos.html', 
                           agendamentos=agendamentos_para_template_atual, 
                           pets=pets_do_cliente, 
                           servicos=servicos_db)

@app.route('/cadastrar-servico', methods=['POST'])
def cadastrar_servico_agendamento():
    print(f"--- DEBUG INÍCIO /cadastrar-servico ---")
    print(f"Conteúdo do formulário recebido (request.form): {request.form}") # Veja tudo que o form enviou

    if not session.get('logged_in') or not session.get('cliente_id'):
        print("DEBUG: Usuário não logado, redirecionando para login.")
        # flash("Faça login para agendar um serviço.", "warning") # Se estiver usando flash messages
        return redirect(url_for('logincadastro')) 
    
    pet_id_str = request.form.get('pet_id')
    servico_id_str = request.form.get('servico_id')
    data = request.form.get('data') 
    hora = request.form.get('hora')
    print(f"DEBUG: Dados brutos do form: pet_id_str='{pet_id_str}', servico_id_str='{servico_id_str}', data='{data}', hora='{hora}'")

    pet_id, servico_id = None, None
    try:
        if pet_id_str and pet_id_str.strip(): # Verifica se não é None e não é só espaço
            pet_id = int(pet_id_str)
        if servico_id_str and servico_id_str.strip():
            servico_id = int(servico_id_str)
        print(f"DEBUG: IDs convertidos: pet_id={pet_id}, servico_id={servico_id}")
    except ValueError:
        print("DEBUG ERROR: Falha ao converter pet_id ou servico_id para inteiro.")
        # flash("ID de Pet ou Serviço inválido.", "error")
        return redirect(url_for('servico_page')) # Use o nome da função da sua rota de serviços

    # Validação dos campos
    if not all([pet_id, servico_id, data, hora]):
        print(f"DEBUG ERROR: Validação 'not all' falhou. Um ou mais campos são None ou vazios após processamento.")
        print(f"Detalhes: pet_id={pet_id}, servico_id={servico_id}, data='{data}', hora='{hora}'")
        # flash("Todos os campos (Pet, Serviço, Data, Hora) são obrigatórios.", "error")
        return redirect(url_for('servico_page')) # Use o nome da função da sua rota de serviços

    data_hora_str = f"{data} {hora}" # Ex: "2024-06-03 14:30"
    print(f"DEBUG: String data_hora_str para o DB: '{data_hora_str}'")

    if db_manager.agendar_servico(pet_id, servico_id, data_hora_str):
        print(f"DEBUG: db_manager.agendar_servico retornou SUCESSO.")
        # flash("Serviço agendado com sucesso!", "success")
    else:
        print(f"DEBUG ERROR: db_manager.agendar_servico retornou FALHA.")
        # flash("Falha ao agendar o serviço. Verifique os dados ou tente mais tarde.", "error")
    
    print(f"--- DEBUG FIM /cadastrar-servico ---")
    return redirect(url_for('servico_page')) # Use o nome da função da sua rota de serviços


# --- Rotas para Vacinação (Agora usando o Banco de Dados) ---
@app.route('/vacina') # Removido endpoint
def vacina_page():
    pets_do_cliente = []
    registros_vacinas_do_cliente = []

    if session.get('logged_in') and session.get('cliente_id'):
        cliente_id_logado = session['cliente_id']
        pets_do_cliente = db_manager.listar_pets_simples(cliente_id=cliente_id_logado)
        
        # Listar vacinas apenas dos pets do cliente logado
        # Precisamos iterar pelos pets do cliente e buscar as vacinas de cada um
        # ou modificar listar_registros_vacinas para aceitar cliente_id e fazer o JOIN.
        # Por ora, vamos buscar por pet_id se um pet for selecionado, ou todas do cliente.
        # Para simplificar, vamos listar todas do cliente por enquanto.
        # Esta query em `listar_registros_vacinas` já faz JOIN com pets, então podemos adaptar
        # `listar_registros_vacinas` para também aceitar `cliente_id`.
        # (Vou assumir que você adaptaria `listar_registros_vacinas` ou faria um loop)

        # Exemplo simples: listar vacinas de todos os pets do cliente logado
        lista_pets_cliente = db_manager.listar_pets_simples(cliente_id=cliente_id_logado)
        for pet in lista_pets_cliente:
            vacinas_pet = db_manager.listar_registros_vacinas(pet_id=pet['id'])
            registros_vacinas_do_cliente.extend(vacinas_pet)
            
    return render_template('vacina.html', registros_vacinas=registros_vacinas_do_cliente, pets=pets_do_cliente)


@app.route('/cadastrar-vacina', methods=['POST']) # Removido endpoint
def cadastrar_vacina_registro():
    if not session.get('logged_in') or not session.get('cliente_id'):
        return redirect(url_for('logincadastro'))
    
    cliente_id_logado = session['cliente_id']

    pet_id_str = request.form.get('pet_id') 
    nome_vacina = request.form.get('vacina')
    data_aplicacao = request.form.get('data')
    proxima_data_aplicacao = request.form.get('proxima_data')

    pet_id = None
    try:
        if pet_id_str: pet_id = int(pet_id_str)
    except ValueError:
        print("Erro: ID do Pet inválido para vacina.")
        return redirect(url_for('vacina_page')) # Usar nome da função
            
    if not all([pet_id, nome_vacina, data_aplicacao]):
        print("Erro: Campos Pet, Nome da Vacina e Data de Aplicação são obrigatórios.")
        return redirect(url_for('vacina_page'))

    # Adicional: Verificar se o pet_id pertence ao cliente_id_logado
    # (Lógica similar à de agendamento de serviço)

    if not proxima_data_aplicacao:
        proxima_data_aplicacao = None

    if db_manager.cadastrar_registro_vacina(pet_id, nome_vacina, data_aplicacao, proxima_data_aplicacao):
        print(f"Registro de vacina '{nome_vacina}' para Pet ID {pet_id} cadastrado.")
    else:
        print(f"Falha ao cadastrar registro de vacina.")
    return redirect(url_for('vacina_page')) # Usar nome da função

# --- Rotas para Pets e API ---
@app.route('/cadastro-pet', methods=['POST'])
def cadastro_pet_json():
    cliente_id_para_pet = None
    if session.get('logged_in') and session.get('cliente_id'):
        cliente_id_para_pet = session['cliente_id']
    else:
        clientes = db_manager.listar_clientes()
        if not clientes:
            return jsonify({'erro': 'Nenhum cliente base cadastrado. Operação de cadastro de pet não pode prosseguir.'}), 400 # Mensagem mais clara
        cliente_id_para_pet = clientes[0]['id'] # Usando o primeiro cliente como fallback

    data_req = request.get_json()
    if not data_req:
        return jsonify({'erro': 'Requisição JSON inválida ou vazia.'}), 400
        
    nome_pet = data_req.get('nome_pet')
    especie = data_req.get('especie')
    raca = data_req.get('raca')
    idade_str = data_req.get('idade') # Continuamos pegando, mas agora é opcional

    idade = None # Default para idade

    # Validação dos campos obrigatórios (sem idade)
    if not nome_pet or not especie or not raca:
        return jsonify({'erro': 'Nome, espécie e raça são obrigatórios.'}), 400
    
    try:
        # Tenta converter idade apenas se fornecida e não for uma string vazia
        if idade_str and idade_str.strip(): # .strip() para remover espaços em branco
            idade = int(idade_str)
        
        # Chamada para adicionar_pet agora passa 'idade' que pode ser None
        # A ordem dos parâmetros no método adicionar_pet é (nome, especie, raca, cliente_id, idade=None)
        pet_id = db_manager.adicionar_pet(nome_pet, especie, raca, cliente_id_para_pet, idade=idade)
        
        if pet_id:
            pet_cadastrado = {
                'mensagem': 'Pet cadastrado com sucesso', 
                'pet_id': pet_id,
                'nome_pet': nome_pet, 
                'especie': especie, 
                'raca': raca
            }
            if idade is not None: # Adiciona idade ao response apenas se ela foi processada
                pet_cadastrado['idade'] = idade
            return jsonify(pet_cadastrado), 200
        else:
            # Este erro ocorreria se db_manager.adicionar_pet retornasse None (ex: exceção no DB)
            return jsonify({'erro': 'Falha ao cadastrar pet no banco de dados.'}), 500
            
    except ValueError: # Se idade_str for fornecido mas não for um número válido
        return jsonify({'erro': 'Idade, se fornecida, deve ser um número válido.'}), 400
    except Exception as e:
        print(f"Erro inesperado no cadastro de pet JSON: {e}")
        # Log detalhado do erro no servidor é importante aqui
        # import traceback
        # print(traceback.format_exc())
        return jsonify({'erro': 'Falha interna ao processar o cadastro do pet.'}), 500


@app.route('/api/pets')
def api_listar_pets():
    cliente_id_query = request.args.get('cliente_id')
    pets_db = []
    if cliente_id_query:
        try:
            pets_db = db_manager.listar_pets_simples(cliente_id=int(cliente_id_query))
        except ValueError:
            pets_db = db_manager.listar_pets_simples() # Fallback para todos se ID inválido
    else:
         pets_db = db_manager.listar_pets_simples()
    return jsonify([dict(p) for p in pets_db])


if __name__ == '__main__':
    with app.app_context():
        db_manager.criar_tabelas()
        db_manager.popular_servicos_iniciais()
    app.run(debug=True)
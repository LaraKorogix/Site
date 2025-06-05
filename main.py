from flask import Flask, render_template, request, redirect, url_for, jsonify, session # Session para gerenciamento de login
from database import Database 

from flask import Flask # ... and other imports
from database import Database # Your updated database.py

# Replace with your actual MySQL credentials and database name
MYSQL_HOST = "localhost"  # Or your MySQL server IP/hostname
MYSQL_USER = "root"
MYSQL_PASSWORD = "ceub123456"
MYSQL_DATABASE = "petshop_db" # The database name you want to use/create

app = Flask(__name__)
app.secret_key = 'ae91a837b73d8267d03c035e9cfed45fe6652f55711db34b1d5a58d767f8783a' 

# Instantiate Database with MySQL credentials
db_manager = Database(
    host=MYSQL_HOST,
    user=MYSQL_USER,
    password=MYSQL_PASSWORD,
    database_name=MYSQL_DATABASE
)

# == Bloco Principal de Rotas da Aplicação ==

# Rota inicial, exibe a página principal.
@app.route('/')
def index():
    return render_template('index.html')

# == Rotas de Teste e Depuração de Sessão (Desenvolvimento) ==

# Define valores na sessão para facilitar testes.
@app.route('/set-test-session')
def set_test_session():
    session['test_key'] = 'Olá Mundo da Sessão!'
    session['user_role'] = 'admin_test'
    print(f"DEBUG: Rota /set-test-session - Dados da sessão definidos: {session.get('test_key')}, {session.get('user_role')}")
    return "Dados de teste definidos na sessão. Vá para /get-test-session para verificar."

# Recupera e exibe valores da sessão para verificação.
@app.route('/get-test-session')
def get_test_session():
    test_value = session.get('test_key')
    role_value = session.get('user_role')
    print(f"DEBUG: Rota /get-test-session - 'test_key': {test_value}, 'user_role': {role_value}")
    return f"Valor de 'test_key' da sessão: {test_value}<br>Valor de 'user_role' da sessão: {role_value}"

# Limpa todos os dados da sessão (útil para forçar novo login em testes).
@app.route('/clear-all-session-debug')
def clear_all_session_debug():
    session.clear() 
    print("DEBUG: Rota /clear-all-session-debug - Sessão limpa.")
    return "Toda a sessão foi limpa. Tente logar novamente."

# == Rotas de Simulação de Login/Logout (Desenvolvimento) ==

# Define um cliente como logado para fins de teste rápido.
@app.route('/login-simulado/<int:cliente_id_para_logar>')
def login_simulado(cliente_id_para_logar):
    print(f"DEBUG: /login-simulado - Tentando logar cliente ID: {cliente_id_para_logar}")
    session['cliente_id'] = cliente_id_para_logar
    session['logged_in'] = True
    print(f"DEBUG: /login-simulado - Sessão definida: cliente_id={session.get('cliente_id')}, logged_in={session.get('logged_in')}")
    return redirect(url_for('home')) # Ou redirecionar para 'servico_page' para testes diretos

# Desconecta o cliente simulado, limpando dados da sessão.
@app.route('/logout-simulado')
def logout_simulado():
    session.pop('cliente_id', None)
    session.pop('logged_in', None)
    return redirect(url_for('index'))

# == Rotas de Autenticação e Cadastro de Clientes ==

# Exibe a página combinada de login e opções de cadastro.
@app.route('/login-cadastro')
def logincadastro():
    return render_template('login-cadastro.html')

# Exibe o formulário de cadastro de novo cliente.
@app.route('/cadastro')
def exibir_cadastro():
    return render_template('cadastro.html')

# Processa os dados do formulário de registro de novo cliente.
@app.route('/registrar', methods=['POST'])
def registrar():
    nome = request.form.get('nome')
    email = request.form.get('email')
    celular = request.form.get('celular') 
    # NOTA: Campo 'telefone' (separado de celular) pode ser descomentado e usado se necessário.
    genero = request.form.get('genero')
    data_nascimento = request.form.get('data_nascimento')
    cpf = request.form.get('cpf')
    senha = request.form.get('senha')
    # --------------------------------------------------------------------

    # Validação básica: verifica se campos cruciais foram enviados.
    if not all([nome, email, celular, cpf, senha]): # 'celular' usado como telefone principal.
        print("Erro: Campos obrigatórios não preenchidos no registro.")
        # TODO: Implementar mensagens flash para feedback ao usuário aqui.
        return redirect(url_for('exibir_cadastro'))

    # Variáveis do formulário prontas para uso no cadastro.
    # 'celular' é o contato telefônico principal nesta lógica.
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
        # Falha no cadastro (ex: CPF já existe ou outro erro de banco).
        print(f"Falha ao registrar usuário {cpf}. Pode ser CPF duplicado ou outro erro no DB.")
        # TODO: Implementar mensagens flash para informar o usuário sobre o erro.
        return redirect(url_for('exibir_cadastro'))

# == Rota da Página Inicial do Usuário (Pós-Login) ==

# Rota da página principal do usuário logado (dashboard).
@app.route('/home') 
def home():
    agendamentos_do_cliente = []
    if session.get('logged_in') and session.get('cliente_id'):
        cliente_id_logado = session['cliente_id']
        # Busca agendamentos detalhados do cliente, com data/hora já separados.
        agendamentos_do_cliente = db_manager.listar_agendamentos_detalhados(cliente_id=cliente_id_logado)
    else:
        # Comportamento se não logado: atualmente mostra home vazia.
        # Poderia redirecionar para 'logincadastro' ou exibir mensagem no template.
        print("Nenhum cliente logado para mostrar agendamentos na home.")
        # NOTA: Template home.html deve tratar o caso de não haver agendamentos.

    # Prepara os dados de agendamento para o formato esperado pelo template home.html.
    # Ajuste de nome de campo: 'nome_servico' (BD) para 'servico' (template).
    agendamentos_para_template = []
    for ag in agendamentos_do_cliente:
        agendamentos_para_template.append({
            'nome_pet': ag['nome_pet'], # type: ignore
            'servico': ag['nome_servico'], # Mapeamento realizado # type: ignore
            'data': ag['data'], # type: ignore
            'hora': ag['hora'], # type: ignore
            # TODO: Verificar se o template home.html necessita de mais campos aqui.
        })
    return render_template('home.html', agendamentos=agendamentos_para_template)

# == Rotas de Agendamento de Serviços ==

# Exibe a página de agendamento de serviços, listando pets do cliente e serviços disponíveis.
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
    
    servicos_db = db_manager.listar_servicos() # Lista todos os serviços disponíveis
    
    # Carrega agendamentos existentes do cliente para exibição na página de serviços.
    agendamentos_do_cliente_atual = []
    if session.get('logged_in') and session.get('cliente_id'):
       agendamentos_do_cliente_atual = db_manager.listar_agendamentos_detalhados(cliente_id=session['cliente_id'])
    
    agendamentos_para_template_atual = [] # Formatação para o template de serviços
    for ag_atual in agendamentos_do_cliente_atual:
        agendamentos_para_template_atual.append({
            'nome_pet': ag_atual['nome_pet'],# type: ignore
            'servico': ag_atual['nome_servico'],# type: ignore
            'data': ag_atual['data'],# type: ignore
            'hora': ag_atual['hora'], # type: ignore
        })

    return render_template('servicos.html', 
                           agendamentos=agendamentos_para_template_atual, 
                           pets=pets_do_cliente, 
                           servicos=servicos_db)

# Processa o formulário de novo agendamento de serviço.
@app.route('/cadastrar-servico', methods=['POST'])
def cadastrar_servico_agendamento():
    print(f"--- DEBUG INÍCIO /cadastrar-servico ---")
    print(f"Conteúdo do formulário recebido (request.form): {request.form}") # Log dos dados brutos.

    if not session.get('logged_in') or not session.get('cliente_id'):
        print("DEBUG: Usuário não logado, redirecionando para login.")
        # TODO: Adicionar mensagens flash para "Faça login para agendar".
        return redirect(url_for('logincadastro')) 
    
    pet_id_str = request.form.get('pet_id')
    servico_id_str = request.form.get('servico_id')
    data = request.form.get('data') 
    hora = request.form.get('hora')
    print(f"DEBUG: Dados brutos do form: pet_id_str='{pet_id_str}', servico_id_str='{servico_id_str}', data='{data}', hora='{hora}'")

    pet_id, servico_id = None, None
    try:
        # Validação e conversão dos IDs de pet e serviço.
        if pet_id_str and pet_id_str.strip(): 
            pet_id = int(pet_id_str)
        if servico_id_str and servico_id_str.strip():
            servico_id = int(servico_id_str)
        print(f"DEBUG: IDs convertidos: pet_id={pet_id}, servico_id={servico_id}")
    except ValueError:
        print("DEBUG ERROR: Falha ao converter pet_id ou servico_id para inteiro.")
        # TODO: Adicionar mensagens flash para "ID de Pet ou Serviço inválido".
        return redirect(url_for('servico_page')) # Redireciona para a pág. de serviços.

    # Garante que todos os dados necessários para o agendamento foram fornecidos.
    if not all([pet_id, servico_id, data, hora]):
        print(f"DEBUG ERROR: Validação 'not all' falhou. Um ou mais campos são None ou vazios após processamento.")
        print(f"Detalhes: pet_id={pet_id}, servico_id={servico_id}, data='{data}', hora='{hora}'")
        # TODO: Adicionar mensagens flash para "Todos os campos são obrigatórios".
        return redirect(url_for('servico_page')) 

    data_hora_str = f"{data} {hora}" # Concatena data e hora para o formato do DB (ex: "2024-06-03 14:30").
    print(f"DEBUG: String data_hora_str para o DB: '{data_hora_str}'")

    if db_manager.agendar_servico(pet_id, servico_id, data_hora_str):
        print(f"DEBUG: db_manager.agendar_servico retornou SUCESSO.")
        # TODO: Adicionar mensagens flash para "Serviço agendado com sucesso!".
    else:
        print(f"DEBUG ERROR: db_manager.agendar_servico retornou FALHA.")
        # TODO: Adicionar mensagens flash para "Falha ao agendar o serviço".
    
    print(f"--- DEBUG FIM /cadastrar-servico ---")
    return redirect(url_for('servico_page')) # Redireciona para a pág. de serviços.

# == Rotas para Gerenciamento de Vacinação de Pets ==

# Exibe a página de registros de vacinação, com pets do cliente.
@app.route('/vacina') 
def vacina_page():
    pets_do_cliente = []
    registros_vacinas_do_cliente = []

    if session.get('logged_in') and session.get('cliente_id'):
        cliente_id_logado = session['cliente_id']
        pets_do_cliente = db_manager.listar_pets_simples(cliente_id=cliente_id_logado)
        
        # Busca pets do cliente e seus respectivos registros de vacina.
        # Lógica atual: itera pelos pets e busca vacinas para cada um.
        # OTIMIZAÇÃO POSSÍVEL: Modificar `listar_registros_vacinas` para aceitar `cliente_id`
        # e fazer um JOIN, buscando todas as vacinas dos pets do cliente de uma vez.
        # SUGESTÃO: Adaptar `listar_registros_vacinas` para filtrar por `cliente_id` diretamente.
        # (A implementação atual itera e agrega)
        for pet in pets_do_cliente: # Usando a lista já buscada
            vacinas_pet = db_manager.listar_registros_vacinas(pet_id=pet['id']) # type: ignore
            registros_vacinas_do_cliente.extend(vacinas_pet)
            
    return render_template('vacina.html', registros_vacinas=registros_vacinas_do_cliente, pets=pets_do_cliente)

# Processa o formulário de novo registro de vacina.
@app.route('/cadastrar-vacina', methods=['POST'])
def cadastrar_vacina_registro():
    if not session.get('logged_in') or not session.get('cliente_id'):
        return redirect(url_for('logincadastro'))
    
    cliente_id_logado = session['cliente_id'] # Pode ser usado para validação de propriedade do pet

    pet_id_str = request.form.get('pet_id') 
    nome_vacina = request.form.get('vacina')
    data_aplicacao = request.form.get('data')
    proxima_data_aplicacao = request.form.get('proxima_data')

    pet_id = None
    try:
        if pet_id_str: pet_id = int(pet_id_str)
    except ValueError:
        print("Erro: ID do Pet inválido para vacina.")
        # TODO: Flash message de erro.
        return redirect(url_for('vacina_page')) # Redireciona para a página de vacinas.
            
    if not all([pet_id, nome_vacina, data_aplicacao]):
        print("Erro: Campos Pet, Nome da Vacina e Data de Aplicação são obrigatórios.")
        # TODO: Flash message de erro.
        return redirect(url_for('vacina_page'))

    # TODO: Validar se o pet_id pertence ao cliente_id_logado (importante para segurança).

    if not proxima_data_aplicacao: # Permite próxima data ser opcional
        proxima_data_aplicacao = None

    if db_manager.cadastrar_registro_vacina(pet_id, nome_vacina, data_aplicacao, proxima_data_aplicacao):
        print(f"Registro de vacina '{nome_vacina}' para Pet ID {pet_id} cadastrado.")
        # TODO: Flash message de sucesso.
    else:
        print(f"Falha ao cadastrar registro de vacina.")
        # TODO: Flash message de erro.
    return redirect(url_for('vacina_page')) # Redireciona para a página de vacinas.

# == Rotas de Gerenciamento de Pets (incluindo API JSON) ==

# Endpoint JSON para cadastrar um novo pet via requisição POST.
@app.route('/cadastro-pet', methods=['POST'])
def cadastro_pet_json():
    cliente_id_para_pet = None
    if session.get('logged_in') and session.get('cliente_id'):
        cliente_id_para_pet = session['cliente_id']
    else:
        # Fallback se não houver cliente logado: tenta usar o primeiro cliente da base.
        # Isso pode ser útil para cenários de admin ou testes iniciais sem login.
        clientes = db_manager.listar_clientes()
        if not clientes:
            return jsonify({'erro': 'Nenhum cliente base cadastrado. Cadastro de pet não pode prosseguir.'}), 400
        cliente_id_para_pet = clientes[0]['id'] # type: ignore

    data_req = request.get_json()
    if not data_req:
        return jsonify({'erro': 'Requisição JSON inválida ou vazia.'}), 400
        
    nome_pet = data_req.get('nome_pet')
    especie = data_req.get('especie')
    raca = data_req.get('raca')
    idade_str = data_req.get('idade') # Idade é opcional.

    idade = None # Inicializa 'idade' como None.

    # Validação dos campos essenciais para o pet.
    if not nome_pet or not especie or not raca:
        return jsonify({'erro': 'Nome, espécie e raça são obrigatórios.'}), 400
    
    try:
        # Processa 'idade' se fornecida e for uma string não vazia.
        if idade_str and idade_str.strip(): # .strip() remove espaços em branco.
            idade = int(idade_str)
        
        # O método adicionar_pet() aceita 'idade' como None.
        # Assinatura do método: adicionar_pet(nome, especie, raca, cliente_id, idade=None)
        pet_id = db_manager.adicionar_pet(nome_pet, especie, raca, cliente_id_para_pet, idade=idade)
        
        if pet_id:
            pet_cadastrado = {
                'mensagem': 'Pet cadastrado com sucesso', 
                'pet_id': pet_id,
                'nome_pet': nome_pet, 
                'especie': especie, 
                'raca': raca
            }
            if idade is not None: # Inclui 'idade' na resposta JSON se tiver sido definida.
                pet_cadastrado['idade'] = idade
            return jsonify(pet_cadastrado), 200
        else:
            # Trata falha no db_manager.adicionar_pet (ex: erro de banco de dados).
            return jsonify({'erro': 'Falha ao cadastrar pet no banco de dados.'}), 500
            
    except ValueError: # Se 'idade_str' for fornecido mas não for um número válido.
        return jsonify({'erro': 'Idade, se fornecida, deve ser um número válido.'}), 400
    except Exception as e:
        print(f"Erro inesperado no cadastro de pet JSON: {e}")
        # IMPORTANTE: Logar exceções detalhadas no servidor é crucial aqui.
        # import traceback
        # print(traceback.format_exc()) # Para depuração mais profunda de exceções.
        return jsonify({'erro': 'Falha interna ao processar o cadastro do pet.'}), 500

# Endpoint API para listar pets. Suporta filtro por 'cliente_id' via query param.
@app.route('/api/pets')
def api_listar_pets():
    cliente_id_query = request.args.get('cliente_id')
    pets_db = []
    if cliente_id_query:
        try:
            pets_db = db_manager.listar_pets_simples(cliente_id=int(cliente_id_query))
        except ValueError:
            # Se cliente_id inválido na query, lista todos os pets como fallback.
            pets_db = db_manager.listar_pets_simples() 
    else:
        pets_db = db_manager.listar_pets_simples() # Lista todos se nenhum cliente_id for fornecido.
    return jsonify([dict(p) for p in pets_db]) # Converte cada linha do BD (Row) para dict. # type: ignore

# == Inicialização da Aplicação e Configurações do Banco de Dados ==

if __name__ == '__main__':
    # Garante que operações de DB (criar tabelas, popular) ocorram no contexto da aplicação Flask.
    with app.app_context():
        db_manager.criar_tabelas() # Cria as tabelas do banco de dados se não existirem.
        db_manager.popular_servicos_iniciais() # Popula dados iniciais (ex: lista de serviços padrão).
    app.run(debug=True) # Inicia o servidor de desenvolvimento Flask com modo debug ativo.
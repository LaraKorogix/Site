import sqlite3
from datetime import datetime

class Database:
    def __init__(self, db_file):
        self.db_file = db_file

    def _get_db_conn(self):
        conn = sqlite3.connect(self.db_file)
        conn.row_factory = sqlite3.Row
        return conn

    def criar_tabelas(self):
        conn = self._get_db_conn()
        cursor = conn.cursor()

        # Tabela Clientes (mantida da versão anterior)
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            cpf VARCHAR(14) UNIQUE NOT NULL,
            telefone VARCHAR(20),
            email VARCHAR(100),
            genero VARCHAR(20),
            data_nascimento VARCHAR(10),
            senha VARCHAR(100) 
        )''')

        # Tabela Pets (mantida da versão anterior)
        cursor.execute('''CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            especie VARCHAR(100) NOT NULL,
            raca VARCHAR(100) NOT NULL,
            idade INTEGER,
            cliente_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )''')

        # Tabela Servicos (mantida da versão anterior)
        cursor.execute('''CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL UNIQUE,
            preco DECIMAL(9,2) NOT NULL
        )''')

        # Tabela Agendamentos (mantida da versão anterior)
        cursor.execute('''CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER,
            servico_id INTEGER,
            data_hora DATETIME,
            FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
            FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE
        )''')

        # NOVA Tabela para Registros de Vacinas
        cursor.execute('''CREATE TABLE IF NOT EXISTS registros_vacinas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER NOT NULL,
            nome_vacina VARCHAR(100) NOT NULL,
            data_aplicacao DATE NOT NULL,
            proxima_data_aplicacao DATE,
            FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
        )''')

        conn.commit()
        conn.close()
        print("Tabelas (incluindo registros_vacinas) verificadas/criadas pela classe Database.")

    def popular_servicos_iniciais(self):
        servicos_padrao = [
            ("Banho", 26.00), # Preço ajustado conforme seu exemplo
            ("Tosa Higiênica", 25.00),
            ("Tosa Completa", 50.00),
            ("Consulta Veterinária", 50.00),
            ("Aplicação de Vacina", 15.00) # Custo do serviço de aplicar, a vacina em si pode ter outro custo ou ser parte do nome.
                                         # Ou, se o preço da vacina varia, pode ser registrado no momento.
                                         # O valor 85 que você mencionou pode ser o nome_vacina + custo,
                                         # mas para o serviço em si, vamos colocar um valor simbólico aqui.
        ]
        conn = self._get_db_conn()
        cursor = conn.cursor()
        for nome, preco in servicos_padrao:
            try:
                cursor.execute("INSERT INTO servicos (nome, preco) VALUES (?, ?)", (nome, preco))
            except sqlite3.IntegrityError:
                pass
        conn.commit()
        conn.close()
        print("Serviços iniciais verificados/populados pela classe Database.")

    # --- Métodos CRUD para Clientes ---
    def cadastrar_cliente(self, nome, cpf, telefone, email, genero, data_nascimento, senha):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO clientes (nome, cpf, telefone, email, genero, data_nascimento, senha) VALUES (?, ?, ?, ?, ?, ?, ?)",
                           (nome, cpf, telefone, email, genero, data_nascimento, senha))
            conn.commit()
            return True
        except sqlite3.IntegrityError:
            print(f"Erro DB: CPF '{cpf}' já cadastrado.")
            return False
        finally:
            conn.close()
    
    def listar_clientes(self):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, cpf, telefone FROM clientes")
        clientes = cursor.fetchall()
        conn.close()
        return [dict(cliente) for cliente in clientes]

    def buscar_cliente_id_por_cpf(self, cpf):
        """Busca o ID de um cliente pelo CPF."""
        conn = self._get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clientes WHERE cpf = ?", (cpf,))
        cliente = cursor.fetchone()
        conn.close()
        return cliente['id'] if cliente else None

    # --- Métodos CRUD para Pets ---
    def adicionar_pet(self, nome, especie, raca, idade, cliente_id):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO pets (nome, especie, raca, cliente_id) VALUES (?, ?, ?, ?)",
                           (nome, especie, raca, cliente_id))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao adicionar pet: {e}")
            return None
        finally:
            conn.close()

    def listar_pets_simples(self):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome FROM pets")
        pets = cursor.fetchall()
        conn.close()
        return [dict(pet) for pet in pets]

    def buscar_pet_por_nome(self, nome_pet, cliente_id=None): # Pode opcionalmente filtrar por cliente
        conn = self._get_db_conn()
        cursor = conn.cursor()
        query = "SELECT id FROM pets WHERE nome = ?"
        params = [nome_pet]
        if cliente_id:
            query += " AND cliente_id = ?"
            params.append(cliente_id)
        query += " LIMIT 1"
        cursor.execute(query, tuple(params))
        pet = cursor.fetchone()
        conn.close()
        return pet['id'] if pet else None

    # --- Métodos CRUD para Tipos de Serviços ---
    def listar_servicos(self): # Lista os tipos de serviço e seus preços
        conn = self._get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, nome, preco FROM servicos")
        servicos = cursor.fetchall()
        conn.close()
        return [dict(s) for s in servicos]

    def buscar_servico_por_nome(self, nome_servico):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id, preco FROM servicos WHERE nome = ? LIMIT 1", (nome_servico,))
        servico = cursor.fetchone()
        conn.close()
        return servico if servico else None # Retorna o Row (id, preco) ou None

    # --- Métodos CRUD para Agendamentos ---
    def agendar_servico(self, pet_id, servico_id, data_hora_str):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            dt_obj = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M") # Valida/converte formato
            data_hora_sqlite = dt_obj.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("INSERT INTO agendamentos (pet_id, servico_id, data_hora) VALUES (?, ?, ?)",
                           (pet_id, servico_id, data_hora_sqlite))
            conn.commit()
            return True
        except ValueError:
            print(f"Erro: Formato de data/hora inválido: '{data_hora_str}'. Use YYYY-MM-DD HH:MM")
            return False
        except Exception as e:
            print(f"Erro ao agendar serviço: {e}")
            return False
        finally:
            conn.close()

    def listar_agendamentos_detalhados(self):
        """Lista agendamentos com detalhes do pet, serviço e cliente."""
        conn = self._get_db_conn()
        cursor = conn.cursor()
        # Modificado para incluir o nome do cliente
        cursor.execute('''
            SELECT 
                a.id as agendamento_id, 
                p.nome as nome_pet, 
                s.nome as nome_servico, 
                s.preco as valor_servico,
                strftime('%Y-%m-%d %H:%M', a.data_hora) as data_hora_formatada,
                c.nome as nome_cliente,
                c.cpf as cpf_cliente
            FROM agendamentos a
            JOIN pets p ON a.pet_id = p.id
            JOIN servicos s ON a.servico_id = s.id
            JOIN clientes c ON p.cliente_id = c.id
            ORDER BY a.data_hora DESC
        ''')
        agendamentos = cursor.fetchall()
        conn.close()
        return [dict(ag) for ag in agendamentos]

    # --- Métodos para agendamento rápido de serviços comuns ---
    def _agendar_servico_comum(self, pet_id, nome_servico_comum, data_hora_str):
        servico_info = self.buscar_servico_por_nome(nome_servico_comum)
        if not servico_info:
            print(f"Erro: Tipo de serviço '{nome_servico_comum}' não encontrado na tabela de serviços.")
            return False
        
        servico_id = servico_info['id']
        # O preço já está na tabela de serviços, então não precisamos passá-lo aqui.
        # A função agendar_servico não lida com preço customizado.
        return self.agendar_servico(pet_id, servico_id, data_hora_str)

    def agendar_tosa_higienica(self, pet_id, data_hora_str):
        return self._agendar_servico_comum(pet_id, "Tosa Higiênica", data_hora_str)

    def agendar_tosa_completa(self, pet_id, data_hora_str):
        return self._agendar_servico_comum(pet_id, "Tosa Completa", data_hora_str)

    def agendar_banho(self, pet_id, data_hora_str):
        return self._agendar_servico_comum(pet_id, "Banho", data_hora_str)
    
    # Para a "vacina" como um serviço agendável (custo de aplicação):
    def agendar_aplicacao_vacina(self, pet_id, data_hora_str):
        return self._agendar_servico_comum(pet_id, "Aplicação de Vacina", data_hora_str)

    # --- Métodos CRUD para Registros de Vacinas ---
    def cadastrar_registro_vacina(self, pet_id, nome_vacina, data_aplicacao_str, proxima_data_aplicacao_str=None):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            # Validar e formatar datas (ex: YYYY-MM-DD)
            datetime.strptime(data_aplicacao_str, "%Y-%m-%d") # Valida formato
            if proxima_data_aplicacao_str:
                datetime.strptime(proxima_data_aplicacao_str, "%Y-%m-%d") # Valida formato
            else:
                proxima_data_aplicacao_str = None # Garante que seja NULL se vazio

            cursor.execute("""
                INSERT INTO registros_vacinas (pet_id, nome_vacina, data_aplicacao, proxima_data_aplicacao)
                VALUES (?, ?, ?, ?)
            """, (pet_id, nome_vacina, data_aplicacao_str, proxima_data_aplicacao_str))
            conn.commit()
            return True
        except ValueError:
            print(f"Erro: Formato de data inválido para vacina. Use YYYY-MM-DD.")
            return False
        except Exception as e:
            print(f"Erro ao cadastrar registro de vacina: {e}")
            return False
        finally:
            conn.close()

    def listar_registros_vacinas(self, pet_id=None):
        """Lista todos os registros de vacinas ou para um pet específico."""
        conn = self._get_db_conn()
        cursor = conn.cursor()
        query = """
            SELECT rv.id, rv.pet_id, p.nome as nome_pet, rv.nome_vacina, 
                   strftime('%Y-%m-%d', rv.data_aplicacao) as data_aplicacao, 
                   strftime('%Y-%m-%d', rv.proxima_data_aplicacao) as proxima_data_aplicacao
            FROM registros_vacinas rv
            JOIN pets p ON rv.pet_id = p.id
        """
        params = []
        if pet_id:
            query += " WHERE rv.pet_id = ?"
            params.append(pet_id)
        query += " ORDER BY rv.data_aplicacao DESC"
        
        cursor.execute(query, tuple(params))
        registros = cursor.fetchall()
        conn.close()
        return [dict(reg) for reg in registros]
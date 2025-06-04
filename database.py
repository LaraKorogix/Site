# database.py
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

        # Tabela Clientes
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

        # Tabela Pets - A coluna 'idade' continua existindo, mas será opcional na inserção
        cursor.execute('''CREATE TABLE IF NOT EXISTS pets (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL,
            especie VARCHAR(100) NOT NULL,
            raca VARCHAR(100) NOT NULL,
            idade INTEGER, 
            cliente_id INTEGER,
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        )''')

        # ... (restante das tabelas: servicos, agendamentos, registros_vacinas) ...
        # (O código das outras tabelas permanece o mesmo da sua versão anterior)

        cursor.execute('''CREATE TABLE IF NOT EXISTS servicos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            nome VARCHAR(100) NOT NULL UNIQUE,
            preco DECIMAL(9,2) NOT NULL
        )''')

        cursor.execute('''CREATE TABLE IF NOT EXISTS agendamentos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            pet_id INTEGER,
            servico_id INTEGER,
            data_hora DATETIME,
            FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
            FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE
        )''')

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
        # ... (código de popular_servicos_iniciais permanece o mesmo) ...
        servicos_padrao = [
            ("Banho", 26.00),
            ("Tosa Higiênica", 25.00),
            ("Tosa Completa", 50.00),
            ("Consulta Veterinária", 50.00),
            ("Aplicação de Vacina", 15.00)
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
    # ... (cadastrar_cliente, listar_clientes, buscar_cliente_id_por_cpf permanecem os mesmos) ...
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
        conn = self._get_db_conn()
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clientes WHERE cpf = ?", (cpf,))
        cliente = cursor.fetchone()
        conn.close()
        return cliente['id'] if cliente else None

    # --- Métodos CRUD para Pets ---
    # Alterado: 'idade' é agora um parâmetro opcional com default None
    def adicionar_pet(self, nome, especie, raca, cliente_id, idade=None):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            # A query continua incluindo 'idade', que será NULL se 'idade' for None
            cursor.execute("INSERT INTO pets (nome, especie, raca, cliente_id, idade) VALUES (?, ?, ?, ?, ?)",
                           (nome, especie, raca, cliente_id, idade))
            conn.commit()
            return cursor.lastrowid
        except Exception as e:
            print(f"Erro ao adicionar pet no DB: {e}")
            return None
        finally:
            conn.close()

    # ... (listar_pets_simples, buscar_pet_por_nome permanecem os mesmos) ...
    def listar_pets_simples(self, cliente_id=None):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        query = "SELECT id, nome FROM pets"
        params = []
        if cliente_id:
            query += " WHERE cliente_id = ?"
            params.append(cliente_id)
        cursor.execute(query, tuple(params))
        pets = cursor.fetchall()
        conn.close()
        return [dict(pet) for pet in pets]

    def buscar_pet_por_nome(self, nome_pet, cliente_id=None):
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
    # ... (listar_servicos, buscar_servico_por_nome permanecem os mesmos) ...
    def listar_servicos(self):
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
        return servico 

    # --- Métodos CRUD para Agendamentos ---
    # ... (agendar_servico, listar_agendamentos_detalhados, _agendar_servico_comum, etc. permanecem os mesmos) ...
    def agendar_servico(self, pet_id, servico_id, data_hora_str):
        print(f"DB DEBUG (agendar_servico): Recebido pet_id={pet_id}, servico_id={servico_id}, data_hora_str='{data_hora_str}'")
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            # Verifica se os IDs existem nas tabelas referenciadas (BOA PRÁTICA)
            cursor.execute("SELECT id FROM pets WHERE id = ?", (pet_id,))
            if not cursor.fetchone():
                print(f"DB DEBUG ERROR (agendar_servico): pet_id {pet_id} não encontrado na tabela pets.")
                return False
            
            cursor.execute("SELECT id FROM servicos WHERE id = ?", (servico_id,))
            if not cursor.fetchone():
                print(f"DB DEBUG ERROR (agendar_servico): servico_id {servico_id} não encontrado na tabela servicos.")
                return False

            dt_obj = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M") # Espera YYYY-MM-DD HH:MM
            data_hora_sqlite = dt_obj.strftime("%Y-%m-%d %H:%M:%S")
            print(f"DB DEBUG (agendar_servico): data_hora_sqlite formatada para INSERT: '{data_hora_sqlite}'")

            cursor.execute("INSERT INTO agendamentos (pet_id, servico_id, data_hora) VALUES (?, ?, ?)",
                           (pet_id, servico_id, data_hora_sqlite))
            conn.commit()
            print(f"DB DEBUG (agendar_servico): INSERT e COMMIT realizados com SUCESSO.")
            return True
        except ValueError: # Erro na conversão de data/hora
            print(f"DB DEBUG ERROR (agendar_servico): ValueError ao processar data_hora_str='{data_hora_str}'. Formato esperado YYYY-MM-DD HH:MM")
            return False
        except sqlite3.IntegrityError as e: # Erro de integridade (ex: FK não existe, mas a verificação acima deveria pegar)
             print(f"DB DEBUG ERROR (agendar_servico): sqlite3.IntegrityError: {e}")
             return False
        except Exception as e: # Outras exceções do DB
            print(f"DB DEBUG ERROR (agendar_servico): Exceção geral no DB: {e}")
            import traceback # Para mais detalhes do erro
            print(traceback.format_exc())
            return False
        finally:
            if conn: # Garante que conn existe antes de tentar fechar
                conn.close()

    def listar_agendamentos_detalhados(self, cliente_id=None):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        base_query = '''
            SELECT 
                a.id as agendamento_id, 
                p.nome as nome_pet, 
                s.nome as nome_servico,
                s.preco as valor_servico,
                strftime('%Y-%m-%d', a.data_hora) as data,
                strftime('%H:%M', a.data_hora) as hora,
                c.nome as nome_cliente,
                c.cpf as cpf_cliente
            FROM agendamentos a
            JOIN pets p ON a.pet_id = p.id
            JOIN servicos s ON a.servico_id = s.id
            JOIN clientes c ON p.cliente_id = c.id
        '''
        params = []
        if cliente_id:
            base_query += " WHERE c.id = ?"
            params.append(cliente_id)
        base_query += " ORDER BY a.data_hora DESC"
        cursor.execute(base_query, tuple(params))
        agendamentos = cursor.fetchall()
        conn.close()
        return [dict(ag) for ag in agendamentos]

    def _agendar_servico_comum(self, pet_id, nome_servico_comum, data_hora_str):
        servico_info = self.buscar_servico_por_nome(nome_servico_comum)
        if not servico_info:
            print(f"Erro: Tipo de serviço '{nome_servico_comum}' não encontrado.")
            return False
        servico_id = servico_info['id']
        return self.agendar_servico(pet_id, servico_id, data_hora_str)

    def agendar_tosa_higienica(self, pet_id, data_hora_str):
        return self._agendar_servico_comum(pet_id, "Tosa Higiênica", data_hora_str)

    def agendar_tosa_completa(self, pet_id, data_hora_str):
        return self._agendar_servico_comum(pet_id, "Tosa Completa", data_hora_str)

    def agendar_banho(self, pet_id, data_hora_str):
        return self._agendar_servico_comum(pet_id, "Banho", data_hora_str)
    
    def agendar_aplicacao_vacina(self, pet_id, data_hora_str):
        return self._agendar_servico_comum(pet_id, "Aplicação de Vacina", data_hora_str)

    # --- Métodos CRUD para Registros de Vacinas ---
    # ... (cadastrar_registro_vacina, listar_registros_vacinas permanecem os mesmos) ...
    def cadastrar_registro_vacina(self, pet_id, nome_vacina, data_aplicacao_str, proxima_data_aplicacao_str=None):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            datetime.strptime(data_aplicacao_str, "%Y-%m-%d")
            if proxima_data_aplicacao_str and proxima_data_aplicacao_str.strip() != "":
                datetime.strptime(proxima_data_aplicacao_str, "%Y-%m-%d")
            else:
                proxima_data_aplicacao_str = None
            cursor.execute("INSERT INTO registros_vacinas (pet_id, nome_vacina, data_aplicacao, proxima_data_aplicacao) VALUES (?, ?, ?, ?)",
                           (pet_id, nome_vacina, data_aplicacao_str, proxima_data_aplicacao_str))
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
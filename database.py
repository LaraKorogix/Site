# database.py
import mysql.connector
from mysql.connector import errorcode # For specific error handling
from datetime import datetime

class Database:
    def __init__(self, host, user, password, database_name):
        # MySQL connection parameters
        self.host = host
        self.user = user
        self.password = password
        self.database_name = database_name
        self._ensure_database_exists() # Ensure database exists on initialization

    def _ensure_database_exists(self):
        """Creates the database if it doesn't already exist."""
        try:
            # Connect to MySQL server (without specifying a database initially)
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password
            )
            cursor = conn.cursor()
            # Use CHARACTER SET and COLLATE for proper unicode support
            cursor.execute(f"CREATE DATABASE IF NOT EXISTS {self.database_name} CHARACTER SET utf8mb4 COLLATE utf8mb4_unicode_ci")
            print(f"Database '{self.database_name}' checked/created successfully.")
            cursor.close()
            conn.close()
        except mysql.connector.Error as err:
            print(f"Error ensuring database '{self.database_name}' exists: {err}")
            # Depending on your app's needs, you might want to raise this error
            # or handle it more gracefully. For now, just printing.

    def _get_db_conn(self):
        """Establishes a connection to the MySQL database."""
        try:
            conn = mysql.connector.connect(
                host=self.host,
                user=self.user,
                password=self.password,
                database=self.database_name
            )
            return conn
        except mysql.connector.Error as err:
            print(f"Error connecting to MySQL database '{self.database_name}': {err}")
            raise # Re-raise the error so calling functions know connection failed

    def criar_tabelas(self):
        """Creates the necessary tables in the MySQL database if they don't exist."""
        conn = self._get_db_conn()
        cursor = conn.cursor() # Standard cursor for DDL

        # Table Clientes
        cursor.execute('''CREATE TABLE IF NOT EXISTS clientes (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nome VARCHAR(100) NOT NULL,
            cpf VARCHAR(14) UNIQUE NOT NULL,
            telefone VARCHAR(20),
            email VARCHAR(100),
            genero VARCHAR(20),
            data_nascimento VARCHAR(10), 
            senha VARCHAR(100) 
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''') # Added ENGINE & CHARSET for MySQL

        # Table Pets
        cursor.execute('''CREATE TABLE IF NOT EXISTS pets (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nome VARCHAR(100) NOT NULL,
            especie VARCHAR(100) NOT NULL,
            raca VARCHAR(100) NOT NULL,
            idade INTEGER, 
            cliente_id INT, 
            FOREIGN KEY (cliente_id) REFERENCES clientes(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Table Servicos
        cursor.execute('''CREATE TABLE IF NOT EXISTS servicos (
            id INT PRIMARY KEY AUTO_INCREMENT,
            nome VARCHAR(100) NOT NULL UNIQUE,
            preco DECIMAL(9,2) NOT NULL
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Table Agendamentos
        cursor.execute('''CREATE TABLE IF NOT EXISTS agendamentos (
            id INT PRIMARY KEY AUTO_INCREMENT,
            pet_id INT,
            servico_id INT,
            data_hora DATETIME, 
            FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE,
            FOREIGN KEY (servico_id) REFERENCES servicos(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')

        # Table Registros_Vacinas
        cursor.execute('''CREATE TABLE IF NOT EXISTS registros_vacinas (
            id INT PRIMARY KEY AUTO_INCREMENT,
            pet_id INT NOT NULL,
            nome_vacina VARCHAR(100) NOT NULL,
            data_aplicacao DATE NOT NULL, 
            proxima_data_aplicacao DATE, 
            FOREIGN KEY (pet_id) REFERENCES pets(id) ON DELETE CASCADE
        ) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_unicode_ci''')
        
        conn.commit()
        cursor.close()
        conn.close()
        print("MySQL Tables (incluindo registros_vacinas) verified/created.")

    def popular_servicos_iniciais(self):
        """Populates the 'servicos' table with initial data if they don't exist."""
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
                # Using %s as placeholder for MySQL
                cursor.execute("INSERT INTO servicos (nome, preco) VALUES (%s, %s)", (nome, preco))
            except mysql.connector.Error as err:
                if err.errno == errorcode.ER_DUP_ENTRY: # Specific error for duplicate entry
                    pass # Service already exists, skip
                else:
                    print(f"Error inserting service '{nome}': {err}") # Log other errors
        conn.commit()
        cursor.close()
        conn.close()
        print("Initial services verified/populated for MySQL.")

    # --- Métodos CRUD para Clientes ---
    def cadastrar_cliente(self, nome, cpf, telefone, email, genero, data_nascimento, senha):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO clientes (nome, cpf, telefone, email, genero, data_nascimento, senha) VALUES (%s, %s, %s, %s, %s, %s, %s)",
                           (nome, cpf, telefone, email, genero, data_nascimento, senha))
            conn.commit()
            return True
        except mysql.connector.Error as err:
            if err.errno == errorcode.ER_DUP_ENTRY:
                print(f"MySQL Error: CPF '{cpf}' já cadastrado.")
            else:
                print(f"MySQL Error ao cadastrar cliente: {err}")
            return False
        finally:
            cursor.close()
            conn.close()
    
    def listar_clientes(self):
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True) # Get rows as dictionaries
        cursor.execute("SELECT id, nome, cpf, telefone FROM clientes")
        clientes = cursor.fetchall()
        cursor.close()
        conn.close()
        return clientes # Already a list of dicts

    def buscar_cliente_id_por_cpf(self, cpf):
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id FROM clientes WHERE cpf = %s", (cpf,))
        cliente = cursor.fetchone()
        cursor.close()
        conn.close()
        return cliente['id'] if cliente else None # type: ignore

    # --- Métodos CRUD para Pets ---
    def adicionar_pet(self, nome, especie, raca, cliente_id, idade=None):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO pets (nome, especie, raca, cliente_id, idade) VALUES (%s, %s, %s, %s, %s)",
                           (nome, especie, raca, cliente_id, idade))
            conn.commit()
            return cursor.lastrowid # Get the ID of the inserted row
        except mysql.connector.Error as e:
            print(f"MySQL Error ao adicionar pet: {e}")
            return None
        finally:
            cursor.close()
            conn.close()

    def listar_pets_simples(self, cliente_id=None):
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id, nome FROM pets"
        params = []
        if cliente_id:
            query += " WHERE cliente_id = %s"
            params.append(cliente_id)
        cursor.execute(query, tuple(params))
        pets = cursor.fetchall()
        cursor.close()
        conn.close()
        return pets

    def buscar_pet_por_nome(self, nome_pet, cliente_id=None):
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        query = "SELECT id FROM pets WHERE nome = %s"
        params = [nome_pet]
        if cliente_id:
            query += " AND cliente_id = %s"
            params.append(cliente_id)
        query += " LIMIT 1" # Ensure only one row is returned
        cursor.execute(query, tuple(params))
        pet = cursor.fetchone()
        cursor.close()
        conn.close()
        return pet['id'] if pet else None # type: ignore

    # --- Métodos CRUD para Tipos de Serviços ---
    def listar_servicos(self):
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, nome, preco FROM servicos")
        servicos = cursor.fetchall()
        cursor.close()
        conn.close()
        return servicos

    def buscar_servico_por_nome(self, nome_servico):
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        cursor.execute("SELECT id, preco FROM servicos WHERE nome = %s LIMIT 1", (nome_servico,))
        servico = cursor.fetchone()
        cursor.close()
        conn.close()
        return servico 

    # --- Métodos CRUD para Agendamentos ---
    def agendar_servico(self, pet_id, servico_id, data_hora_str):
        print(f"DB DEBUG (agendar_servico): Recebido pet_id={pet_id}, servico_id={servico_id}, data_hora_str='{data_hora_str}'")
        conn = self._get_db_conn()
        # Use a separate cursor for verification to avoid issues if main transaction fails
        verify_cursor = conn.cursor() 
        try:
            verify_cursor.execute("SELECT id FROM pets WHERE id = %s", (pet_id,))
            if not verify_cursor.fetchone():
                print(f"DB DEBUG ERROR (agendar_servico): pet_id {pet_id} não encontrado.")
                return False
            
            verify_cursor.execute("SELECT id FROM servicos WHERE id = %s", (servico_id,))
            if not verify_cursor.fetchone():
                print(f"DB DEBUG ERROR (agendar_servico): servico_id {servico_id} não encontrado.")
                return False
            verify_cursor.close() # Close verify cursor once done

            # Convert string to datetime object, then format for MySQL DATETIME
            dt_obj = datetime.strptime(data_hora_str, "%Y-%m-%d %H:%M")
            data_hora_mysql = dt_obj.strftime("%Y-%m-%d %H:%M:%S") # MySQL DATETIME format
            print(f"DB DEBUG (agendar_servico): data_hora_mysql formatada: '{data_hora_mysql}'")

            main_cursor = conn.cursor()
            main_cursor.execute("INSERT INTO agendamentos (pet_id, servico_id, data_hora) VALUES (%s, %s, %s)",
                               (pet_id, servico_id, data_hora_mysql))
            conn.commit()
            main_cursor.close()
            print(f"DB DEBUG (agendar_servico): INSERT e COMMIT SUCESSO.")
            return True
        except ValueError:
            print(f"DB DEBUG ERROR (agendar_servico): ValueError com data_hora_str='{data_hora_str}'. Formato: YYYY-MM-DD HH:MM")
            return False
        except mysql.connector.Error as e:
            print(f"DB DEBUG ERROR (agendar_servico): MySQL Error: {e}")
            # import traceback # Uncomment for detailed traceback during debugging
            # print(traceback.format_exc())
            return False
        finally:
            # Garante que verify_cursor foi definido antes de tentar fechá-lo
            if 'verify_cursor' in locals() and verify_cursor:
                verify_cursor.close()  # Simplesmente feche o cursor

            # Mantém a verificação para a conexão, pois conn.is_connected() existe
            if 'conn' in locals() and conn and conn.is_connected():
                conn.close()

    def listar_agendamentos_detalhados(self, cliente_id=None):
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        # Using MySQL's DATE_FORMAT function
        base_query = '''
            SELECT 
                a.id as agendamento_id, 
                p.nome as nome_pet, 
                s.nome as nome_servico,
                s.preco as valor_servico,
                DATE_FORMAT(a.data_hora, '%Y-%m-%d') as data,
                DATE_FORMAT(a.data_hora, '%H:%i') as hora, /* %i for minutes in MySQL */
                c.nome as nome_cliente,
                c.cpf as cpf_cliente
            FROM agendamentos a
            JOIN pets p ON a.pet_id = p.id
            JOIN servicos s ON a.servico_id = s.id
            JOIN clientes c ON p.cliente_id = c.id
        '''
        params = []
        if cliente_id:
            base_query += " WHERE c.id = %s"
            params.append(cliente_id)
        base_query += " ORDER BY a.data_hora DESC"
        cursor.execute(base_query, tuple(params))
        agendamentos = cursor.fetchall()
        cursor.close()
        conn.close()
        return agendamentos

    def _agendar_servico_comum(self, pet_id, nome_servico_comum, data_hora_str):
        servico_info = self.buscar_servico_por_nome(nome_servico_comum)
        if not servico_info:
            print(f"Erro: Tipo de serviço '{nome_servico_comum}' não encontrado.")
            return False
        servico_id = servico_info['id'] # type: ignore
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
    def cadastrar_registro_vacina(self, pet_id, nome_vacina, data_aplicacao_str, proxima_data_aplicacao_str=None):
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            # Validate date strings before insertion (MySQL DATE format is 'YYYY-MM-DD')
            datetime.strptime(data_aplicacao_str, "%Y-%m-%d") # Validates format
            if proxima_data_aplicacao_str and proxima_data_aplicacao_str.strip() != "":
                datetime.strptime(proxima_data_aplicacao_str, "%Y-%m-%d") # Validates format
            else:
                proxima_data_aplicacao_str = None # Ensure it's SQL NULL if empty
            
            cursor.execute("INSERT INTO registros_vacinas (pet_id, nome_vacina, data_aplicacao, proxima_data_aplicacao) VALUES (%s, %s, %s, %s)",
                           (pet_id, nome_vacina, data_aplicacao_str, proxima_data_aplicacao_str))
            conn.commit()
            return True
        except ValueError:
            print(f"MySQL Error: Formato de data inválido para vacina. Use YYYY-MM-DD.")
            return False
        except mysql.connector.Error as e:
            print(f"MySQL Error ao cadastrar registro de vacina: {e}")
            return False
        finally:
            cursor.close()
            conn.close()

    def listar_registros_vacinas(self, pet_id=None):
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        # Using MySQL's DATE_FORMAT for DATE columns as well for consistency
        query = """
            SELECT rv.id, rv.pet_id, p.nome as nome_pet, rv.nome_vacina, 
                   DATE_FORMAT(rv.data_aplicacao, '%Y-%m-%d') as data_aplicacao, 
                   DATE_FORMAT(rv.proxima_data_aplicacao, '%Y-%m-%d') as proxima_data_aplicacao
            FROM registros_vacinas rv
            JOIN pets p ON rv.pet_id = p.id
        """
        params = []
        if pet_id:
            query += " WHERE rv.pet_id = %s"
            params.append(pet_id)
        query += " ORDER BY rv.data_aplicacao DESC"
        cursor.execute(query, tuple(params))
        registros = cursor.fetchall()
        cursor.close()
        conn.close()
        return registros
    def buscar_agendamento_por_id(self, agendamento_id):
        """Busca um agendamento específico pelo ID, formatando data e hora."""
        conn = self._get_db_conn()
        cursor = conn.cursor(dictionary=True)
        query = """
            SELECT 
                a.id as agendamento_id, 
                a.pet_id,
                p.nome as nome_pet,
                p.cliente_id, # Importante para verificação de propriedade
                a.servico_id,
                s.nome as nome_servico,
                DATE_FORMAT(a.data_hora, '%Y-%m-%d') as data,
                DATE_FORMAT(a.data_hora, '%H:%i') as hora
            FROM agendamentos a
            JOIN pets p ON a.pet_id = p.id
            JOIN servicos s ON a.servico_id = s.id
            WHERE a.id = %s
        """
        try:
            cursor.execute(query, (agendamento_id,))
            agendamento = cursor.fetchone()
            return agendamento
        except mysql.connector.Error as e:
            print(f"MySQL Error ao buscar agendamento por ID: {e}") # Log no servidor
            return None
        finally:
            cursor.close()
            conn.close()

    def editar_agendamento(self, agendamento_id, nova_data_hora_str):
        """Atualiza a data e hora de um agendamento existente."""
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            dt_obj = datetime.strptime(nova_data_hora_str, "%Y-%m-%d %H:%M")
            data_hora_mysql = dt_obj.strftime("%Y-%m-%d %H:%M:%S")

            cursor.execute("UPDATE agendamentos SET data_hora = %s WHERE id = %s",
                           (data_hora_mysql, agendamento_id))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"DB INFO: Agendamento ID {agendamento_id} atualizado para {data_hora_mysql}.") # Log no servidor
                return True
            else:
                print(f"DB WARN: Nenhuma linha atualizada para agendamento ID {agendamento_id}.") # Log no servidor
                return False
        except ValueError:
            print(f"DB Error: Formato de data/hora inválido para edição: '{nova_data_hora_str}'. Use YYYY-MM-DD HH:MM.") # Log no servidor
            return False
        except mysql.connector.Error as e:
            print(f"MySQL Error ao editar agendamento ID {agendamento_id}: {e}") # Log no servidor
            return False
        finally:
            cursor.close()
            conn.close()

    def excluir_agendamento(self, agendamento_id):
        """Exclui um agendamento específico pelo ID."""
        conn = self._get_db_conn()
        cursor = conn.cursor()
        try:
            cursor.execute("DELETE FROM agendamentos WHERE id = %s", (agendamento_id,))
            conn.commit()
            if cursor.rowcount > 0:
                print(f"DB INFO: Agendamento ID {agendamento_id} excluído.") # Log no servidor
                return True
            else:
                print(f"DB WARN: Nenhuma linha excluída para agendamento ID {agendamento_id}.") # Log no servidor
                return False
        except mysql.connector.Error as e:
            print(f"MySQL Error ao excluir agendamento ID {agendamento_id}: {e}") # Log no servidor
            return False
        finally:
            cursor.close()
            conn.close()

    def verificar_propriedade_agendamento(self, agendamento_id, cliente_id_logado):
        """Verifica se um agendamento pertence a um cliente específico."""
        agendamento = self.buscar_agendamento_por_id(agendamento_id)
        if agendamento and agendamento.get('cliente_id') == cliente_id_logado:  # type: ignore
            return True
        print(f"DB WARN: Tentativa de acesso não autorizado ao agendamento ID {agendamento_id} pelo cliente ID {cliente_id_logado}.") # Log no servidor
        return False
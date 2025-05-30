from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# 1. Página inicial redireciona para login-cadastro


@app.route('/')
def index():
    return redirect(url_for('index'))

# 2. Página de login ou criação de conta
@app.route('/login-cadastro', methods=['GET'])
def logincadastro():
    return render_template('login-cadastro.html')

# 3. Página home após login ou cadastro concluído
@app.route('/home')
def home():
    return render_template('home.html')

# 4. Página de formulário de cadastro
@app.route('/cadastro', methods=['GET'])
def exibir_cadastro():
    return render_template('cadastro.html')

# 5. Processa o cadastro e redireciona para home
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

# Executa o servidor
if __name__ == '__main__':
    app.run(debug=True)

from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Página inicial (index.html)
@app.route('/')
def index():
    return render_template('index.html')

# Página com opções de login/cadastro
@app.route('/login-cadastro')
def logincadastro():
    return render_template('login-cadastro.html')

# Página de cadastro
@app.route('/cadastro')
def exibir_cadastro():
    return render_template('cadastro.html')

# Envio do formulário de cadastro
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

# Página home após login ou cadastro

@app.route('/home')
def home():
    return render_template('home.html')

@app.route('/servico')
def servico():
    return render_template('servicos.html')

@app.route('/vacina')
def vacina():
    return render_template('vacina.html')


if __name__ == '__main__':
    app.run(debug=True)

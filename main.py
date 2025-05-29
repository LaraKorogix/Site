from flask import Flask, render_template, request, redirect, url_for

app = Flask(__name__)

# Página principal
@app.route('/')
def index():
    return render_template('index.html')

# Rota de login (exemplo com teste fixo)
@app.route('/logar', methods=['POST'])
def logar():
    usuario = request.form.get('usuario')
    senha = request.form.get('senha')

    # Teste básico de login (temporário)
    if usuario == 'admin' and senha == '1234':
        return redirect(url_for('index.html'))
    else:
        return "<h1>Login inválido</h1><a href='/'>Voltar</a>"

# Página principal após login
@app.route('/home')
def pagina_principal():
    return render_template('home.html')  # Crie esse arquivo se quiser

# Logout
@app.route('/logout')
def logout():
    return redirect(url_for('index'))

# Executa o servidor
if __name__ == '__main__':
    app.run(debug=True)

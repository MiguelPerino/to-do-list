from flask import Flask, render_template, request, redirect, url_for, flash
from models.user import create_table,insert_user, get_user_by_email
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.secret_key = 'segredo'


create_table()


@app.route('/')
def home():
    return render_template('index.html')

@app.route('/cadastro', methods=['GET'])
def cadastro_page():
    return render_template('index.html') #mudei de cadastro.html para index.html

@app.route('/login', methods=['GET', 'POST'])   
def login_page():
    if request.method == 'GET':
        return render_template('login.html')
    
    email = request.form['email'].strip()
    senha = request.form['senha'].strip()

    if not email or not senha:
        flash('Preencha todos os campos', 'error')
        return redirect(url_for('login_page'))

    user = get_user_by_email(email)

    if user is None:
        flash('Usuário não encontrado', 'error')
        return redirect(url_for('login_page'))
    
    #user = (id, nome, email, senha)
    if not check_password_hash(user[3], senha):
        flash('Senha incorreta!', 'error')
        return redirect(url_for('login_page'))
    
    return render_template('login_sucesso.html', nome=user[1])

@app.route('/cadastro', methods=['POST'])
def cadastro():
    nome = request.form['nome'].strip()
    email = request.form['email'].strip()
    senha = request.form['senha'].strip()
    
    senha_hash = generate_password_hash(senha)

    if not nome or not email or not senha:    #validar os dados antes do banco de dados
        flash('Preencha todos os campos', 'error')
        return redirect(url_for('cadastro_page'))

    try:
        insert_user(nome, email, senha_hash)
        flash('Usuário cadastrado com sucesso', 'success')
        return redirect(url_for('login_page'))
    
    except sqlite3.IntegrityError:
        flash('Email ja cadastrado', 'error')

    return redirect(url_for('cadastro_page'))

if __name__ == '__main__':
    app.run(debug=True)
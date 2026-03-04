from flask import Flask, render_template, request, redirect, url_for, flash, session
from models.user import create_table,insert_user, get_user_by_email
from models.task import *
import sqlite3
from werkzeug.security import check_password_hash, generate_password_hash

app = Flask(__name__)

app.secret_key = 'segredo'


create_table()
create_task_table()

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
    
    # Salva o usuario na sessão
    session['user_id'] = user[0]
    session['user_nome'] = user[1]

    return redirect(url_for('tarefas'))

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

@app.route('/tarefas')
def tarefas():
    if 'user_id' not in session:
        flash('Faça login para acessar suas tarefas', 'error')
        return redirect(url_for('login_page'))

    tasks = get_tasks_by_user(session['user_id'])
    return render_template('tarefas.html', nome=session['user_nome'], tasks=tasks)

@app.route('/tarefas/adicionar', methods=['POST'])
def adicionar_tarefa():
    if 'user_id' not in session:
        return redirect(url_for('login_page'))
    
    titulo = request.form['titulo'].strip()
    descricao = request.form.get('descricao', '').strip()
    data_limite = request.form.get('data_limite', '')

    if not titulo:
        flash('O título da tarefa é obrigatório', 'error')
        return redirect(url_for('tarefas'))
    insert_task(session['user_id'], titulo, descricao, data_limite)
    flash('Tarefa adicionada', 'success')
    return redirect(url_for('tarefas'))

@app.route('/tarefas/concluir/<int:task_id>', methods=['POST'])
def concluir_tarefa(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    toggle_task(task_id, session['user_id'])
    return redirect(url_for('tarefas'))

@app.route('/tarefas/deletar/<int:task_id>', methods=['POST'])
def deletar_tarefa(task_id):
    if 'user_id' not in session:
        return redirect(url_for('login_page'))

    delete_task(task_id, session['user_id'])
    flash('Tarefa removida', 'success')
    return redirect(url_for('tarefas'))

@app.route('/logout')
def logout():
    session.clear()
    flash('Você saiu da conta', 'success')
    return redirect(url_for('home'))

if __name__ == '__main__':
    # app.run(debug=True)
    app.run(debug=False)
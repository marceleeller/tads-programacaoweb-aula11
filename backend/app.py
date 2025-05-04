from flask import Flask, request, jsonify, render_template, redirect, url_for
import mysql.connector
from flask_cors import CORS
from dotenv import load_dotenv
from bcrypt import hashpw, gensalt, checkpw
import os

# Carregar variáveis de ambiente
load_dotenv()

# Configuração do Flask
app = Flask(__name__)
CORS(app)

# Conexão com o banco de dados
def get_db_connection():
    return mysql.connector.connect(
        host=os.getenv('DB_HOST', 'localhost'),
        user=os.getenv('DB_USER', 'root'),
        password=os.getenv('DB_PASSWORD', ''),
        database=os.getenv('DB_NAME', 'sistema_usuario')
    )

# Rota para listar todos os usuários em formato JSON
@app.route('/usuarios', methods=['GET'])
def listar_usuarios():
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuario')
    usuarios = cursor.fetchall()
    cursor.close()
    conn.close()
    return jsonify(usuarios)

# Endpoint para criar um novo usuário
@app.route('/create', methods=['POST'])
def criar_usuario():
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400

    senha_hash = hashpw(senha.encode('utf-8'), gensalt())

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'INSERT INTO usuario (nome, email, senha) VALUES (%s, %s, %s)',
            (nome, email, senha_hash)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Usuário cadastrado com sucesso!'}), 201
    except mysql.connector.Error as err:
        return jsonify({'error': f'Erro no banco de dados: {err}'}), 500

# Rota para atualizar um usuário
@app.route('/update/<int:id>', methods=['GET', 'POST'])
def atualizar_usuario_html(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuario WHERE id = %s', (id,))
    usuario = cursor.fetchone()

    if request.method == 'POST':
        nome = request.form['nome']
        email = request.form['email']
        senha = request.form['senha']
        senha_hash = hashpw(senha.encode('utf-8'), gensalt())

        cursor.execute(
            'UPDATE usuario SET nome = %s, email = %s, senha = %s WHERE id = %s',
            (nome, email, senha_hash, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return redirect(url_for('listar_usuarios_html'))

    cursor.close()
    conn.close()
    return render_template('update.html', usuario=usuario)

# Rota para excluir um usuário
@app.route('/delete/<int:id>', methods=['DELETE'])
def excluir_usuario(id):
    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute('DELETE FROM usuario WHERE id = %s', (id,))
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Usuário excluído com sucesso!'}), 200
    except mysql.connector.Error as err:
        return jsonify({'error': f'Erro no banco de dados: {err}'}), 500

# Rota para obter um usuário específico
@app.route('/usuarios/<int:id>', methods=['GET'])
def obter_usuario(id):
    conn = get_db_connection()
    cursor = conn.cursor(dictionary=True)
    cursor.execute('SELECT * FROM usuario WHERE id = %s', (id,))
    usuario = cursor.fetchone()
    cursor.close()
    conn.close()

    if usuario:
        return jsonify(usuario)
    else:
        return jsonify({'error': 'Usuário não encontrado'}), 404

@app.route('/usuarios/<int:id>', methods=['PUT'])
def atualizar_usuario(id):
    data = request.get_json()
    nome = data.get('nome')
    email = data.get('email')
    senha = data.get('senha')

    if not nome or not email or not senha:
        return jsonify({'error': 'Todos os campos são obrigatórios!'}), 400

    senha_hash = hashpw(senha.encode('utf-8'), gensalt())

    try:
        conn = get_db_connection()
        cursor = conn.cursor()
        cursor.execute(
            'UPDATE usuario SET nome = %s, email = %s, senha = %s WHERE id = %s',
            (nome, email, senha_hash, id)
        )
        conn.commit()
        cursor.close()
        conn.close()
        return jsonify({'message': 'Usuário atualizado com sucesso!'})
    except mysql.connector.Error as err:
        return jsonify({'error': f'Erro no banco de dados: {err}'}), 500

if __name__ == '__main__':
    app.run(debug=True)
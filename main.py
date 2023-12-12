from flask import Flask, jsonify, request
from sqlalchemy import create_engine, text

app = Flask(__name__)
engine = create_engine('postgresql://user:senha@localhost:5432/nome_do_banco')


# Operação READ - Listar todos os alunos
@app.route('/alunos', methods=['GET'])
def listarAlunos():
    with engine.connect() as conn:
        query = text('SELECT * FROM aluno;')
        response = conn.execute(query)

        # Obter os nomes das colunas
        column_names = response.keys()

        # Coletar os resultados em uma lista de dicionários
        alunos = [dict(zip(column_names, row)) for row in response]

    return jsonify(alunos)


# Operação READ - Obter detalhes de um aluno específico
@app.route('/alunos/<int:aluno_id>', methods=['GET'])
def obterAluno(aluno_id):
    with engine.connect() as conn:
        query = text('SELECT * FROM aluno WHERE id = :aluno_id;')
        response = conn.execute(query, {'aluno_id': aluno_id})
        aluno = response.fetchone()

        if aluno:
            column_names = response.keys()
            aluno_dict = dict(zip(column_names, aluno))
            return jsonify(aluno_dict)
        else:
            return jsonify({'message': 'Aluno não encontrado'}), 404


# Operação CREATE - Adicionar um novo aluno
@app.route('/alunos', methods=['POST'])
def adicionarAluno():
    novo_aluno = request.get_json()

    query = text('INSERT INTO aluno (nome, cpf, arg_class, ano_entrada) '
                 'VALUES (:nome, :cpf, :arg_class, :ano_entrada) RETURNING *;')

    with engine.connect() as conn:
        response = conn.execute(query, {'nome': novo_aluno.get('nome'), 'cpf': novo_aluno.get('cpf'),
                                        'arg_class': novo_aluno.get('arg_class'),
                                        'ano_entrada': novo_aluno.get('ano_entrada')})
        novo_aluno_inserido = response.fetchone()

        # Commit da transação
        conn.commit()

    column_names = response.keys()
    aluno_dict = dict(zip(column_names, novo_aluno_inserido))

    return jsonify(aluno_dict), 201


# Operação UPDATE - Atualizar informações de um aluno
@app.route('/alunos/<int:aluno_id>', methods=['PUT'])
def atualizarAluno(aluno_id):
    aluno_atualizado = request.get_json()

    query = text('UPDATE aluno SET nome = :nome, cpf = :cpf, arg_class = :arg_class, '
                 'ano_entrada = :ano_entrada WHERE id = :aluno_id RETURNING *;')

    with engine.connect() as conn:
        response = conn.execute(query, {'nome': aluno_atualizado.get('nome'), 'cpf': aluno_atualizado.get('cpf'),
                                        'arg_class': aluno_atualizado.get('arg_class'),
                                        'ano_entrada': aluno_atualizado.get('ano_entrada'),
                                        'aluno_id': aluno_id})

        aluno_atualizado = response.fetchone()

        # Commit da transação
        conn.commit()

    if aluno_atualizado:
        column_names = response.keys()
        aluno_dict = dict(zip(column_names, aluno_atualizado))
        return jsonify(aluno_dict)
    else:
        return jsonify({'message': 'Aluno não encontrado'}), 404


# Operação DELETE - Remover um aluno
@app.route('/alunos/<int:aluno_id>', methods=['DELETE'])
def removerAluno(aluno_id):
    query = text('DELETE FROM aluno WHERE id = :aluno_id RETURNING *;')
    with engine.connect() as conn:
        response = conn.execute(query, {'aluno_id': aluno_id})

        aluno_removido = response.fetchone()

        # Commit da transação
        conn.commit()

    if aluno_removido:
        column_names = response.keys()
        aluno_dict = dict(zip(column_names, aluno_removido))
        return jsonify(aluno_dict)
    else:
        return jsonify({'message': 'Aluno não encontrado'}), 404


if __name__ == '__main__':
    app.run(debug=True)

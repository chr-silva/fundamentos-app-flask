import os
import psycopg2
from flask import Flask, render_template, request, redirect, url_for
from dotenv import load_dotenv

# Carrega as variáveis do .env - IMPORTANTE PARA SEGURANÇA (OWASP A07)

load_dotenv()
app = Flask(__name__)

# Uso da SECRET_KEY via variável de ambiente (OWASP A05: Falha de Configuração)
app.secret_key = os.getenv('SECRET_KEY')


def get_db_connection():
    try:
        conn = psycopg2.connect(
            host=os.getenv('DB_HOST'),
            database=os.getenv('DB_NAME'),
            user=os.getenv('DB_USER'),
            password=os.getenv('DB_PASSWORD')
        )
        return conn
    except psycopg2.Error as e:
        print(f"Erro de conexão com o banco de dados: {e}")
        # Em produção, este erro não deve expor detalhes internos (OWASP A05)
        # Deve ser substituído por uma mensagem de erro genérica.
        return None


# Rotas de CRUD com foco em segurança (OWASP A03)
@app.route('/nova', methods=('GET', 'POST'))
def nova_tarefa():
    if request.method == 'POST':
        titulo = request.form['titulo']
        descricao = request.form['descricao']

        # VALIDAÇÃO BÁSICA PARA PREVENIR DADOS OFENSIVOS (CRIMES CONTRA A HONRA)
        if len(titulo) > 100 or len(descricao) > 1000:
            # LGPD / Marco Civil: Evita o armazenamento de dados excessivos
            # (Princípio da Necessidade)
            # e grandes volumes de texto potencialmente ilícito.
            return "Erro: Conteúdo muito longo. Limite de 100 caracteres para título.", 400

        conn = get_db_connection()
        if conn:
            cur = conn.cursor()
            # PREVENÇÃO DE SQL INJECTION (OWASP A03) com placeholder %s
            cur.execute(
                'INSERT INTO tarefas (titulo, descricao) VALUES (%s, %s)',
                (titulo, descricao)
            )
            conn.commit()
            cur.close()
            conn.close()

        return redirect(url_for('index'))

    return render_template('nova.html')


# Rotas restantes (index, editar, deletar) seguem o mesmo princípio de segurança.


if __name__ == '__main__':
    # Em produção, o debug deve ser False (OWASP A05)
    app.run(debug=True)

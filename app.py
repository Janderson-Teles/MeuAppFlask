from flask import Flask, render_template, request, redirect, url_for, session, flash
import csv, os, re

app = Flask(__name__)
app.secret_key = "sua_chave_secreta"

# Caminho do arquivo CSV onde os dados serão salvos
ARQUIVO_CSV = "leads.csv"

@app.route("/", methods=["GET", "POST"])
def index():
    if request.method == "POST":
        nome = request.form['nome'].strip()
        telefone = request.form['telefone'].strip()
        email = request.form['email'].strip()
        servico = request.form.get("servico")
        
        erros = []
        if not telefone.isdigit() or not (10 <= len(telefone) <= 15):
            erros.append("Número de telefone inválido. Informe apenas números com DDD, exemplo: 11999999999.")

        padrao_email = r"^[\w\.-]+@[\w\.-]+\.\w+$"
        if not re.match(padrao_email, email):
            erros.append("E-mail inválido.")
            
        if erros:
            for erro in erros:
                flash(erro, "danger")
            return redirect(url_for("index"))
        
        # Salvar os dados no CSV
        salvar_dados_csv(nome, telefone, email, servico)
        
        session["nome"] = nome
        
        # Redirecionar para a página de agradecimento com o nome como parâmetro
        return redirect(url_for('obrigado'))
        
    return render_template('formulario.html')

@app.route("/obrigado")
def obrigado():
    nome = session.get("nome", "Cliente")
    whatsapp = "(61) 999999999"  # Altere para seu número real
    return render_template(
        "obrigado.html", 
        nome=nome, 
        whatsapp=whatsapp
        )

@app.route("/login", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        usuario = request.form["usuario"]
        senha = request.form["senha"]
        if usuario == "admin" and senha == "1234":  # Altere depois
            session["logado"] = True
            return redirect(url_for("admin"))
        else:
            flash("login Inválido.", "danger")
            return redirect(url_for("login"))
    return render_template("login.html")

@app.route("/admin")
def admin():
    if not session.get("logado"):
        return redirect(url_for("login"))
    
    leads = []
    if os.path.exists(ARQUIVO_CSV):
        with open(ARQUIVO_CSV, newline='', encoding='utf-8') as f:
            reader = csv.reader(f)
            cabecalho = next(reader)
            for row in reader:
                leads.append(row)
    else:
        cabecalho = []
    
    return render_template("admin.html", cabecalho=cabecalho, leads=leads)

@app.route("/excluir/<int:index>", methods=["POST"])
def excluir(index):
    if not session.get("logado"):
        return redirect(url_for("login"))

    linhas = []

    with open(ARQUIVO_CSV, newline='', encoding='utf-8') as f:
        reader = csv.reader(f)
        cabecalho = next(reader)
        linhas = list(reader)

    if 0 <= index < len(linhas):
        del linhas[index]
        with open(ARQUIVO_CSV, "w", newline='', encoding='utf-8') as f:
            writer = csv.writer(f)
            writer.writerow(cabecalho)
            writer.writerows(linhas)
        flash("Registro excluído com sucesso!", "success")
    else:
        flash("Índice inválido.", "danger")

    return redirect(url_for("admin"))

@app.route("/logout")
def logout():
    session.clear()
    return redirect(url_for("login"))

def salvar_dados_csv(nome, telefone, email, servico):
    # Se o arquivo não existir, cria com cabeçalho
    arquivo_existe = os.path.exists(ARQUIVO_CSV)
    with open(ARQUIVO_CSV, "a", newline='', encoding='utf-8') as csvfile:
        writer = csv.writer(csvfile)
        if not arquivo_existe:
            writer.writerow(["Nome", "Telefone", "Email", "Serviço"])
        writer.writerow([nome, telefone, email, servico])

if __name__ == "__main__":
    app.run(debug=True)

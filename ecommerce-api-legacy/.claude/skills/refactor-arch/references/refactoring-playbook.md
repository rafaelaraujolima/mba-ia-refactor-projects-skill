# Playbook de Refatoração

Um padrão de transformação para cada família de anti-pattern do catálogo, cada um com um exemplo
antes/depois. Os exemplos são mostrados em Python/Flask e Node/Express, já que são as stacks que
você mais vai encontrar, mas a *transformação* é o que importa — aplique a mesma forma seja qual
for a linguagem que você estiver de fato refatorando.

---

## 1. Extrair segredos hardcoded para config baseada em variáveis de ambiente

Corrige o #1 do catálogo (Credenciais e Segredos Hardcoded).

**Antes**
```python
app.config["SECRET_KEY"] = "minha-chave-super-secreta-123"
app.config["DEBUG"] = True
```

**Depois**
```python
# config/settings.py
import os

SECRET_KEY = os.environ.get("SECRET_KEY")
DEBUG = os.environ.get("FLASK_DEBUG", "false").lower() == "true"

if not SECRET_KEY:
    raise RuntimeError("SECRET_KEY environment variable is required")
```
```python
# app.py
from config import settings
app.config["SECRET_KEY"] = settings.SECRET_KEY
app.config["DEBUG"] = settings.DEBUG
```
Adicione um `.env.example` (não um `.env`) listando os nomes de variável exigidos com valores
placeholder, e adicione `.env` ao `.gitignore` se uma abordagem de carregar `.env`
(`python-dotenv`, `--env-file` embutido do Node, ou `dotenv`) for usada localmente. Nunca commite
um valor de segredo real, incluindo um "corrigido".

---

## 2. Parametrizar toda query

Corrige o #2 do catálogo (SQL Injection).

**Antes**
```python
cursor.execute("SELECT * FROM produtos WHERE id = " + str(id))
```
```python
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha) VALUES ('" + nome + "', '" + email + "', '" + senha + "')"
)
```

**Depois**
```python
cursor.execute("SELECT * FROM produtos WHERE id = ?", (id,))
```
```python
cursor.execute(
    "INSERT INTO usuarios (nome, email, senha) VALUES (?, ?, ?)",
    (nome, email, senha_hash),
)
```
Equivalente em Node/`sqlite3` — o driver já suporta placeholders; o bug é não usá-los:
```javascript
// Antes
db.run(`DELETE FROM users WHERE id = ${id}`);

// Depois
db.run("DELETE FROM users WHERE id = ?", [id]);
```
Se existir um endpoint de query crua (aceitando SQL arbitrário vindo da requisição), remova-o por
completo — nenhuma parametrização torna seguro "rodar qualquer SQL que o cliente mandar". Deixe
explícito no relatório/refatoração que você removeu esse endpoint, não apenas modificou.

---

## 3. Dividir um God File em Models e Controllers por domínio

Corrige o #3 do catálogo (God Class / God File).

**Antes**: `models.py` (350 linhas) contém funções de query + formatação para produtos, usuários
*e* pedidos, tudo misturado, importado por inteiro em `controllers.py`.

**Depois**: um módulo de model por domínio, cada um dono apenas do acesso a dados daquele domínio:
```
models/
├── produto_model.py     # get_all(), get_by_id(), create(), update(), delete(), search()
├── usuario_model.py     # get_all(), get_by_id(), create(), authenticate()
└── pedido_model.py      # create(), get_all(), get_by_user(), update_status()
```
```python
# models/produto_model.py
def get_by_id(id):
    db = get_db()
    row = db.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
    return dict(row) if row else None
```
E um controller correspondente por domínio que chama apenas seu próprio model mais qualquer outro
model que uma operação genuinamente entre entidades precise (ex.: `pedido_controller.py`
legitimamente chama tanto `pedido_model` quanto `produto_model` para checar estoque — isso é
orquestração, não um God File, desde que viva em uma função de controller claramente delimitada).

Para uma God *Class* que mistura setup de banco + roteamento + lógica (comum na forma "Manager" do
Node): quebre o setup de banco do construtor em um módulo `models/db.js`, mova o corpo de cada
handler de rota para uma função de controller, e deixe a classe/arquivo de registro de rotas sem
fazer nada além da conexão entre as peças.

---

## 4. Substituir tratamento de senha fraco/texto puro por um hash de verdade

Corrige o #4 do catálogo (Hashing de Senha Fraco ou Ausente).

**Antes**
```python
def login_usuario(email, senha):
    cursor.execute("SELECT * FROM usuarios WHERE email = ? AND senha = ?", (email, senha))
```
```python
def set_password(self, pwd):
    self.password = hashlib.md5(pwd.encode()).hexdigest()
```

**Depois** (Flask — `werkzeug.security`, já é dependência do Flask, sem pacote novo necessário)
```python
from werkzeug.security import generate_password_hash, check_password_hash

def set_password(self, pwd):
    self.password = generate_password_hash(pwd)

def check_password(self, pwd):
    return check_password_hash(self.password, pwd)
```
```python
def login_usuario(email, senha):
    usuario = get_usuario_by_email(email)
    if usuario and check_password_hash(usuario["senha_hash"], senha):
        return usuario
    return None
```
Equivalente em Node: trocar um `badCrypto()` caseiro por `bcrypt`:
```javascript
const bcrypt = require('bcrypt');
const hash = await bcrypt.hash(plainPassword, 10);
const ok = await bcrypt.compare(candidate, storedHash);
```
Linhas existentes com senha em texto puro/hash fraco não podem ser migradas automaticamente (você
não tem o texto puro para linhas em MD5) — registre no resumo da auditoria/refatoração que os
usuários existentes vão precisar resetar a senha, em vez de fingir silenciosamente que as linhas
antigas agora estão seguras.

---

## 5. Mover lógica de negócio de Controllers/Routes para Models/Services

Corrige o #5 do catálogo (Lógica de Negócio Presa em Controllers).

**Antes** (rota fazendo validação + cálculo + persistência inline)
```python
@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    total = Task.query.count()
    done = Task.query.filter_by(status='done').count()
    ...
    stats = {'completion_rate': round((done / total) * 100, 2) if total > 0 else 0, ...}
    return jsonify(stats), 200
```

**Depois**
```python
# models/task.py
class Task(db.Model):
    ...
    @staticmethod
    def compute_stats():
        total = Task.query.count()
        done = Task.query.filter_by(status='done').count()
        completion_rate = round((done / total) * 100, 2) if total > 0 else 0
        return {"total": total, "done": done, "completion_rate": completion_rate, ...}
```
```python
# controllers/task_controller.py
def get_task_stats():
    return Task.compute_stats()
```
```python
# routes/task_routes.py
@task_bp.route('/tasks/stats', methods=['GET'])
def task_stats():
    return jsonify(task_controller.get_task_stats()), 200
```
A rota agora tem três linhas: chamar o controller, devolver o que ele retornar. Essa é a forma
alvo para todo route handler.

---

## 6. Adicionar autenticação/autorização de verdade

Corrige o #6 do catálogo (Autenticação Ausente ou Falsa).

**Antes**: `/admin/reset-db` e `/admin/query` acessíveis por qualquer um; o login retorna
`"fake-jwt-token-" + str(user.id)`, que nada nunca verifica de novo.

**Depois** — emitir e verificar um token de verdade, e proteger rotas sensíveis com ele:
```python
# controllers/auth_controller.py
import jwt
from config import settings

def issue_token(user):
    return jwt.encode({"sub": user["id"], "role": user["tipo"]}, settings.SECRET_KEY, algorithm="HS256")

def require_auth(role=None):
    def decorator(view):
        @wraps(view)
        def wrapper(*args, **kwargs):
            token = request.headers.get("Authorization", "").removeprefix("Bearer ")
            try:
                payload = jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
            except jwt.InvalidTokenError:
                return jsonify({"erro": "Não autorizado"}), 401
            if role and payload.get("role") != role:
                return jsonify({"erro": "Acesso negado"}), 403
            return view(*args, **kwargs)
        return wrapper
    return decorator
```
```python
@app.route("/admin/reset-db", methods=["POST"])
@require_auth(role="admin")
def reset_database():
    ...
```
Se o propósito inteiro de um endpoint já era inseguro por design (execução de SQL arbitrário), o
fix correto é remover, não apenas proteger com auth — colocar uma capacidade inerentemente
perigosa atrás de autenticação ainda deixa essa capacidade inerentemente perigosa.

---

## 7. Substituir estado global mutável por injeção de dependência

Corrige o #7 do catálogo (Forte Acoplamento / Sem DI).

**Antes**
```python
db_connection = None

def get_db():
    global db_connection
    if db_connection is None:
        db_connection = sqlite3.connect(db_path)
    return db_connection
```
Toda função de model chama `get_db()` diretamente — nenhuma função pode ser testada sem um arquivo
SQLite real, e nada pode substituir um banco em memória para os testes.

**Depois**
```python
# config/db.py
def create_connection(db_path):
    conn = sqlite3.connect(db_path, check_same_thread=False)
    conn.row_factory = sqlite3.Row
    return conn
```
```python
# app.py (composition root)
db = create_connection(settings.DB_PATH)
```
```python
# models/produto_model.py
def get_by_id(db, id):
    return db.execute("SELECT * FROM produtos WHERE id = ?", (id,)).fetchone()
```
A conexão é criada uma única vez no startup e passada para quem precisar dela (diretamente, via um
helper com escopo de requisição, ou via um pequeno acessor de contexto de aplicação para frameworks
que suportam isso) — a diferença em relação à versão "antes" é que nada mais *cria* sua própria
dependência internamente; tudo passa a recebê-la.

---

## 8. Converter pirâmides de callback em async/await

Corrige o #8 do catálogo (Fluxo Assíncrono Desestruturado).

**Antes**
```javascript
this.db.get("SELECT * FROM courses WHERE id = ?", [cid], (err, course) => {
    this.db.get("SELECT id FROM users WHERE email = ?", [e], (err, user) => {
        this.db.run("INSERT INTO enrollments ...", [userId, cid], function(err) {
            self.db.run("INSERT INTO payments ...", [enrId, course.price, status], function(err) {
                res.json({ msg: "Sucesso" });
            });
        });
    });
});
```

**Depois** (promisifique o driver uma vez, depois use async/await em todo lugar)
```javascript
// models/db.js
const { promisify } = require('util');
const dbGet = promisify(db.get.bind(db));
const dbRun = promisify(db.run.bind(db));
```
```javascript
// controllers/checkoutController.js
async function checkout(courseId, email, card) {
    const course = await courseModel.findActiveById(courseId);
    if (!course) throw new NotFoundError("Curso não encontrado");

    let user = await userModel.findByEmail(email);
    if (!user) user = await userModel.create({ email, ... });

    const enrollment = await enrollmentModel.create(user.id, courseId);
    const payment = await paymentModel.create(enrollment.id, course.price, status);
    return { enrollmentId: enrollment.id };
}
```
```javascript
// routes/checkoutRoutes.js
router.post('/api/checkout', async (req, res, next) => {
    try {
        const result = await checkoutController.checkout(req.body.c_id, req.body.eml, req.body.card);
        res.status(200).json(result);
    } catch (err) {
        next(err);  // middleware de erro centralizado trata a forma da resposta
    }
});
```
O padrão manual de contador pendente para coordenar operações paralelas (`coursesPending--`)
vira `await Promise.all(items.map(item => process(item)))`.

---

## 9. Corrigir queries N+1 com uma busca em lote

Corrige o #9 do catálogo (Queries N+1).

**Antes**
```python
for row in pedidos:
    cursor2.execute("SELECT * FROM itens_pedido WHERE pedido_id = ?", (row["id"],))
    for item in cursor2.fetchall():
        cursor3.execute("SELECT nome FROM produtos WHERE id = ?", (item["produto_id"],))
```

**Depois**
```python
pedido_ids = [row["id"] for row in pedidos]
placeholders = ",".join("?" * len(pedido_ids))
itens = db.execute(
    f"SELECT * FROM itens_pedido WHERE pedido_id IN ({placeholders})", pedido_ids
).fetchall()

produto_ids = {item["produto_id"] for item in itens}
placeholders = ",".join("?" * len(produto_ids))
produtos_by_id = {
    row["id"]: row["nome"]
    for row in db.execute(
        f"SELECT id, nome FROM produtos WHERE id IN ({placeholders})", list(produto_ids)
    ).fetchall()
}
# depois junte as três coleções em memória por id em vez de consultar por linha
```
Com um ORM, o mesmo fix costuma ser um eager-load de uma linha:
`Task.query.options(joinedload(Task.user))` em vez de acessar `t.user` de forma lazy dentro de um
loop.

---

## 10. Extrair lógica duplicada para uma única função/método compartilhado

Corrige o #10 do catálogo (Lógica/Validação Duplicada).

**Antes**: a mesma checagem aninhada de if/else "essa task está atrasada" copiada e colada em três
route handlers e também no próprio model.

**Depois**: mantenha exatamente uma implementação, no model, e faça todo chamador usá-la:
```python
# models/task.py
class Task(db.Model):
    @property
    def is_overdue(self):
        return bool(
            self.due_date
            and self.due_date < datetime.now(timezone.utc)
            and self.status not in ("done", "cancelled")
        )
```
```python
# todo lugar que antes recalculava isso:
task_data["overdue"] = task.is_overdue
```
Note a limpeza secundária que vem de graça aqui: o if/else aninhado de nove linhas colapsa em uma
única expressão booleana — duplicação e complexidade desnecessária costumam ser o mesmo fix.

---

## 11. Substituir APIs deprecated pelo equivalente moderno

Corrige o #11 do catálogo (APIs Deprecated / Obsoletas).

**Antes**
```python
created_at = db.Column(db.DateTime, default=datetime.utcnow)
```
```javascript
const bodyParser = require('body-parser');
app.use(bodyParser.json());
```

**Depois**
```python
created_at = db.Column(db.DateTime, default=lambda: datetime.now(timezone.utc))
```
```javascript
app.use(express.json());  // embutido no Express desde a 4.16, sem dependência extra necessária
```
Remova do manifesto (`requirements.txt`/`package.json`) a dependência agora não usada, quando um
pacote deprecated for descartado em favor de um embutido ou de uma alternativa atualizada — uma
dependência obsoleta esquecida no manifesto é, por si só, um pequeno finding.

---

## 12. Centralizar o tratamento de erro

Corrige o #12 do catálogo (Validação Ausente no Nível de Rota / Middleware Inadequado).

**Antes**: cada controller tem seu próprio `try/except Exception as e: return jsonify({"erro":
str(e)}), 500`, com nomes de chave inconsistentes e sem nenhum log.

**Depois**
```python
# middlewares/error_handler.py
class AppError(Exception):
    def __init__(self, message, status_code=400):
        self.message = message
        self.status_code = status_code

def register_error_handlers(app):
    @app.errorhandler(AppError)
    def handle_app_error(e):
        return jsonify({"error": e.message}), e.status_code

    @app.errorhandler(Exception)
    def handle_unexpected(e):
        app.logger.exception("Unhandled error")
        return jsonify({"error": "Internal server error"}), 500
```
Os controllers agora fazem `raise AppError("Produto não encontrado", 404)` em vez de montar a
resposta inline, e a forma de toda resposta de erro passa a ser consistente de graça.

---

## 13. Substituir números mágicos/logging via print por constantes e um logger de verdade

Corrige os #13 e #14 do catálogo (Nomenclatura Ruim/Números Mágicos, Logging Orientado a Debug).

**Antes**
```python
if faturamento > 10000:
    desconto = faturamento * 0.1
elif faturamento > 5000:
    desconto = faturamento * 0.05
print("ERRO ao criar produto: " + str(e))
```

**Depois**
```python
# constants.py
DISCOUNT_TIERS = [(10_000, 0.10), (5_000, 0.05), (1_000, 0.02)]
```
```python
import logging
logger = logging.getLogger(__name__)
...
logger.error("Erro ao criar produto", exc_info=e)
```
`logger` respeita níveis de log e pode ser silenciado/redirecionado em produção, ao contrário de
`print`, o que também corrige o code smell de flag de debug ligada quando combinado com o padrão
#1 (o config agora controla o nível de log em vez de `debug=True` ser o único interruptor).

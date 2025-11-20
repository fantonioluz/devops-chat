# DevOps Learning Chat v2.0 🚀

Chat educacional sobre DevOps com Google OAuth, múltiplos modelos de IA (Gemini + OpenRouter) e histórico de conversas salvo em PostgreSQL.

## 🆕 v2.0 - Novidades

- ✅ **Login Google** - Autenticação segura via OAuth 2.0  
- ✅ **PostgreSQL** - Banco de dados para usuários e conversas
- ✅ **OpenRouter** - Acesso a GPT, Claude, Llama e mais modelos
- ✅ **Histórico** - Todas conversas salvas e recuperáveis
- ✅ **Seleção de Modelo** - Escolha entre vários modelos de IA

## 🚀 Quick Start

### 1. Configure as APIs

**Google OAuth** (https://console.cloud.google.com/):
- Crie projeto → APIs & Services → Credentials
- OAuth 2.0 Client ID (Web application)
- Authorized origins: `http://localhost:3000`

**OpenRouter** (https://openrouter.ai/):  
- Crie conta → Keys → Generate API Key
- Tier gratuito disponível!

### 2. Configure o `.env`

```bash
cp .env.example .env
```

Edite o `.env`:
```env
GEMINI_API_KEY=sua_chave_gemini
OPENROUTER_API_KEY=sua_chave_openrouter
GOOGLE_CLIENT_ID=seu_google_client_id  
JWT_SECRET_KEY=uma-senha-segura-aqui
```

### 3. Execute

```bash
docker-compose up --build
```

Acesse: http://localhost:3000

## 📚 API Endpoints

### Auth
- `POST /auth/google` - Login com token do Google
- `GET /auth/me` - Info do usuário

### Chat  
- `POST /chat` - Enviar mensagem (opcional: conversation_id, model)
- `GET /models` - Listar modelos disponíveis

### Conversas (Autenticado)
- `GET /conversations` - Listar suas conversas
- `GET /conversations/{id}` - Ver conversa completa
- `DELETE /conversations/{id}` - Deletar conversa

## 🤖 Modelos Disponíveis

### Gemini (Google - Grátis)
- `gemini-2.5-flash` ⚡ - Rápido, ideal para produção
- `gemini-2.5-pro` 🧠 - Raciocínio avançado

### OpenRouter (Vários provedores)
- `openai/gpt-4o` - GPT-4 Optimized
- `openai/gpt-3.5-turbo` - Econômico
- `anthropic/claude-3.5-sonnet` - Claude 3.5
- `meta-llama/llama-3.3-70b-instruct` - Llama 3.3 (FREE!)

## 🏗️ Arquitetura

```
├── backend/          # FastAPI + SQLAlchemy + PostgreSQL
│   ├── main.py      # API endpoints
│   ├── models.py    # DB models (User, Conversation, Message)
│   ├── auth.py      # JWT + Google OAuth
│   ├── ai_service.py # Gemini + OpenRouter
│   └── database.py  # PostgreSQL config
├── frontend/        # React + Vite + Google OAuth
└── docker-compose.yml # PostgreSQL + Backend + Frontend
```

## 📊 Banco de Dados

```
users → conversations → messages
```

- **users**: google_id, email, name, picture
- **conversations**: user_id, title, model
- **messages**: conversation_id, role, content

## 🧪 Testes

```bash
# Backend
cd backend && pytest -v --cov

# Frontend  
cd frontend && npm test
```

## 📦 Deploy (Railway)

1. Crie 3 serviços: PostgreSQL, Backend (Python), Frontend (Static)
2. Configure variáveis: `GEMINI_API_KEY`, `OPENROUTER_API_KEY`, `GOOGLE_CLIENT_ID`, `JWT_SECRET_KEY`
3. GitHub Actions faz deploy automático (staging/main)

## 🔒 Segurança

- JWT tokens (7 dias de validade)
- OAuth 2.0 (sem senhas armazenadas)
- CORS configurado
- SQLAlchemy ORM (proteção contra SQL injection)

## 💡 Como Usar

1. **Login** → Botão "Login com Google"
2. **Escolha o Modelo** → Dropdown no chat
3. **Converse** → Pergunte sobre DevOps!
4. **Histórico** → Sidebar com conversas salvas

## 🛠️ Tecnologias

**Backend**: FastAPI • PostgreSQL • SQLAlchemy • JWT • Google AI • OpenRouter  
**Frontend**: React • Vite • Axios • @react-oauth/google  
**DevOps**: Docker • Docker Compose • GitHub Actions • Railway

## 📝 Exemplo de Uso

```python
import requests

# 1. Login
resp = requests.post('http://localhost:8000/auth/google', 
                     json={'token': 'GOOGLE_ID_TOKEN'})
token = resp.json()['access_token']

# 2. Chat
resp = requests.post('http://localhost:8000/chat',
    headers={'Authorization': f'Bearer {token}'},
    json={
        'messages': [{'role': 'user', 'content': 'O que é Docker?'}],
        'model': 'gemini-2.5-flash'
    })
print(resp.json()['response'])
```

## 🔄 Changelog

**v2.0.0** (Nov 2025)
- Google OAuth authentication
- OpenRouter integration
- PostgreSQL database
- Conversation history
- Multiple AI models

**v1.0.0** (Nov 2025)  
- Initial release with Gemini

## 📄 Licença

MIT

---

Made with ❤️ for DevOps students

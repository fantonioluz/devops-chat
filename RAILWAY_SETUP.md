# 🚀 Deploy com Docker Compose no Railway

## Arquitetura Simplificada

**Antes:** 3 serviços separados (backend, frontend, db)  
**Agora:** 1 serviço único com Docker Compose

## ✅ Vantagens

- ✨ **Mais simples** - Um único serviço para gerenciar
- 💰 **Mais barato** - Custo de 1 serviço ao invés de 3
- 🔄 **Paridade dev/prod** - Mesma configuração local e produção
- 🗄️ **Banco incluído** - PostgreSQL sobe automaticamente
- 🌐 **Network funciona** - Comunicação entre serviços garantida

## 📋 Setup no Railway

### 1. Criar Projeto
1. Acesse [railway.app](https://railway.app)
2. Clique em **New Project**
3. Escolha **Deploy from GitHub repo**
4. Selecione o repositório `devops-chat`
5. Railway detectará o `railway.toml` automaticamente

### 2. Configurar Variáveis de Ambiente

No Railway, adicione essas variáveis no seu serviço:

```env
# APIs de IA
GEMINI_API_KEY=sua_chave_do_gemini
OPENROUTER_API_KEY=sua_chave_do_openrouter

# Segurança
JWT_SECRET_KEY=um_secret_bem_seguro_aqui

# Google OAuth (se usar)
VITE_GOOGLE_CLIENT_ID=seu_client_id_do_google

# Frontend - URL da API (Railway fornece automaticamente)
VITE_API_URL=https://seu-app.railway.app

# CORS - Domínio do Railway
CORS_ORIGINS=https://seu-app.railway.app

# Banco (já configurado no docker-compose.yml, não precisa alterar)
# POSTGRES_USER=devops_user
# POSTGRES_PASSWORD=devops_password
# POSTGRES_DB=devops_chat
```

### 3. Configurar Domínio

O Railway fornecerá um domínio automático tipo:
- `https://devops-chat-production.up.railway.app`

Você pode configurar um domínio customizado depois.

### 4. Portas Expostas

O Railway detectará automaticamente:
- **Frontend:** Porta 3000
- **Backend API:** Porta 8000

## 🔄 Como Funciona o Deploy

### Deploy Automático

Quando você fizer push para:
- **`staging` branch** → Deploy automático no ambiente staging
- **`main` branch** → Deploy automático no ambiente production

### Deploy Manual (via CLI)

```bash
# Instalar Railway CLI
npm install -g @railway/cli

# Login
railway login

# Link ao projeto
railway link

# Deploy
railway up
```

## 🗄️ Banco de Dados

O PostgreSQL é gerenciado pelo Docker Compose:

- **Volume persistente** - Dados não são perdidos entre deploys
- **Healthcheck** - Backend só inicia quando DB está pronto
- **Backup** - Configure backups periódicos no Railway

### Acessar o banco

```bash
# Via Railway CLI
railway run psql -U devops_user -d devops_chat
```

## 📊 Monitoramento

No Railway você pode ver:
- Logs em tempo real de todos os containers
- Métricas de CPU e memória
- Status de saúde via `/health` endpoint

## 🔐 Secrets do GitHub Actions

Configure no GitHub (Settings → Secrets):

```
RAILWAY_TOKEN_STAGING=<token_do_railway>
RAILWAY_TOKEN_PRODUCTION=<token_do_railway>
GEMINI_API_KEY=<sua_chave>
```

### Obter Railway Token

```bash
railway login
railway tokens
```

## 🐛 Troubleshooting

### Container não inicia
```bash
railway logs
```

### Banco não conecta
Verifique se o healthcheck do PostgreSQL está OK:
```bash
railway run docker-compose ps
```

### Frontend não encontra backend
Verifique as variáveis `VITE_API_URL` e `CORS_ORIGINS`

## 📝 Estrutura de Arquivos

```
devops-chat/
├── docker-compose.yml      # Orquestra todos os serviços
├── railway.toml           # Config do Railway (raiz)
├── .dockerignore          # Otimiza o build
├── backend/
│   ├── Dockerfile
│   └── ...
└── frontend/
    ├── Dockerfile
    └── ...
```

## 🎯 Próximos Passos

1. ✅ Fazer commit das alterações
2. ✅ Push para `dev`
3. ✅ Criar projeto no Railway
4. ✅ Configurar variáveis de ambiente
5. ✅ Fazer merge para `staging` ou `main`
6. ✅ Acompanhar o deploy via GitHub Actions
7. ✅ Verificar logs no Railway

---

**Pronto!** 🎉 Seu projeto está configurado para deploy simplificado com Docker Compose!

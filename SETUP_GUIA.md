# 🚦 Ordem de Configuração - Passo a Passo

## Status Atual ✅

- ✅ Workflows de teste funcionando
- ✅ Build do Docker Compose funcionando
- ⏸️ Deploys desabilitados (até configurar Railway)

## 📋 Escolha seu caminho:

### Opção 1: 🐳 Desenvolvimento Local (Recomendado para começar)

Use Docker Compose localmente sem Railway:

```powershell
# 1. Testar localmente
docker compose up --build

# 2. Acessar
# Frontend: http://localhost:3000
# Backend: http://localhost:8000
# Docs API: http://localhost:8000/docs
```

**Vantagens:**
- ✅ Grátis
- ✅ Rápido para testar
- ✅ Controle total
- ✅ Debugar facilmente

---

### Opção 2: ☁️ Deploy no Railway (Para produção)

Siga esta ordem **exatamente**:

#### **Passo 1: Criar Ambientes no GitHub**
```
1. GitHub → Seu repositório → Settings → Environments
2. Criar "staging"
3. Criar "production"
```

#### **Passo 2: Criar Projeto no Railway**
```
1. Acesse https://railway.app
2. Login com GitHub
3. New Project → Deploy from GitHub repo
4. Selecione "devops-chat"
5. Railway vai criar 3 serviços (mas vamos usar só 1)
```

#### **Passo 3: Simplificar para 1 Serviço**
```
No Railway dashboard:
1. Delete os serviços "backend" e "frontend" (se criados)
2. Mantenha apenas 1 serviço
3. Configure para usar Docker Compose:
   - Settings → Build → Docker Compose
   - Root Directory: /
```

#### **Passo 4: Configurar Variáveis no Railway**
```
No serviço único, adicione:

GEMINI_API_KEY=sua_chave_aqui
OPENROUTER_API_KEY=sua_chave_aqui
JWT_SECRET_KEY=troque-isso-por-algo-seguro-em-producao
VITE_GOOGLE_CLIENT_ID=seu_client_id
VITE_API_URL=https://seu-dominio.railway.app
CORS_ORIGINS=https://seu-dominio.railway.app
```

#### **Passo 5: Obter Token do Railway**
```bash
npm install -g @railway/cli
railway login
railway tokens create
# Copie o token gerado
```

#### **Passo 6: Configurar Secrets no GitHub**
```
GitHub → Settings → Secrets → Actions → New secret

RAILWAY_TOKEN_STAGING=<seu-token>
RAILWAY_TOKEN_PRODUCTION=<seu-token>
GEMINI_API_KEY=<sua-chave>
```

#### **Passo 7: Habilitar Deploys Automáticos**

Edite os workflows:

**`.github/workflows/deploy-staging.yml`:**
```yaml
on:
  push:
    branches: [ staging ]
  # Remova: workflow_dispatch
```

**`.github/workflows/deploy-production.yml`:**
```yaml
on:
  push:
    branches: [ main ]
  # Remova: workflow_dispatch
```

Descomente também:
```yaml
environment: staging  # ou production
```

---

## 🎯 Recomendação

**Comece com Opção 1** (Local):
1. Teste tudo localmente
2. Certifique-se que funciona 100%
3. Depois vá para Railway (Opção 2)

---

## 🧪 Testar Workflows Agora

Os workflows funcionam assim:

### ✅ Test Pipeline (Automático)
- Roda em: PRs e pushes para `staging`/`main`
- Testa: Backend + Frontend
- Status: **FUNCIONANDO** ✅

### ✅ Build Pipeline (Automático)
- Roda em: Push para `staging`/`main`
- Testa: Build do Docker Compose
- Status: **FUNCIONANDO** ✅

### ⏸️ Deploy Pipelines (Manual)
- Roda em: Apenas manual (workflow_dispatch)
- Deploy: Railway (Docker Compose)
- Status: **DESABILITADO** até Railway estar pronto

Para testar deploy manualmente:
```
GitHub → Actions → Deploy to Staging → Run workflow
```

---

## 🐛 Troubleshooting

### Workflow de teste falha
```bash
# Rode localmente primeiro
cd backend
pytest test_main.py -v
```

### Build falha
```bash
# Teste o build local
docker compose build
```

### Deploy falha
```bash
# Verifique:
1. Railway está configurado?
2. Token está correto nos Secrets?
3. Serviço único existe no Railway?
```

---

## ✅ Checklist Rápido

**Para rodar local:**
- [ ] Tem Docker instalado
- [ ] Copiou o `.env` com suas chaves
- [ ] `docker compose up`

**Para Railway:**
- [ ] Ambientes criados no GitHub
- [ ] Projeto criado no Railway
- [ ] 1 serviço configurado (não 3)
- [ ] Variáveis configuradas
- [ ] Token nos GitHub Secrets
- [ ] Workflows descomentados

---

**Qual opção você quer seguir primeiro?** 🎯

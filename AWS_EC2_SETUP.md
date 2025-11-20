# 🚀 Deploy Automatizado na AWS EC2

## 📋 Visão Geral

Deploy totalmente automatizado via GitHub Actions. O código nunca precisa ser clonado na EC2.

**Como funciona:**
1. GitHub Actions builda as imagens Docker
2. Faz push para Docker Hub
3. Copia docker-compose.prod.yml para EC2
4. EC2 faz pull das imagens e sobe os containers

**Vantagens:**
- ✅ Deploy 100% automatizado
- ✅ Sem necessidade de clonar repositório na EC2
- ✅ Rollback fácil (muda a tag da imagem)
- ✅ Consistente entre ambientes

---

## 🎯 Passo a Passo Completo

### **1. Criar Conta no Docker Hub**

1. Acesse [hub.docker.com](https://hub.docker.com)
2. Crie uma conta gratuita
3. Crie um Access Token:
   - **Account Settings** → **Security** → **New Access Token**
   - Nome: `github-actions`
   - Copie o token (você não verá novamente!)

---

### **2. Criar Instância EC2**

#### 1.1 No AWS Console

1. Acesse **EC2 Dashboard**
2. Clique em **Launch Instance**

#### 1.2 Configurações Recomendadas

**Basic Details:**
- **Name:** `devops-chat-staging` (ou `production`)
- **AMI:** Ubuntu Server 22.04 LTS
- **Instance type:** `t2.medium` (2 vCPU, 4GB RAM) ou maior
- **Storage:** 30 GB gp3 (mínimo)

**Key pair:**
- Crie um novo par de chaves: `devops-chat-key`
- Formato: `.pem`
- **IMPORTANTE:** Baixe e guarde o arquivo `.pem` com segurança!

**Network settings:**
- **VPC:** Default ou crie uma nova
- **Auto-assign public IP:** Enable
- **Firewall (Security Group):**
  ```
  Nome: devops-chat-sg
  
  Inbound rules:
  - SSH (22) - Seu IP ou GitHub Actions IPs
  - HTTP (80) - 0.0.0.0/0
  - HTTPS (443) - 0.0.0.0/0
  - Custom TCP (8000) - 0.0.0.0/0 (Backend API)
  - Custom TCP (3000) - 0.0.0.0/0 (Frontend)
  ```

#### 1.3 Launch

- Clique em **Launch instance**
- Anote o **Public IPv4 address** (ex: `54.123.45.67`)

---

### **2. Preparar a Instância EC2**

#### 2.1 Conectar via SSH

```bash
# No seu terminal local
chmod 400 devops-chat-key.pem
ssh -i devops-chat-key.pem ubuntu@54.123.45.67
```

#### 2.2 Instalar Docker

```bash
# Atualizar sistema
sudo apt update
sudo apt upgrade -y

# Instalar Docker
curl -fsSL https://get.docker.com -o get-docker.sh
sudo sh get-docker.sh

# Adicionar usuário ao grupo docker (IMPORTANTE!)
sudo usermod -aG docker ubuntu

# Instalar Docker Compose
sudo apt install docker-compose-plugin -y

# Configurar permissões para sudo sem senha (necessário para deploy automatizado)
echo "ubuntu ALL=(ALL) NOPASSWD: /usr/bin/docker, /usr/bin/docker-compose" | sudo tee /etc/sudoers.d/docker

# Logout e login novamente para aplicar mudanças de grupo
exit
```

#### 2.3 Conectar novamente e testar

```bash
ssh -i devops-chat-key.pem ubuntu@54.123.45.67

# Verificar instalação
docker --version
docker compose version
```

#### 2.4 Primeiro teste (opcional)

```bash
# Criar diretório de trabalho
mkdir -p ~/app
cd ~/app

# Testar Docker
docker run hello-world
```

---

### **3. Configurar Docker Hub no GitHub**

#### 3.1 Adicionar Secrets no GitHub

Acesse: **GitHub → Repositório → Settings → Secrets and variables → Actions**

Clique em **New repository secret** e adicione:

```
DOCKER_USERNAME=seu_usuario_dockerhub
DOCKER_PASSWORD=seu_token_do_dockerhub
```

---

### **4. Configurar Secrets da AWS EC2**

Adicione mais secrets no GitHub:

Adicione mais secrets no GitHub:

```
# EC2 Connection
EC2_USER=ubuntu
EC2_SSH_KEY=<conteúdo-completo-do-arquivo-.pem>
EC2_HOST_STAGING=54.123.45.67
EC2_HOST_PRODUCTION=54.123.45.68  (se tiver)

# Application Secrets
GEMINI_API_KEY=sua_chave_gemini
OPENROUTER_API_KEY=sua_chave_openrouter
POSTGRES_PASSWORD=senha_segura_do_postgres

# Staging Environment
JWT_SECRET_KEY_STAGING=chave_jwt_super_segura_staging
CORS_ORIGINS_STAGING=http://54.123.45.67
VITE_API_URL=http://54.123.45.67:8000
VITE_GOOGLE_CLIENT_ID=seu_google_client_id

# Production Environment
JWT_SECRET_KEY_PRODUCTION=chave_jwt_super_segura_production
CORS_ORIGINS_PRODUCTION=http://54.123.45.68
```

**Detalhes:**

- `EC2_SSH_KEY`: Todo o conteúdo do `.pem` (incluindo BEGIN/END)
- `EC2_HOST_*`: IP público da instância EC2
- `CORS_ORIGINS_*`: Domínios permitidos (pode ser http://IP ou https://dominio.com)

---

### **5. Fazer o Primeiro Deploy**

```bash
# No seu computador local
git add .
git commit -m "feat: configurar deploy automatizado AWS"
git push origin staging
```

**O que acontece:**

1. ✅ GitHub Actions builda as imagens
2. ✅ Faz push para Docker Hub
3. ✅ Conecta na EC2 via SSH
4. ✅ Copia docker-compose.prod.yml e .env
5. ✅ Faz pull das imagens
6. ✅ Sobe os containers

**Acompanhar:**
- GitHub → Actions → Deploy to Staging

**Acessar após deploy:**
- Frontend: `http://54.123.45.67`
- Backend: `http://54.123.45.67:8000`
- API Docs: `http://54.123.45.67:8000/docs`

---

## 🔄 Como Funciona o Deploy

### Fluxo Completo

```
1. Push para staging/main
   ↓
2. Build Workflow roda
   - Builda backend image
   - Builda frontend image  
   - Push para Docker Hub
   ↓
3. Deploy Workflow roda
   - Cria arquivo .env com secrets
   - Copia docker-compose.prod.yml via SCP
   - Copia .env via SCP
   - SSH na EC2
   - docker compose pull (baixa imagens)
   - docker compose up -d (sobe containers)
```

### Estrutura na EC2

```
/home/ubuntu/
├── docker-compose.yml (copiado do docker-compose.prod.yml)
└── .env (gerado pelo GitHub Actions)
```

**Não há código-fonte na EC2!** Apenas configuração e containers rodando.

---

## 🔒 Segurança

### Configurações Recomendadas

1. **Elastic IP** - IP fixo ao invés de dinâmico
2. **HTTPS com Let's Encrypt**:
   ```bash
   # Instalar nginx como reverse proxy
   sudo apt install nginx certbot python3-certbot-nginx
   
   # Configurar domínio
   sudo certbot --nginx -d seu-dominio.com
   ```

3. **Security Group** - Apenas portas necessárias
4. **Secrets Manager** - Para variáveis sensíveis em produção
5. **Backup PostgreSQL** - Snapshot automático do volume

---

## 📊 Monitoramento

### Ver logs na EC2

```bash
ssh -i devops-chat-key.pem ubuntu@54.123.45.67

# Logs dos containers
docker compose logs -f
docker compose logs -f backend
docker compose logs -f frontend
docker compose logs -f db
```

### Ver status

```bash
docker compose ps
docker stats
```

### Restart manual

```bash
docker compose restart
docker compose restart backend
```

---

## 🔄 Rollback

Se algo der errado, faça rollback para versão anterior:

```bash
# SSH na EC2
ssh -i devops-chat-key.pem ubuntu@54.123.45.67

# Editar .env e mudar IMAGE_TAG
nano .env
# Mude: IMAGE_TAG=staging para IMAGE_TAG=v1.0.0 (versão anterior)

# Atualizar containers
docker compose pull
docker compose up -d
```

---

## 💰 Custos Estimados

**t2.medium (2 vCPU, 4GB RAM):**
- On-Demand: ~$33/mês
- Reserved (1 ano): ~$23/mês

**Storage 30GB:** ~$2.40/mês

**Total:** ~$25-35/mês por ambiente

**Free Tier:** t2.micro grátis por 12 meses (750h/mês)

---

## 🐛 Troubleshooting

### Build falha no GitHub Actions

```
Erro: "Username and password required"
→ Verificar DOCKER_USERNAME e DOCKER_PASSWORD nos secrets
```

### Deploy falha com "Permission denied"

```
→ Verificar se EC2_SSH_KEY está completo (incluindo BEGIN/END)
→ Verificar se Security Group permite SSH
```

### Container não inicia na EC2

```bash
# Ver logs
docker compose logs -f backend

# Verificar se imagens foram baixadas
docker images

# Verificar .env
cat .env
```

### Sem espaço em disco

```bash
# Limpar imagens antigas
docker system prune -a -f

# Verificar espaço
df -h
```

---

## ✅ Checklist Final

**Docker Hub:**
- [ ] Conta criada
- [ ] Access Token gerado
- [ ] Secrets configurados no GitHub

**AWS EC2:**
- [ ] Instância criada
- [ ] Security Group configurado
- [ ] Docker instalado
- [ ] Chave .pem baixada

**GitHub:**
- [ ] Todos os secrets configurados
- [ ] Build workflow funcionando
- [ ] Deploy workflow funcionando

**Aplicação:**
- [ ] Frontend acessível
- [ ] Backend acessível  
- [ ] API docs funcionando
- [ ] Banco de dados persistindo

---

🎉 **Deploy automatizado configurado com sucesso!**

Agora cada push para `staging` ou `main` faz deploy automático na AWS EC2!

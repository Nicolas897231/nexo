# Despliegue Produccion LAN NexoVia

## Estado Antes De Publicar

Este repo queda preparado para un MVP productivo en LAN con tres servidores Ubuntu:

- `10.10.10.240`: API FastAPI.
- `10.10.10.241`: PostgreSQL.
- `10.10.10.242`: Web Next.js.

La autenticacion web usa cookies HttpOnly generadas por la API y transportadas por el proxy/rewrite de Next.js. La web no guarda tokens en localStorage.

## Requisitos Previos

En los tres servidores:

```bash
sudo apt update
sudo apt install -y ca-certificates curl git ufw
sudo install -m 0755 -d /etc/apt/keyrings
sudo curl -fsSL https://download.docker.com/linux/ubuntu/gpg -o /etc/apt/keyrings/docker.asc
sudo chmod a+r /etc/apt/keyrings/docker.asc
sudo tee /etc/apt/sources.list.d/docker.sources > /dev/null <<EOF
Types: deb
URIs: https://download.docker.com/linux/ubuntu
Suites: $(. /etc/os-release && echo "${UBUNTU_CODENAME:-$VERSION_CODENAME}")
Components: stable
Architectures: $(dpkg --print-architecture)
Signed-By: /etc/apt/keyrings/docker.asc
EOF
sudo apt update
sudo apt install -y docker-ce docker-ce-cli containerd.io docker-buildx-plugin docker-compose-plugin
sudo systemctl enable --now docker
```

## 1. Servidor BD 10.10.10.241

```bash
sudo mkdir -p /opt/nexovia/infra/production
sudo chown -R $USER:$USER /opt/nexovia
cd /opt/nexovia
git clone TU_REPO .
cd infra/production
cp db.env.example db.env
nano db.env
```

Usa una clave larga en `POSTGRES_PASSWORD`.

Firewall:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow from 10.10.10.240 to any port 5432 proto tcp
sudo ufw enable
```

Levantar:

```bash
docker compose --env-file db.env -f db-compose.yml up -d
docker compose --env-file db.env -f db-compose.yml ps
```

## 2. Servidor API 10.10.10.240

```bash
sudo mkdir -p /opt/nexovia
sudo chown -R $USER:$USER /opt/nexovia
cd /opt/nexovia
git clone TU_REPO .
cd infra/production
cp api.env.example api.env
nano api.env
```

Configura:

- `DATABASE_URL` con password real de PostgreSQL.
- `JWT_SECRET` con un secreto largo. Puedes generarlo con:

```bash
openssl rand -hex 48
```

Firewall:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow from 10.10.10.242 to any port 8000 proto tcp
sudo ufw allow from 10.10.10.0/24 to any port 8000 proto tcp
sudo ufw enable
```

Levantar API y migraciones:

```bash
docker compose -f api-compose.yml up -d --build
docker compose -f api-compose.yml logs -f api
```

Probar:

```bash
curl http://10.10.10.240:8000/health
curl http://10.10.10.240:8000/api/v1/health
```

## 3. Servidor Web 10.10.10.242

```bash
sudo mkdir -p /opt/nexovia
sudo chown -R $USER:$USER /opt/nexovia
cd /opt/nexovia
git clone TU_REPO .
cd infra/production
```

Firewall:

```bash
sudo ufw default deny incoming
sudo ufw default allow outgoing
sudo ufw allow OpenSSH
sudo ufw allow from 10.10.10.0/24 to any port 3000 proto tcp
sudo ufw enable
```

Levantar web:

```bash
docker compose -f web-compose.yml up -d --build
docker compose -f web-compose.yml logs -f web
```

Probar:

```bash
curl http://10.10.10.242:3000/login
curl http://10.10.10.242:3000/api/v1/health
```

Abrir en navegador:

```text
http://10.10.10.242:3000/register
```

## Primer Usuario

1. Entra a `http://10.10.10.242:3000/register`.
2. Crea la cuenta.
3. La web registra el usuario, inicia sesion y redirige al onboarding.
4. Luego entra a dashboard.

## HTTPS

Para uso publico real, coloca dominios internos o publicos y TLS. Cuando uses HTTPS:

- API: `SESSION_COOKIE_SECURE=true`.
- Web: `NEXT_PUBLIC_API_BASE_URL=/api/v1`.
- Mantener proxy `/api/*` desde la web hacia la API.

## Backups

En `10.10.10.241`:

```bash
cd /opt/nexovia/infra/production
docker compose --env-file db.env -f db-compose.yml exec postgres pg_dump -U nexovia_user nexovia > backups/nexovia-$(date +%F).sql
```

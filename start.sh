#!/usr/bin/bash

# Create secrets.toml file
if [ ! -f .secrets.toml ]; then
echo "[development]" > .secrets.toml
echo "dynaconf_merge = true" >> .secrets.toml
echo "" >> .secrets.toml
echo "[development.security]" >> .secrets.toml
echo "# openssl rand -hex 32" >> .secrets.toml
echo "ADMIN_PASS = \"admin\"" >> .secrets.toml
echo "DELIVERY_PASS = \"delivery\"" >> .secrets.toml
echo "SECRET_KEY = \"cc47718e359f700772b80da58e581d4843317ab1ee99bb649c45a64be914a6e2\"" >> .secrets.toml
fi

# Start environment with docker-compose
docker-compose up -d

# wait 5 seconds
sleep 5

# Initial data in database
docker-compose exec api alembic stamp base
docker-compose exec api alembic upgrade head
docker compose exec api dundie initialize
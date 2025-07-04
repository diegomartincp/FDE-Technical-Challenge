#!/bin/bash
set -e

# Paso 1: Copia la configuración HTTP a la carpeta de nginx
echo "Copiando la configuración HTTP a nginx/nginx.conf"
cp nginx/nginx.http.conf nginx/nginx.conf

# Paso 2: Arranca solo nginx en modo HTTP
echo "Arrancando nginx solo en HTTP"
docker-compose up -d nginx

# Paso 3: Ejecuta Certbot para obtener los certificados
echo "Ejecutando Certbot para obtener los certificados"
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
  --email tu-email@dominio.com --agree-tos --no-eff-email \
  -d happyrobot-challenge.duckdns.org -d www.happyrobot-challenge.duckdns.org

if [ $? -ne 0 ]; then
  echo "ERROR: Certbot falló. Saliendo."
  exit 1
fi

# Paso 4: Sustituye la configuración por la de HTTPS
echo "Sustituyendo la configuración por la de HTTPS"
cp nginx/nginx.https.conf nginx/nginx.conf

# Paso 5: Reinicia nginx para activar HTTPS
echo "Reiniciando nginx para activar HTTPS"
docker-compose restart nginx

# Paso 6: Arranca el resto de los servicios
echo "Arrancando el resto de los servicios"
docker-compose up -d app db

#!/bin/bash
set -e

# Step 1: Copy the http configuration to the nginx folder
echo "Copying the http configuration to the nginx folder"
cp nginx.http.conf nginx/nginx.conf

# Step 2: Start nginx only in HTTP
echo "Starting nginx only in HTTP"
docker-compose up -d nginx

# Step 3: Execute Certbot to obtain the certificates
echo "Executing Certbot to obtain the certificates"
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
  --email tu-email@dominio.com --agree-tos --no-eff-email \
  -d happyrobot-challenge.duckdns.org -d www.happyrobot-challenge.duckdns.org

if [ $? -ne 0 ]; then
  echo "ERROR: Certbot failed. Exiting."
  exit 1
fi

# Step 4: Replace the configuration by the https one
echo "Replacing the configuration by the https one, now the server will be available in https"
cp nginx.https.conf nginx/nginx.conf

# Step 5: Restart nginx to activate HTTPS
echo "Restarting nginx to activate HTTPS"
docker-compose restart nginx

# Step 6: Start the rest of the services
echo "Starting the rest of the services"
docker-compose up -d app db

#!/bin/bash
set -e

# Step 1: Copy the HTTP configuration to the nginx folder
echo "Copying the HTTP configuration to nginx/nginx.conf"
cp nginx/nginx.http.conf nginx/nginx.conf

# Step 2: Start nginx only in HTTP mode
echo "Starting nginx only in HTTP mode"
docker-compose up -d nginx

# Step 3: Run Certbot to obtain the certificates
echo "Running Certbot to obtain the certificates"
docker run --rm -it \
  -v "$(pwd)/certbot/www:/var/www/certbot" \
  -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
  certbot/certbot certonly --webroot --webroot-path=/var/www/certbot \
  --email tu-email@dominio.com --agree-tos --no-eff-email \
  -d happyrobot-challenge.duckdns.org -d www.happyrobot-challenge.duckdns.org

if [ $? -ne 0 ]; then
  echo "ERROR: Certbot failed. Exiting."
  exit 1
fi

# Step 4: Replace the configuration with the HTTPS one
echo "Replacing the configuration with the HTTPS one"
cp nginx/nginx.https.conf nginx/nginx.conf

# Step 5: Restart nginx to activate HTTPS
echo "Restarting nginx to activate HTTPS"
docker-compose restart nginx

# Step 6: Start the rest of the services
echo "Starting the rest of the services"
docker-compose up -d app db

#!/bin/bash
set -e

# Create required directories
mkdir -p certbot nginx superset_home

# Step 1: Copy the HTTP configuration to the nginx folder
echo "-- > Copying the HTTP configuration to nginx/nginx.conf"
cp nginx/nginx.http.conf nginx/nginx.conf

# Step 2: Start nginx only in HTTP mode
echo "Starting nginx only in HTTP mode"
docker-compose up -d nginx

# Step 3: Ask if you want to create or renew certificates
read -p "¿Want to create or renew SSL certificates? (s/n): " cert_choice
if [[ "$cert_choice" =~ ^[Ss]$ ]]; then
  echo "-- > Running Certbot to obtain the certificates"
  docker run --rm -it \
    -v "$(pwd)/certbot/www:/var/www/certbot" \
    -v "$(pwd)/certbot/conf:/etc/letsencrypt" \
    certbot/certbot certonly --webroot --webroot-path=/var/www/certbot \
    --email tu-email@dominio.com --agree-tos --no-eff-email \
    -d happyrobot-challenge.duckdns.org -d www.happyrobot-challenge.duckdns.org

  if [ $? -ne 0 ]; then
    echo "-- > ERROR: Certbot failed. Exiting."
    exit 1
  fi
else
  echo "-- > Skiping SSL certificate creation"
fi

# Step 4: Start Superset dashboard and create admin user
echo "-- > Start Superset dashboard and create admin user"
docker-compose up -d superset
docker exec -it superset superset db upgrade
docker exec -it superset superset fab create-admin \
    --username admin --firstname Admin --lastname User --email admin@superset.local --password admin
docker exec -it superset superset init

# Step 5: Replace the configuration with the HTTPS one
echo "-- > Replacing the configuration with the HTTPS one"
cp nginx/nginx.https.conf nginx/nginx.conf

# Step 6: Restart nginx to activate HTTPS
echo "-- > Restarting nginx to activate HTTPS"
docker-compose restart nginx

# Step 7: Start the rest of the services
echo "-- > Starting the rest of the services"
docker-compose up -d app db

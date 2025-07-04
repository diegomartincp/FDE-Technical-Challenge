# 1. install docker engine on server
sudo apt update
sudo apt install -y docker.io
sudo systemctl enable --now docker
sudo usermod -aG docker $USER

-> Then restart the session to make changes take effect.

# 2. Install docker compose
sudo apt update
sudo apt install -y docker-compose

-> Check with docker-compose --version

# 3. Clone the repository
git clone https://github.com/diegomartincp/FDE-Technical-Challenge.git

# 4. Create .env
-> Access the folder and use nano .env to copy the .env file

# 5. Create the folders used in the docker volumes
mkdir -p certbot/www certbot/conf dbdata nginx

# 6. Start nginx
docker-compose up -d nginx

# 7. Generate the SSL certificates and update the nginx configuration
docker-compose run --rm certbot certonly --webroot --webroot-path=/var/www/certbot \
  --email tu-email@dominio.com --agree-tos --no-eff-email \
  -d tudominio.com -d www.tudominio.com
docker-compose restart nginx

# 8. Start the application
docker-compose up -d

# 9. Update the application
git pull
docker-compose up -d --build
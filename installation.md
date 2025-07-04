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
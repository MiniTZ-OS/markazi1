#!/bin/bash
set -e

# Taghdisilabs Deployment Script
# Target: Ubuntu 22.04 VPS
# Domain: taghdisilabs.digital

echo "🚀 Starting deployment to VPS..."

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Configuration
DOMAIN="taghdisilabs.digital"
APP_DIR="/var/www/taghdisilabs"
NODE_USER="appuser"
PM2_APP_NAME="taghdisilabs"

echo -e "${YELLOW}📦 Step 1: Update system packages${NC}"
sudo apt update && sudo apt upgrade -y

echo -e "${YELLOW}🔧 Step 2: Install Node.js 22 LTS${NC}"
curl -fsSL https://deb.nodesource.com/setup_22.x | sudo -E bash -
sudo apt install -y nodejs build-essential

echo -e "${YELLOW}🌐 Step 3: Install Nginx${NC}"
sudo apt install -y nginx

echo -e "${YELLOW}🔒 Step 4: Install SSL (Let's Encrypt)${NC}"
sudo apt install -y certbot python3-certbot-nginx

echo -e "${YELLOW}📁 Step 5: Create application directory${NC}"
sudo mkdir -p $APP_DIR
sudo chown -R $NODE_USER:$NODE_USER $APP_DIR

echo -e "${YELLOW}🔐 Step 6: Create app user${NC}"
if ! id "$NODE_USER" &>/dev/null; then
  sudo useradd -r -s /bin/bash $NODE_USER
  echo "  ✓ User $NODE_USER created"
fi

echo -e "${YELLOW}📥 Step 7: Clone and install repository${NC}"
cd $APP_DIR
sudo -u $NODE_USER git clone https://github.com/MahdiTT96/TaghdisiLabs.git . || sudo -u $NODE_USER git pull
sudo -u $NODE_USER npm ci

echo -e "${YELLOW}🏗️  Step 8: Build Next.js app${NC}"
sudo -u $NODE_USER npm run build

echo -e "${YELLOW}📦 Step 9: Install PM2 globally${NC}"
sudo npm install -g pm2

echo -e "${YELLOW}🚀 Step 10: Start app with PM2${NC}"
sudo -u $NODE_USER pm2 start ecosystem.config.js --env production
sudo pm2 startup systemd -u $NODE_USER --hp /home/$NODE_USER
sudo pm2 save

echo -e "${YELLOW}🌐 Step 11: Configure Nginx${NC}"
sudo tee /etc/nginx/sites-available/$DOMAIN > /dev/null <<EOF
server {
    listen 80;
    listen [::]:80;
    server_name $DOMAIN www.$DOMAIN;

    location / {
        proxy_pass http://localhost:3000;
        proxy_http_version 1.1;
        proxy_set_header Upgrade \$http_upgrade;
        proxy_set_header Connection 'upgrade';
        proxy_set_header Host \$host;
        proxy_cache_bypass \$http_upgrade;
        proxy_set_header X-Real-IP \$remote_addr;
        proxy_set_header X-Forwarded-For \$proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto \$scheme;
    }

    location /_health {
        proxy_pass http://localhost:3000/_health;
        access_log off;
    }

    location /_agent {
        proxy_pass http://localhost:3000/_agent;
        proxy_set_header Host \$host;
    }
}
EOF

echo -e "${YELLOW}🔗 Step 12: Enable Nginx site${NC}"
sudo ln -sf /etc/nginx/sites-available/$DOMAIN /etc/nginx/sites-enabled/$DOMAIN
sudo rm -f /etc/nginx/sites-enabled/default
sudo nginx -t && sudo systemctl restart nginx

echo -e "${YELLOW}🔒 Step 13: Install SSL Certificate${NC}"
sudo certbot --nginx -d $DOMAIN -d www.$DOMAIN --non-interactive --agree-tos -m admin@$DOMAIN

echo -e "${YELLOW}⏰ Step 14: Setup auto-renewal${NC}"
sudo systemctl enable certbot.timer
sudo systemctl start certbot.timer

echo -e "${YELLOW}🧹 Step 15: Cleanup old files${NC}"
sudo find /var/www -maxdepth 1 -type d ! -name taghdisilabs -exec sudo rm -rf {} + 2>/dev/null || true

echo -e "${GREEN}✅ Deployment complete!${NC}"
echo ""
echo -e "${GREEN}🎉 Your site is now live at:${NC}"
echo -e "   https://$DOMAIN"
echo ""
echo -e "${GREEN}📊 Agent Inspector:${NC}"
echo -e "   https://$DOMAIN/_agent"
echo ""
echo -e "${GREEN}❤️  Health Check:${NC}"
echo -e "   https://$DOMAIN/_health"
echo ""
echo -e "${YELLOW}📝 Useful commands:${NC}"
echo "   sudo pm2 logs $PM2_APP_NAME       # View app logs"
echo "   sudo pm2 restart $PM2_APP_NAME    # Restart app"
echo "   sudo systemctl restart nginx      # Restart Nginx"
echo "   sudo certbot renew --dry-run      # Test SSL renewal"
echo ""

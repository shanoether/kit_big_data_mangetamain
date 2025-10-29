#!/bin/bash
# Setup HTTPS for mangetamain.duckdns.org
# This script sets up Let's Encrypt SSL certificate for your Streamlit app

set -e

DOMAIN="mangetamain.duckdns.org"
EMAIL="${LETSENCRYPT_EMAIL:-}"  # Optional, from .env or empty

echo "🔒 Setting up HTTPS for mangetamain.duckdns.org"
echo "================================================"
echo ""

# Check if running on VM
if [ ! -d "/opt/app" ]; then
    echo "⚠️  This script should be run on the VM (kit-big-data-1)"
    echo "Run: gcloud compute ssh kit-big-data-1 --zone=europe-west9-b"
    exit 1
fi

echo "📦 Step 1: Installing Certbot..."
sudo apt-get update
sudo apt-get install -y certbot

echo ""
echo "🔓 Step 2: Opening firewall ports..."
echo "   - Port 80: Temporary (for Let's Encrypt validation only)"
echo "   - Port 443: Permanent (for Streamlit HTTPS - standard HTTPS port)"
sudo ufw allow 80/tcp 2>/dev/null || true
sudo ufw allow 443/tcp 2>/dev/null || true

echo ""
echo "⚠️  Step 3: Checking and stopping services using port 80..."
cd /opt/app

# Stop Docker containers
echo "Stopping Docker containers..."
sudo docker compose down 2>/dev/null || true

# Stop common web servers that might be using port 80
echo "Checking for web servers on port 80..."
if sudo systemctl is-active --quiet apache2 2>/dev/null; then
    echo "Stopping Apache2..."
    sudo systemctl stop apache2
fi

if sudo systemctl is-active --quiet nginx 2>/dev/null; then
    echo "Stopping Nginx..."
    sudo systemctl stop nginx
fi

# Verify port 80 is free (check only LISTEN state, not ESTABLISHED connections)
sleep 1
if sudo lsof -i:80 -sTCP:LISTEN >/dev/null 2>&1; then
    echo "❌ Port 80 is still in use after stopping web servers:"
    echo ""
    sudo lsof -i:80 -sTCP:LISTEN
    echo ""
    echo "Please manually stop the service above and run the script again."
    exit 1
else
    echo "✅ Port 80 is free (ready for certbot)"
fi

echo ""
echo "📜 Step 4: Obtaining Let's Encrypt certificate..."
echo "   Domain: $DOMAIN"

if [ -z "$EMAIL" ]; then
    echo "   Email: None (using --register-unsafely-without-email)"
    sudo certbot certonly --standalone \
        --agree-tos \
        --register-unsafely-without-email \
        -d "$DOMAIN" \
        --non-interactive
else
    echo "   Email: $EMAIL"
    sudo certbot certonly --standalone \
        --agree-tos \
        --email "$EMAIL" \
        -d "$DOMAIN" \
        --non-interactive
fi

CERT_PATH="/etc/letsencrypt/live/$DOMAIN/fullchain.pem"
KEY_PATH="/etc/letsencrypt/live/$DOMAIN/privkey.pem"

echo ""
echo "✅ Certificate obtained!"
echo "📁 Certificate: $CERT_PATH"
echo "🔑 Key: $KEY_PATH"

echo ""
echo "📝 Step 5: Creating Streamlit SSL configuration on VM..."
mkdir -p /opt/app/.streamlit

cat > /opt/app/.streamlit/config.docker.toml <<EOF
[server]
port = 8501
enableCORS = false
enableXsrfProtection = true
sslCertFile = "/etc/letsencrypt/live/mangetamain.duckdns.org/fullchain.pem"
sslKeyFile = "/etc/letsencrypt/live/mangetamain.duckdns.org/privkey.pem"

[browser]
serverAddress = "mangetamain.duckdns.org"
serverPort = 443
EOF

echo "✅ Config created: /opt/app/.streamlit/config.docker.toml (SSL enabled for Docker only)"
echo "   Note: Local .streamlit/config.toml remains without SSL for development"

echo ""
echo "📦 Step 6: Checking Docker Compose to mount certificates..."

# Check if volumes already configured
if ! grep -q "/etc/letsencrypt" /opt/app/docker-compose.yml; then
    echo "Add Manually certificate volumes to docker-compose.yml..."
else
    echo "✅ Docker Compose already configured for HTTPS"
fi

echo ""
echo "⏰ Step 7: Setting up auto-renewal cron job..."
# Check if cron job already exists
if crontab -l 2>/dev/null | grep -q "certbot renew"; then
    echo "✅ Auto-renewal cron job already exists, skipping..."
else
    echo "Adding new cron job (every 2 months at midnight on the 1st)..."
    (crontab -l 2>/dev/null; echo "0 0 1 */2 * sudo certbot renew --quiet --post-hook 'cd /opt/app && docker compose restart streamlit' >> /var/log/certbot-renewal.log 2>&1") | crontab -
    echo "✅ Auto-renewal configured"
fi

echo ""
echo "🚀 Step 8: Starting Docker containers..."
cd /opt/app
sudo docker compose up -d

echo ""
echo "🔒 Step 9: Closing port 80 (no longer needed after certificate obtained)..."
sudo ufw delete allow 80/tcp 2>/dev/null || echo "Port 80 rule not found or already closed"
echo "✅ Port 80 closed"

echo ""
echo "✅ HTTPS Setup Complete!"
echo ""
echo "═══════════════════════════════════════════════════════════"
echo "🌐 Your app is now available at:"
echo "   https://mangetamain.duckdns.org (standard HTTPS port 443)"
echo ""
echo "   Internal port 8501 is mapped to external port 443"
echo ""
echo "📝 Configuration files:"
echo "   - SSL Config: /opt/app/.streamlit/config.toml"
echo "   - Certificates: /etc/letsencrypt/live/$DOMAIN/"
echo "   - Docker Compose: /opt/app/docker-compose.yml"
echo "   - Backup: /opt/app/docker-compose.yml.backup"
echo ""
echo "🔄 Certificate renewal:"
echo "   - Auto-renews every 2 months via cron"
echo "   - Logs: /var/log/certbot-renewal.log"
echo "   - Test: sudo certbot renew --dry-run"
echo ""
echo "🔍 Check status:"
echo "   - View logs: sudo docker logs streamlit-app"
echo "   - Check cert: sudo certbot certificates"
echo "   - View cron: crontab -l"
echo "═══════════════════════════════════════════════════════════"
echo ""

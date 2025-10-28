# Quick HTTPS Setup for mangetamain.duckdns.org

## 📌 Port Requirements Explained

- **Port 80 (HTTP)**: Only needed temporarily during Let's Encrypt certificate setup for domain validation. **Automatically closed after setup**.
- **Port 443 (HTTPS)**: Standard HTTPS port. Docker maps external 443 to internal 8501 where Streamlit runs.
- **Port 8501**: Internal Streamlit port (not exposed externally).

Your final URL: `https://mangetamain.duckdns.org` (no port number needed!)

## 🔄 Automatic Deployment via CI/CD

The HTTPS setup is integrated into the GitHub Actions deployment workflow:
- ✅ Automatically runs on first deployment if certificate doesn't exist
- ✅ Skips setup on subsequent deployments (checks for existing certificate)
- ✅ Cron job for renewal is only added once (prevents duplicates)
- ✅ Port 80 is automatically closed after certificate setup
- ✅ Certificate auto-renews every 2 months

**Manual setup is only needed if CI/CD hasn't run yet.**

## 🚀 Quick Start (3 Steps)

### Step 1: Update GCP Firewall (Run from local machine)

```bash
# Allow HTTP for Let's Encrypt validation (temporary, only during setup)
gcloud compute firewall-rules create allow-http \
    --project=KitBigData-mangetamain \
    --allow tcp:80 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTP for Let's Encrypt validation"

# Allow standard HTTPS port (permanent)
gcloud compute firewall-rules create allow-https \
    --project=KitBigData-mangetamain \
    --allow tcp:443 \
    --source-ranges 0.0.0.0/0 \
    --description "Allow HTTPS on port 443"

# Optional: Close port 80 after setup if you don't need it
# gcloud compute firewall-rules delete allow-http --project=KitBigData-mangetamain
```

### Step 2: Copy Setup Script to VM

```bash
# From your local machine, in the project root
cd /Users/corentinmergny/Documents/code_local/data_ai700_kitbigdata_telecomparis_p1/kit_big_data_mangetamain

# Copy the setup script to VM
gcloud compute scp scripts/setup_https_mangetamain.sh kit-big-data-1:/tmp/ \
    --zone=europe-west9-b
```

### Step 3: Run Setup on VM

```bash
# SSH into your VM
gcloud compute ssh kit-big-data-1 --zone=europe-west9-b

# Run the setup script
chmod +x /tmp/setup_https_mangetamain.sh
sudo /tmp/setup_https_mangetamain.sh

# That's it! The script will:
# - Install Certbot
# - Get Let's Encrypt certificate
# - Configure Streamlit for HTTPS
# - Update Docker Compose
# - Setup auto-renewal
# - Start your app with HTTPS
```

## ✅ After Setup

Your app will be available at: **https://mangetamain.duckdns.org** (standard HTTPS, no port needed!)

The Docker container maps:
- External port 443 (HTTPS) → Internal port 8501 (Streamlit)

## 🔍 Verify Setup

```bash
# Check if certificate was obtained
sudo certbot certificates

# Check if Docker is running
sudo docker ps

# View Streamlit logs
sudo docker logs streamlit-app

# Test HTTPS connection
curl -I https://mangetamain.duckdns.org:8501
```

## 📋 Configuration Files

After setup, these files will exist on your VM:

```
/opt/app/
├── .streamlit/
│   └── config.toml              # Streamlit HTTPS config
├── docker-compose.yml           # Updated with certificate mounts
├── docker-compose.yml.backup    # Original backup
└── data/

/etc/letsencrypt/live/mangetamain.duckdns.org/
├── fullchain.pem               # SSL certificate
└── privkey.pem                 # Private key
```

## 🔄 Certificate Auto-Renewal

- Certificates renew automatically every 2 months
- Cron job: `0 0 1 */2 *` (1st day of every 2nd month at midnight)
- Logs: `/var/log/certbot-renewal.log`

### Manual Renewal

```bash
# Test renewal (dry run)
sudo certbot renew --dry-run

# Force renewal now
sudo certbot renew --force-renewal

# Restart app after manual renewal
cd /opt/app && sudo docker compose restart streamlit
```

## 🐛 Troubleshooting

### Port 80/443 already in use

```bash
# Check what's using the ports
sudo lsof -i :80
sudo lsof -i :443

# Stop Docker if needed
cd /opt/app
sudo docker compose down

# Try setup again
sudo /tmp/setup_https_mangetamain.sh
```

### Certificate not working

```bash
# Check certificate
sudo certbot certificates

# Check Streamlit config
cat /opt/app/.streamlit/config.toml

# Check Docker volumes
sudo docker inspect streamlit-app | grep -A 10 Mounts

# Restart Docker
cd /opt/app
sudo docker compose restart
```

### Browser shows "Not Secure"

1. Make sure you're accessing `https://` not `http://`
2. Check certificate expiry: `sudo certbot certificates`
3. Verify domain points to correct IP: `nslookup mangetamain.duckdns.org`

## 🔧 Manual Rollback (if needed)

If something goes wrong:

```bash
# Restore original docker-compose
cd /opt/app
sudo mv docker-compose.yml.backup docker-compose.yml

# Remove SSL config
sudo rm -rf /opt/app/.streamlit/

# Restart without HTTPS
sudo docker compose down
sudo docker compose up -d
```

## 📞 Support Commands

```bash
# View all logs
sudo docker compose logs -f

# Check cron jobs
crontab -l

# Check firewall
sudo ufw status

# View certificate files
sudo ls -la /etc/letsencrypt/live/mangetamain.duckdns.org/
```

---

## 🎯 Expected Result

After successful setup:

- ✅ App accessible at `https://mangetamain.duckdns.org:8501`
- ✅ Valid SSL certificate (no browser warnings)
- ✅ Auto-renewal configured
- ✅ HTTP traffic works (redirected to HTTPS)
- ✅ Certificates stored at `/etc/letsencrypt/live/mangetamain.duckdns.org/`

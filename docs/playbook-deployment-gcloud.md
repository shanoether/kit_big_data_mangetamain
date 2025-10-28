# Google Cloud Deployment Playbook

This playbook covers Docker containerization, Google Cloud Platform setup, and deployment workflows for the Mangetamain project.

## Table of Contents
- [Docker Setup](#docker-setup)
- [Building Docker Images](#building-docker-images)
- [Google Cloud Platform Setup](#google-cloud-platform-setup)
- [VM Configuration](#vm-configuration)
- [Deployment Workflow](#deployment-workflow)
- [Troubleshooting Deployment](#troubleshooting-deployment)

---

## Docker Setup

### Prerequisites

- Docker Desktop (macOS/Windows) or Colima (macOS)
- Docker Compose
- BuildKit support

### Colima Setup (macOS Recommended)

Colima is a lightweight Docker runtime for macOS that's more efficient than Docker Desktop.

```bash
# Install Colima (if not installed)
brew install colima

# Start Colima with sufficient resources
colima start --memory 8 --cpu 4

# Switch Docker context to Colima
docker context use colima

# Verify Colima is running
docker ps
```

### Docker BuildKit Configuration

BuildKit enables advanced Docker features like multi-platform builds.

```bash
# Create and use a buildx builder (one-time setup)
docker buildx create --name colima-builder \
  --use \
  --driver docker-container

# Initialize the builder
docker buildx inspect --bootstrap

# Verify builder is ready
docker buildx ls
```

---

## Building Docker Images

### Simple Docker Build (Development)

For quick local testing:

```bash
# Build the image
docker build -t mangetamain .

# Run the container
docker run -p 8501:8501 -v ./data:/app/data mangetamain
```

**Access the application**: Open `http://localhost:8501` in your browser.

---

### Production Build with BuildKit

For deployment to Google Cloud or other platforms:

```bash
# Ensure Colima and buildx are configured
colima start
docker context use colima
docker buildx use colima-builder

# Build for linux/amd64 platform (required for GCP)
DOCKER_BUILDKIT=1 docker buildx build \
  --platform linux/amd64 \
  -t mangetamain-processor:latest \
  --load .
```

**Important**: GCP VMs typically run on `linux/amd64` architecture. Always build for this platform when deploying to GCP.

---

### Docker Compose Build

For multi-container applications:

```bash
# Build and start all services
docker compose up --build

# Alternative with BuildKit
DOCKER_BUILDKIT=1 docker-compose up --build
```

**Note**: `docker-compose.yml` should be configured in your project root.

---

### Interactive Docker Testing

Test your container before deployment:

```bash
# Run container with interactive bash shell
docker run --rm -it \
  --entrypoint /bin/bash \
  -v "$(pwd)/data:/app/data" \
  mangetamain-processor:latest

# Inside container, test imports:
python -c "import sys; print(sys.path); import mangetamain; print('OK')"
```

This is useful for debugging import issues, path problems, or missing dependencies.

---

## Google Cloud Platform Setup

### Install Google Cloud CLI

```bash
# Install gcloud CLI (macOS)
brew install --cask gcloud-cli

# Alternative: Download from Google
# https://cloud.google.com/sdk/docs/install
```

### Initial Authentication and Configuration

```bash
# Login to Google Cloud
gcloud auth login

# Set project and zone using environment variables
set -a && source .env && set +a
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${ZONE}

# Verify configuration
gcloud config list
```

### Create `.env` File

Create a `.env` file in your project root:

```bash
# .env
PROJECT_ID=your-gcp-project-id
ZONE=us-central1-a
VM_NAME=mangetamain-vm
VM_EXTERNAL_IP=xx.xx.xx.xx
```

**Note**: Add `.env` to `.gitignore` to keep credentials secure.

---

## VM Configuration

### Create and Access VM

```bash
# Create VM instance (example)
gcloud compute instances create ${VM_NAME} \
  --zone=${ZONE} \
  --machine-type=e2-medium \
  --image-family=debian-11 \
  --image-project=debian-cloud \
  --boot-disk-size=20GB

# SSH into VM
gcloud compute ssh ${VM_NAME}
```

### SSH Key Setup for Non-Interactive Access

Generate dedicated SSH key for deployment:

```bash
# Generate ED25519 SSH key (more secure than RSA)
ssh-keygen -t ed25519 \
  -f ~/.ssh/deploy_key_kitbigdata \
  -C "deploy@kitbigdata" \
  -N ""

# Add public key to GCP VM metadata or authorized_keys

# Connect using the key
ssh -i ~/.ssh/deploy_key_kitbigdata deploy@$VM_EXTERNAL_IP
```

---

### VM Startup Script

Configure your VM to run setup commands on boot.

**Location**: GCP Console → VM Instance → Edit → Automation → Startup script

**Example startup script**:

```bash
#!/bin/bash
# Install Docker if not present
if ! command -v docker &> /dev/null; then
    apt-get update
    apt-get install -y docker.io docker-compose
fi

# Pull latest image
docker pull gcr.io/${PROJECT_ID}/mangetamain:latest

# Run container
docker run -d \
  --name mangetamain \
  --restart unless-stopped \
  -p 8501:8501 \
  -v /data:/app/data \
  gcr.io/${PROJECT_ID}/mangetamain:latest
```

---

## Deployment Workflow

### Complete Deployment Pipeline

#### 1. Prepare the Application

```bash
# Sync dependencies
uv sync

# Run tests
uv run pytest

# Build distribution
uv build
```

#### 2. Build Docker Image for GCP

```bash
# Start Colima
colima start

# Build multi-platform image
DOCKER_BUILDKIT=1 docker buildx build \
  --platform linux/amd64 \
  -t gcr.io/${PROJECT_ID}/mangetamain:latest \
  --load .
```

#### 3. Push to Google Container Registry

```bash
# Configure Docker for GCR authentication
gcloud auth configure-docker

# Tag image for GCR
docker tag mangetamain:latest gcr.io/${PROJECT_ID}/mangetamain:latest

# Push to GCR
docker push gcr.io/${PROJECT_ID}/mangetamain:latest
```

#### 4. Deploy to VM

```bash
# SSH into VM
gcloud compute ssh ${VM_NAME}

# On VM: Pull and run the image
docker pull gcr.io/${PROJECT_ID}/mangetamain:latest

# Stop old container (if running)
docker stop mangetamain || true
docker rm mangetamain || true

# Run new container
docker run -d \
  --name mangetamain \
  --restart unless-stopped \
  -p 8501:8501 \
  -v /home/deploy/data:/app/data \
  gcr.io/${PROJECT_ID}/mangetamain:latest

# Verify it's running
docker ps
docker logs mangetamain
```

#### 5. Configure Firewall

```bash
# Allow incoming traffic on port 8501
gcloud compute firewall-rules create allow-streamlit \
  --allow tcp:8501 \
  --source-ranges 0.0.0.0/0 \
  --description "Allow Streamlit traffic"
```

#### 6. Access the Application

```
http://VM_EXTERNAL_IP:8501
```

---

## Troubleshooting Deployment

### Docker Build Fails on GCP

**Problem**: Image works locally but fails on GCP VM.

**Solution**: Ensure platform compatibility:
```bash
# Build specifically for linux/amd64
docker buildx build --platform linux/amd64 -t image:tag .
```

---

### Cannot SSH into VM

See [Troubleshooting Playbook - Locked Out of VM](playbook-troubleshooting.md#locked-out-of-vm-no-ssh-access).

**Quick fix**: Add startup script to restore SSH access:
```bash
# In GCP Console: VM → Edit → Startup Script
cat >/etc/ssh/sshd_config.d/30-google-ssh.conf <<'EOF'
UsePAM yes
PubkeyAuthentication yes
AuthorizedKeysCommand /usr/bin/google_authorized_keys
AuthorizedKeysCommandUser root
EOF
systemctl restart ssh
```

---

### Container Exits with Code 137

**Problem**: Container is killed due to memory exhaustion.

**Solutions**:

1. **Increase VM memory**:
   ```bash
   # Stop VM
   gcloud compute instances stop ${VM_NAME}

   # Change machine type to one with more RAM
   gcloud compute instances set-machine-type ${VM_NAME} \
     --machine-type=e2-standard-2

   # Start VM
   gcloud compute instances start ${VM_NAME}
   ```

2. **Optimize Docker image**:
   - Use multi-stage builds
   - Remove unnecessary dependencies
   - Clean up build artifacts

3. **Add memory limits**:
   ```bash
   docker run --memory="2g" --memory-swap="2g" your-image
   ```

---

### Port 8501 Not Accessible

**Symptoms**: Cannot access application from browser.

**Solution**:

1. **Check firewall rules**:
   ```bash
   gcloud compute firewall-rules list
   ```

2. **Create firewall rule if missing**:
   ```bash
   gcloud compute firewall-rules create allow-streamlit \
     --allow tcp:8501 \
     --source-ranges 0.0.0.0/0
   ```

3. **Verify container is running**:
   ```bash
   docker ps
   docker logs mangetamain
   ```

4. **Check VM external IP**:
   ```bash
   gcloud compute instances describe ${VM_NAME} \
     --format='get(networkInterfaces[0].accessConfigs[0].natIP)'
   ```

---

### APT Lock Issues During Setup

See [Troubleshooting Playbook - APT Lock Issues](playbook-troubleshooting.md#apt-lock-issues-on-google-cloud-vm).

**Quick fix**:
```bash
# Find and kill stuck processes
sudo lsof /var/lib/dpkg/lock-frontend
sudo kill -9 <PID>

# Force remove stuck package
sudo dpkg --remove --force-remove-reinstreq google-cloud-cli

# Reconfigure
sudo dpkg --configure -a
```

---

## Advanced Deployment

### Automated Deployment with Cloud Build

Create `cloudbuild.yaml`:

```yaml
steps:
  # Build the container image
  - name: 'gcr.io/cloud-builders/docker'
    args: ['build', '-t', 'gcr.io/$PROJECT_ID/mangetamain:$COMMIT_SHA', '.']

  # Push the container image to GCR
  - name: 'gcr.io/cloud-builders/docker'
    args: ['push', 'gcr.io/$PROJECT_ID/mangetamain:$COMMIT_SHA']

  # Deploy to VM
  - name: 'gcr.io/cloud-builders/gcloud'
    args:
      - 'compute'
      - 'ssh'
      - '${_VM_NAME}'
      - '--command=docker pull gcr.io/$PROJECT_ID/mangetamain:$COMMIT_SHA && docker stop mangetamain || true && docker run -d --name mangetamain -p 8501:8501 gcr.io/$PROJECT_ID/mangetamain:$COMMIT_SHA'

images:
  - 'gcr.io/$PROJECT_ID/mangetamain:$COMMIT_SHA'
```

Trigger build:
```bash
gcloud builds submit --config cloudbuild.yaml
```

---

### Using Docker Compose on GCP VM

1. **Create `docker-compose.yml`** on VM:
   ```yaml
   version: '3.8'
   services:
     mangetamain:
       image: gcr.io/${PROJECT_ID}/mangetamain:latest
       ports:
         - "8501:8501"
       volumes:
         - ./data:/app/data
       restart: unless-stopped
   ```

2. **Deploy**:
   ```bash
   # On VM
   docker-compose pull
   docker-compose up -d
   ```

---

### Continuous Deployment with GitHub Actions

Create `.github/workflows/deploy.yml`:

```yaml
name: Deploy to GCP

on:
  push:
    branches: [main]

jobs:
  deploy:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3

      - name: Setup Cloud SDK
        uses: google-github-actions/setup-gcloud@v1
        with:
          service_account_key: ${{ secrets.GCP_SA_KEY }}
          project_id: ${{ secrets.GCP_PROJECT_ID }}

      - name: Build and Push
        run: |
          gcloud auth configure-docker
          docker build -t gcr.io/${{ secrets.GCP_PROJECT_ID }}/mangetamain:latest .
          docker push gcr.io/${{ secrets.GCP_PROJECT_ID }}/mangetamain:latest

      - name: Deploy to VM
        run: |
          gcloud compute ssh ${{ secrets.VM_NAME }} --command="
            docker pull gcr.io/${{ secrets.GCP_PROJECT_ID }}/mangetamain:latest &&
            docker stop mangetamain || true &&
            docker run -d --name mangetamain -p 8501:8501 gcr.io/${{ secrets.GCP_PROJECT_ID }}/mangetamain:latest
          "
```

---

## Best Practices

1. **Always build for `linux/amd64`** when deploying to GCP
2. **Use Container Registry** (GCR) or Artifact Registry for image storage
3. **Tag images** with version numbers or commit SHAs
4. **Set resource limits** in docker run commands
5. **Use startup scripts** for VM initialization
6. **Monitor logs**: `docker logs -f mangetamain`
7. **Enable automatic restarts**: `--restart unless-stopped`
8. **Back up data volumes** regularly
9. **Use `.dockerignore`** to reduce image size
10. **Test locally** with same platform: `--platform linux/amd64`

---

## Security Considerations

1. **Don't commit secrets** to Git (use `.env` and `.gitignore`)
2. **Use IAM roles** for service account permissions
3. **Restrict firewall rules** to specific IP ranges when possible
4. **Rotate SSH keys** regularly
5. **Keep Docker images updated** with security patches
6. **Use Google Secret Manager** for sensitive configuration
7. **Enable VPC firewall logging** for audit trails
8. **Use private IPs** for internal communication

---

## Monitoring and Maintenance

### Check Application Health

```bash
# View container logs
docker logs -f mangetamain

# Check resource usage
docker stats mangetamain

# Check container health
docker inspect mangetamain
```

### Update Deployed Application

```bash
# Pull latest image
docker pull gcr.io/${PROJECT_ID}/mangetamain:latest

# Recreate container with new image
docker stop mangetamain
docker rm mangetamain
docker run -d --name mangetamain -p 8501:8501 gcr.io/${PROJECT_ID}/mangetamain:latest
```

### Backup Data

```bash
# Create backup of data volume
docker run --rm \
  -v mangetamain_data:/data \
  -v $(pwd)/backup:/backup \
  ubuntu tar czf /backup/data-$(date +%Y%m%d).tar.gz /data
```

# Troubleshooting Playbook

This playbook contains tips, tricks, and solutions for common issues encountered in the Mangetamain project.

## Table of Contents
- [Python Environment Issues](#python-environment-issues)
- [Docker Issues](#docker-issues)
- [Google Cloud Platform Issues](#google-cloud-platform-issues)
- [Testing Issues](#testing-issues)
- [Dependency Issues](#dependency-issues)
- [SSH and Access Issues](#ssh-and-access-issues)

---

## Python Environment Issues

### PyArrow Installation Failures

**Symptoms**:
- Build errors when installing PyArrow
- "Failed building wheel for pyarrow"
- Version conflicts with other packages

**Solution**:

1. **Configure Python version** in `pyproject.toml`:
   ```toml
   [tool.uv]
   python = "3.12.*"
   ```

2. **Force binary-only installation** to avoid compilation:
   ```bash
   export UV_PIP_ONLY_BINARY=":all:"
   # Alternative environment variable:
   export PIP_ONLY_BINARY=":all:"
   ```

3. **Install compatible PyArrow version**:
   ```bash
   # Recreate virtual environment
   uv venv --recreate

   # Install PyArrow with version constraints
   uv add "pyarrow>=16,<18" --no-sync

   # Sync all dependencies
   uv sync
   ```

**Why it works**: Using pre-built binary wheels avoids compilation issues, and the version constraint ensures compatibility with other packages.

---

### Virtual Environment Not Activating

**Symptoms**:
- Commands not found after installation
- Wrong Python version being used

**Solution**:
```bash
# Verify virtual environment exists
ls -la .venv

# Manually activate (if needed)
source .venv/bin/activate

# Verify activation
which python
python --version
```

---

### Jupyter Kernel Not Appearing in VS Code

**Symptoms**:
- Kernel not listed in VS Code notebook interface
- "No kernel found" error

**Solution**:
```bash
# List existing kernels
uv run jupyter kernelspec list

# Remove old kernel if it exists
uv run jupyter kernelspec uninstall venv-3.12-mangetamain

# Reinstall kernel
uv run ipython kernel install --user \
  --name=venv-3.12-mangetamain \
  --display-name "Python 3.12 (mangetamain)"

# Restart VS Code completely
```

---

## Docker Issues

### Docker Exit Code 137 (Out of Memory)

**Symptoms**:
- Container exits with code 137
- "Killed" message in logs
- Docker stops unexpectedly during build or runtime

**Problem**: Container is using too much memory and is killed by the system.

**Solutions**:

1. **Increase Docker memory limit**:
   ```bash
   # For Docker Desktop (macOS)
   # Go to Docker Desktop → Settings → Resources → Memory
   # Increase to at least 4GB (8GB recommended)

   # For Colima
   colima stop
   colima start --memory 8
   ```

2. **Optimize Dockerfile**:
   - Use multi-stage builds
   - Clean up unnecessary files
   - Reduce layer size
   - Use `.dockerignore`

3. **Monitor memory usage**:
   ```bash
   # Check container memory usage
   docker stats

   # Run container with memory limit
   docker run --memory="2g" --memory-swap="2g" your-image
   ```

---

### Colima Docker Context Issues

**Symptoms**:
- "Cannot connect to Docker daemon"
- Docker commands fail

**Solution**:
```bash
# Start Colima
colima start

# Switch to Colima context
docker context use colima

# Verify context
docker context ls
docker ps
```

---

### Docker BuildKit Issues

**Symptoms**:
- Build failures with multi-platform images
- "builder not found" error

**Solution**:
```bash
# Ensure Colima is running
colima start

# Create buildx builder (one-time setup)
docker buildx create --name colima-builder \
  --use \
  --driver docker-container \
  --use

# Initialize builder
docker buildx inspect --bootstrap

# Verify builder
docker buildx ls

# Build with BuildKit
DOCKER_BUILDKIT=1 docker buildx build \
  --platform linux/amd64 \
  -t mangetamain-processor:latest \
  --load .
```

---

## Google Cloud Platform Issues

### Locked Out of VM (No SSH Access)

**Symptoms**:
- Cannot SSH into VM
- Google Cloud Console SSH not working
- "Permission denied" errors

**Solution**: Add startup script to restore SSH access

1. **Go to Google Cloud Console**:
   - Navigate to Compute Engine → VM Instances
   - Select your VM → Edit

2. **Add this startup script**:
   ```bash
   # Restore settings that GCE Web SSH relies on (metadata-injected SSH keys)
   cat >/etc/ssh/sshd_config.d/30-google-ssh.conf <<'EOF'
   # Allow Google to inject temporary SSH keys
   UsePAM yes
   PubkeyAuthentication yes
   PasswordAuthentication no
   ChallengeResponseAuthentication no
   AuthorizedKeysCommand /usr/bin/google_authorized_keys
   AuthorizedKeysCommandUser root
   PermitRootLogin prohibit-password
   EOF

   # Remove hard "AllowUsers" restrictions
   sed -i '/^AllowUsers/d' /etc/ssh/sshd_config || true

   # Restart services
   systemctl restart google-guest-agent || true
   systemctl restart ssh || systemctl restart sshd || true

   echo "Startup script finished"
   ```

3. **Save and restart the VM**

**Why it works**: This restores the default Google Cloud SSH configuration that allows authentication via metadata-injected keys.

---

### APT Lock Issues on Google Cloud VM

**Symptoms**:
- `dpkg` or `apt` commands hang
- "Unable to acquire dpkg frontend lock"
- Package installation fails

**Solution**:

1. **Check for stuck processes**:
   ```bash
   # List processes holding the lock
   sudo lsof /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock 2>/dev/null
   ```

2. **Identify and kill stuck process**:
   ```bash
   # Example: Check specific PID
   ps -p 283985 -o pid,ppid,stat,etime,cmd

   # Kill stuck processes (use actual PIDs from lsof)
   sudo kill -9 283985 283984
   ```

3. **Force remove problematic package**:
   ```bash
   # If google-cloud-cli is stuck
   sudo dpkg --remove --force-remove-reinstreq google-cloud-cli
   ```

4. **Clean up and retry**:
   ```bash
   # Remove lock files (if processes are truly dead)
   sudo rm /var/lib/dpkg/lock-frontend
   sudo rm /var/lib/dpkg/lock
   sudo rm /var/cache/apt/archives/lock

   # Reconfigure packages
   sudo dpkg --configure -a

   # Update package lists
   sudo apt update
   ```

---

### Google Cloud Authentication Issues

**Symptoms**:
- `gcloud` commands fail with authentication errors
- Cannot access GCP resources

**Solution**:
```bash
# Login to Google Cloud
gcloud auth login

# Login for application default credentials
gcloud auth application-default login

# Set project
gcloud config set project YOUR_PROJECT_ID

# Verify configuration
gcloud config list
```

---

## Testing Issues

### Tests Fail After Passing Previously

**Symptoms**:
- Tests pass individually but fail together
- Inconsistent test results

**Solution**:
```bash
# Clear pytest cache
rm -rf .pytest_cache
rm -rf tests/**/__pycache__

# Specific directory cleanup
rm -rf tests/unit/mangetamain/backend/__pycache__

# Run tests again
uv run pytest -v
```

---

### Mock Objects Not Working Correctly

**Symptoms**:
- `AttributeError` in mocked objects
- Tests fail with "MagicMock has no attribute X"

**Solution**:
```python
# Use proper mock configuration
from unittest.mock import MagicMock, patch

# Configure mock return values
mock_obj = MagicMock()
mock_obj.method.return_value = expected_value

# Configure mock attributes
mock_obj.attribute = expected_value

# Use spec to match real object
mock_obj = MagicMock(spec=RealClass)
```

---

### Coverage Report Doesn't Match Expected

**Symptoms**:
- Coverage shows lines as uncovered that should be covered
- Coverage percentage is lower than expected

**Solution**:
```bash
# Clean previous coverage data
rm -rf .coverage
rm -rf htmlcov/

# Run coverage with verbose output
uv run coverage run -m pytest -v
uv run coverage report -m

# Generate HTML report for detailed view
uv run coverage html
# Open htmlcov/index.html in browser
```

---

## Dependency Issues

### Conflicting Package Versions

**Symptoms**:
- `pip` or `uv` reports version conflicts
- Import errors after installation

**Solution**:
```bash
# Check dependency tree
uv pip tree

# Force reinstall with fresh lockfile
rm uv.lock
uv sync

# Use specific version constraints in pyproject.toml
# Example:
# dependencies = [
#     "package>=1.0,<2.0",
# ]
```

---

### Import Errors After Installing Package

**Symptoms**:
- `ModuleNotFoundError` despite package being installed
- Package shows in `uv pip list` but can't be imported

**Solution**:
```bash
# Verify you're using the right Python environment
uv run python -c "import sys; print(sys.executable)"

# Check if package is in site-packages
uv run python -c "import sys; print(sys.path)"

# Reinstall package
uv remove package-name
uv add package-name
uv sync
```

---

## SSH and Access Issues

### SSH Key Authentication Fails

**Symptoms**:
- "Permission denied (publickey)"
- SSH asks for password when it shouldn't

**Solution**:
```bash
# Generate new SSH key
ssh-keygen -t ed25519 -f ~/.ssh/deploy_key_kitbigdata \
  -C "deploy@kitbigdata" -N ""

# Check key permissions (must be 600)
chmod 600 ~/.ssh/deploy_key_kitbigdata
chmod 644 ~/.ssh/deploy_key_kitbigdata.pub

# Add key to SSH agent
eval "$(ssh-agent -s)"
ssh-add ~/.ssh/deploy_key_kitbigdata

# Test connection with verbose output
ssh -v -i ~/.ssh/deploy_key_kitbigdata user@host
```

---

## General Tips

### Enable Verbose Logging

For debugging any command:
```bash
# Python
python -v script.py

# SSH
ssh -v user@host

# Docker
docker build --progress=plain .

# gcloud
gcloud compute ssh VM_NAME --verbosity=debug
```

### Check System Resources

```bash
# Disk space
df -h

# Memory usage
free -h

# Running processes
top
htop  # if installed

# Docker resources
docker system df
docker system prune  # Clean up unused resources
```

### Environment Variable Debugging

```bash
# Print all environment variables
env

# Print specific variable
echo $VARIABLE_NAME

# Check if variable is set
[[ -z "$VARIABLE_NAME" ]] && echo "Not set" || echo "Set: $VARIABLE_NAME"
```

---

## Getting Help

When reporting issues, include:

1. **Error message** (full output)
2. **Command executed** (exact command)
3. **Environment info**:
   ```bash
   python --version
   uv --version
   docker --version
   uname -a
   ```
4. **Steps to reproduce** the issue
5. **What you've already tried**

**Useful diagnostic commands**:
```bash
# Check Python environment
uv run python -c "import sys; print(sys.version); print(sys.executable); print(sys.path)"

# Check installed packages
uv pip list

# Check Docker setup
docker info
docker context ls

# Check gcloud configuration
gcloud config list
gcloud auth list
```

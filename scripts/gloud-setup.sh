brew install --cask gcloud-cli
gcloud auth login

set -a && source .env && set +a
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${ZONE}
gcloud compute ssh ${VM_NAME}

ssh-keygen -t ed25519 -f ~/.ssh/deploy_key_kitbigdata -C "deploy@kitbigdata" -N ""
ssh -i ~/.ssh/deploy_key_kitbigdata deploy@$VM_EXTERNAL_IP


####### Troubleshooting #####

# Locked out of VM
# If stuck without google ssh access to vm
# add the following script in start-up script in vm>edit

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

# If you previously restricted users, remove hard "AllowUsers" lines so Google users can log in
sed -i '/^AllowUsers/d' /etc/ssh/sshd_config || true

# Restart services
systemctl restart google-guest-agent || true
systemctl restart ssh || systemctl restart sshd || true

echo "Startup script finished"


# locked for apt install
sudo dpkg --remove --force-remove-reinstreq google-cloud-cli
ps -p 283985 -o pid,ppid,stat,etime,cmd
sudo lsof /var/lib/dpkg/lock-frontend /var/lib/dpkg/lock 2>/dev/null
sudo kill -9 283985 283984
sudo dpkg --remove --force-remove-reinstreq google-cloud-cli


# Docker exit with error 137: killed because too much memory
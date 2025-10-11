brew install --cask gcloud-cli
gcloud auth login

set -a && source .env && set +a
gcloud config set project ${PROJECT_ID}
gcloud config set compute/zone ${ZONE}
gcloud compute ssh ${VM_NAME}

ssh-keygen -t ed25519 -f ~/.ssh/deploy_key_kitbigdata -C "deploy@kitbigdata" -N ""
ssh -i ~/.ssh/deploy_key_kitbigdata deploy@$VM_EXTERNAL_IP
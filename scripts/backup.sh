#!/bin/sh
set -eu
cd "$(dirname "$0")/.."
mkdir -p backups
stamp=$(date +%Y%m%d-%H%M%S)
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
docker compose exec -T db pg_dump -U lingyao -Fc lingyao > "backups/lingyao-$stamp.dump"
docker run --rm -v referenced-chatgpt-conversation-this-is-an_resume_files:/source:ro -v "$PWD/backups":/backup public.ecr.aws/docker/library/alpine:3.22 sh -c "tar czf /backup/attachments-$stamp.tar.gz -C /source ."
echo "Backup created: backups/lingyao-$stamp.dump and attachments-$stamp.tar.gz"

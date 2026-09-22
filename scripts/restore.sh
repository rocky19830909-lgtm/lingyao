#!/bin/sh
set -eu
if [ "$#" -ne 2 ]; then
  echo "Usage: scripts/restore.sh backups/lingyao-TIME.dump backups/attachments-TIME.tar.gz"
  exit 1
fi
cd "$(dirname "$0")/.."
db_file=$1
files_archive=$2
export PATH="/Applications/Docker.app/Contents/Resources/bin:$PATH"
test -f "$db_file" && test -f "$files_archive"
docker compose exec -T db dropdb -U lingyao --if-exists lingyao
docker compose exec -T db createdb -U lingyao lingyao
docker compose exec -T db pg_restore -U lingyao -d lingyao --clean --if-exists < "$db_file"
docker run --rm -v referenced-chatgpt-conversation-this-is-an_resume_files:/target -v "$PWD":/work public.ecr.aws/docker/library/alpine:3.22 sh -c "rm -rf /target/* && tar xzf /work/$files_archive -C /target"
docker compose restart api
echo "Restore complete."

# Backend Deployment Guide (Google Cloud)

This checklist helps you move the API, agent, and trainer services from local `docker compose` to Google Cloud. Adjust naming to match your project.

## 1. Prerequisites
- gcloud CLI authenticated (`gcloud auth login`) and project set via `gcloud config set project <PROJECT_ID>`.
- Artifact Registry repository created for container images, e.g. `us-docker.pkg.dev/<PROJECT_ID>/voice-agent`.
- Service account with permissions: Cloud Run Admin, Cloud SQL Admin, Secret Manager Admin, Artifact Registry Writer.

## 2. Build & Push Containers
Each backend service already has a Dockerfile under `services/<name>/Dockerfile`.

```bash
# From repo root
gcloud builds submit --tag "us-docker.pkg.dev/$PROJECT_ID/voice-agent/api:latest" --config cloudbuild.yaml --timeout=15m services/api
gcloud builds submit --tag "us-docker.pkg.dev/$PROJECT_ID/voice-agent/agent:latest" services/agent
gcloud builds submit --tag "us-docker.pkg.dev/$PROJECT_ID/voice-agent/trainer:latest" services/trainer
```

> `cloudbuild.yaml` is optional; if omitted, Cloud Build uses the Dockerfile. Supply `--region` if your Artifact Registry is regional.

## 3. Create Managed Postgres (Cloud SQL)
```bash
INSTANCE=voice-agent-db
REGION=us-central1

gcloud sql instances create $INSTANCE \
  --database-version=POSTGRES_16 --tier=db-custom-2-7680 \
  --region=$REGION --storage-auto-increase

gcloud sql databases create voice --instance=$INSTANCE
gcloud sql users create voiceuser --instance=$INSTANCE --password="<GENERATE_STRONG_PASSWORD>"
```

Record the instance connection name (`<PROJECT>:<REGION>:<INSTANCE>`). Update `.env` locally and Cloud Run envs with `DB_URL=postgresql+psycopg2://voiceuser:<PASSWORD>@127.0.0.1/voice` using the Cloud SQL proxy socket.

## 4. Manage Secrets
Push your production credentials into Secret Manager:

```bash
for key in LIVEKIT_URL LIVEKIT_API_KEY LIVEKIT_API_SECRET OPENAI_API_KEY \
           DEEPGRAM_API_KEY ELEVENLABS_API_KEY;
do
  printf "%s" "${!key}" | gcloud secrets create $key --data-file=- --replication-policy=automatic
done
```

If a secret already exists, use `gcloud secrets versions add $key --data-file=-`. Grant the runtime service account `roles/secretmanager.secretAccessor`.

## 5. Persistent Asset Storage
The trainer writes files under `data/voice_samples/` and `data/persona/` (`services/trainer/api.py:25`, `services/trainer/api.py:45`). Cloud Run containers are ephemeral, so store these in Cloud Storage:

1. Create a bucket: `gsutil mb -l $REGION gs://$PROJECT_ID-voice-assets`.
2. Mount via Cloud Run volume (`gcloud run services replace ... --add-volume name=assets,type=cloud-storage,bucket=$BUCKET`).
3. Set env like `TRAINER_ASSET_ROOT=/mnt/assets` and update the trainer code to respect it (or sync manually before deploy).

## 6. Deploy Cloud Run Services
Use one Cloud Run service per container. Examples (adjust region & service account):

```bash
SA=voice-agent-runtime@$PROJECT_ID.iam.gserviceaccount.com
SQL_CONN="${PROJECT_ID}:${REGION}:${INSTANCE}"

# API Service (exposes /token etc.)
gcloud run deploy voice-api \
  --image=us-docker.pkg.dev/$PROJECT_ID/voice-agent/api:latest \
  --region=$REGION --platform=managed --allow-unauthenticated \
  --service-account=$SA \
  --add-cloudsql-instances=$SQL_CONN \
  --set-env-vars=DB_URL="postgresql+psycopg2://voiceuser:<PASSWORD>@/voice?host=/cloudsql/$SQL_CONN" \
  --set-secrets="LIVEKIT_URL=LIVEKIT_URL:latest,LIVEKIT_API_KEY=LIVEKIT_API_KEY:latest,LIVEKIT_API_SECRET=LIVEKIT_API_SECRET:latest"

# Agent Worker (no public endpoint)
gcloud run deploy voice-agent \
  --image=us-docker.pkg.dev/$PROJECT_ID/voice-agent/agent:latest \
  --region=$REGION --platform=managed --no-allow-unauthenticated \
  --service-account=$SA \
  --add-cloudsql-instances=$SQL_CONN \
  --set-env-vars=DB_URL="postgresql+psycopg2://voiceuser:<PASSWORD>@/voice?host=/cloudsql/$SQL_CONN" \
  --set-secrets="OPENAI_API_KEY=OPENAI_API_KEY:latest,DEEPGRAM_API_KEY=DEEPGRAM_API_KEY:latest,ELEVENLABS_API_KEY=ELEVENLABS_API_KEY:latest"

# Trainer API (protected behind IAM or VPC)
gcloud run deploy voice-trainer \
  --image=us-docker.pkg.dev/$PROJECT_ID/voice-agent/trainer:latest \
  --region=$REGION --platform=managed --no-allow-unauthenticated \
  --service-account=$SA \
  --add-cloudsql-instances=$SQL_CONN \
  --set-env-vars=DB_URL="postgresql+psycopg2://voiceuser:<PASSWORD>@/voice?host=/cloudsql/$SQL_CONN" \
  --set-secrets="ELEVENLABS_API_KEY=ELEVENLABS_API_KEY:latest" \
  --set-env-vars=MAX_DOC_MB=50,TRAINER_ASSET_ROOT=/mnt/assets \
  --add-volume=name=assets,type=cloud-storage,bucket=$PROJECT_ID-voice-assets \
  --add-volume-mount=volume=assets,mount-path=/mnt/assets
```

Secure the trainer and agent services by leaving them unauthenticated and calling them via authorized service accounts or VPC access. Update API base URL in the frontend (`frontend/.env.local`) to point to the public Cloud Run domain or a custom domain.

## 7. Database Migration & Seed
- Run `python3 scripts/setup_voice.py ...` and `python3 scripts/setup_persona.py ...` against the new endpoints (set `TRAINER_API_URL` to Cloud Run URL) to rebuild indexes in the shared storage.
- If migrating existing data, dump from local Postgres and restore into Cloud SQL (`pg_dump` / `psql`).

## 8. Monitoring & Logging
- Enable Cloud Run > Logs Router to BigQuery or Cloud Logging sink for long-term storage.
- Create uptime checks for the API and trainer endpoints.
- Optionally add Error Reporting by configuring structured logs (`severity`, `message`).

## 9. Before Production Traffic
- Verify CORS settings (`services/api/main.py`) include your custom domain.
- Confirm minimum concurrency, CPU allocation, and autoscaling limits (`--concurrency`, `--min-instances`) for cold-start sensitive services.
- Test end-to-end by running `python3 scripts/test_api.py --trainer-url https://voice-trainer-<hash>-uc.a.run.app` from a workstation.

Once all checks pass, connect your Google-managed domain to the Cloud Run services or load balancer, and issue SSL via Google-managed certificates.


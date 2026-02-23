# Crypto Verification

Crypto verification service with 33 Voices / Mirror Protocol integration.

## Setup

```bash
# Install dependencies
cd ~/crypto-verification
python3 -m venv venv
source venv/bin/activate
pip install flask requests numpy

# Optional: Node for 33 Voices
npm install
```

## Run locally

```bash
source venv/bin/activate
python backend/app.py
```

Server runs at http://localhost:5001 (5000 often used by AirPlay on macOS)

## Deploy to Vercel

```bash
vercel --prod
```

**Note:** For Vercel, Python serverless functions live in `api/`. The Flask backend (`backend/app.py`) is for local development. For production on Vercel, use the `api/` handlers or wrap Flask with `serverless-http`.

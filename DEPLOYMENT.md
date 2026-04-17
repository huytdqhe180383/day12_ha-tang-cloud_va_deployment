
# Deployment Information

## Public URL

https://day12-lab-huy-production.up.railway.app

## Platform

Railway

## Project Source

- App folder: [06-lab-complete](06-lab-complete)
- Main app: [06-lab-complete/app/main.py](06-lab-complete/app/main.py)
- Environment template: [06-lab-complete/.env.example](06-lab-complete/.env.example)

## Environment Variables Set

- `PORT`
- `REDIS_URL`
- `AGENT_API_KEY`
- `JWT_SECRET`
- `OPENAI_API_KEY` if you use a real model
- `ENVIRONMENT`
- `RATE_LIMIT_PER_MINUTE`
- `DAILY_BUDGET_USD`

## Test Commands

### Health Check

```bash
curl https://day12-lab-huy-production.up.railway.app/health
```

Expected response:

```json
{"status":"ok"}
```

### Ready Check

```bash
curl https://day12-lab-huy-production.up.railway.app/ready
```

### Ask Endpoint with Authentication

```bash
curl -X POST https://day12-lab-huy-production.up.railway.app/ask \
  -H "X-API-Key: YOUR_KEY" \
  -H "Content-Type: application/json" \
   -d '{"question":"Hello"}'
```

### Rate Limit Test

```bash
for i in {1..15}; do
  curl -s -o /dev/null -w "%{http_code}\n" \
      -X POST https://day12-lab-huy-production.up.railway.app/ask \
    -H "X-API-Key: YOUR_KEY" \
    -H "Content-Type: application/json" \
      -d '{"question":"test"}'
done
```

Expected: eventually returns `429`.

## Screenshots

- [Screenshot 2026-04-17 163118.png](screenshots/Screenshot%202026-04-17%20163118.png)
- [Screenshot 2026-04-17 162944.png](screenshots/Screenshot%202026-04-17%20162944.png)
- [Screenshot 2026-04-17 162642.png](screenshots/Screenshot%202026-04-17%20162642.png)
- [Screenshot 2026-04-17 163705.png](screenshots/Screenshot%202026-04-17%20163705.png)

## Railway Deployment Steps

1. Open a terminal in [day12_ha-tang-cloud_va_deployment](.).
2. Go into the final project folder:

   ```bash
   cd 06-lab-complete
   ```

3. Make sure your `.env` or Railway variables include at least `AGENT_API_KEY`, `REDIS_URL`, and `PORT`.
4. Install Railway CLI:

   ```bash
   npm i -g @railway/cli
   ```

5. Log in:

   ```bash
   railway login
   ```

6. Initialize the project:

   ```bash
   railway init
   ```

7. Set environment variables:

   ```bash
   railway variables set AGENT_API_KEY=your-secret-key
   railway variables set REDIS_URL=redis://your-redis-url
   railway variables set ENVIRONMENT=production
   railway variables set RATE_LIMIT_PER_MINUTE=20
   railway variables set DAILY_BUDGET_USD=5.0
   ```

8. Deploy:

   ```bash
   railway up
   ```

9. Get the public URL:

   ```bash
   railway domain
   ```

10. Test the URL using the commands in the Test Commands section.

## Render Deployment Steps

1. Push the repository to GitHub.
2. Open Render and create a new Blueprint.
3. Connect the GitHub repository.
4. Render will read `render.yaml` from [03-cloud-deployment/render](03-cloud-deployment/render).
5. Set the secret variables in the Render dashboard.
6. Deploy the service.
7. Copy the generated public URL into this file.

## What Must Be Verified Before Submission

- Public URL works.
- `/health` returns 200.
- `/ready` returns 200.
- `/ask` returns 401 without `X-API-Key`.
- `/ask` returns 200 with a valid key.
- Rate limiting returns 429 after the limit is exceeded.
- Screenshots are included in the `screenshots/` folder.

## Current Verification Status

- Deployed successfully on Railway.
- `GET /health`: verified `200`.
- `GET /ready`: verified `200`.
- `POST /ask` without API key: verified `401`.
- `POST /ask` with API key: verified `200` and returns answer payload.
- Rate limiting: verified `429` appears under burst traffic.

## Troubleshooting

- If `/ready` returns `not found` or `404`, the app code is usually not the problem. The endpoint is defined in [06-lab-complete/app/main.py](06-lab-complete/app/main.py).
- Check that you are calling the real deployed URL from Railway/Render, not the placeholder `https://your-agent.railway.app` used in this template.
- If you recently changed env vars or the start command, redeploy the service so the new version is actually running.
- For local testing, use `http://localhost:8000/ready` only when the app is running locally with Docker or Uvicorn.

## Notes

- Do not commit `.env` or real secrets.
- If you use Redis in production, confirm the `REDIS_URL` matches the deployed service.
- If you use a real LLM, set `OPENAI_API_KEY`; otherwise the mock LLM is enough for the lab.
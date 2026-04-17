# Day 12 Lab - Answer Sheet

## Part 1: Localhost vs Production

### Exercise 1.1: Anti-patterns found in `01-localhost-vs-production/develop/app.py`

1. Secret hardcoded in code (`OPENAI_API_KEY`, `DATABASE_URL`) so it can be leaked if pushed to GitHub.
2. `DEBUG = True` and `reload=True`, which are fine for local dev but unsafe for production.
3. Host is fixed to `localhost`, so the app cannot receive traffic from outside the container.
4. Port is hardcoded to `8000` instead of reading `PORT` from the environment.
5. No health check endpoint (`/health`) and no readiness endpoint (`/ready`).
6. Uses `print()` for logging and even logs the secret key, which is a security issue.
7. No graceful shutdown handling, so in-flight requests may be interrupted.

### Exercise 1.2: Run basic version

The basic version does run and can answer requests through `/ask`, but it is not production-ready. It has hardcoded secrets, no environment-based configuration, weak logging, no health/readiness checks, and no graceful shutdown behavior.

### Exercise 1.3: Compare basic vs advanced version

| Feature | Basic | Advanced | Why it matters |
|---|---|---|---|
| Config | Hardcoded values | Environment variables | Prevents leaking secrets and makes deployment portable. |
| Health check | None | `/health` endpoint | Lets the platform detect if the app is alive and restart it if needed. |
| Logging | `print()` | Structured JSON logging | Easier to search, parse, and monitor in cloud logs. |
| Shutdown | Immediate / abrupt | Graceful via lifespan / signal handling | Lets current requests finish before the container stops. |
| Host / port | `localhost:8000` | `0.0.0.0` and `PORT` env var | Required for Docker and cloud platforms like Railway/Render. |

---

## Part 2: Docker Containerization

### Exercise 2.1: Basic Dockerfile questions

1. Base image: `python:3.11`.
2. Working directory: `/app`.
3. `COPY requirements.txt` comes first so Docker can reuse the dependency layer cache when application code changes.
4. `CMD` provides the default command for the container; `ENTRYPOINT` defines the executable that always runs. `CMD` is easier to override, so it is usually better for simple app startup commands.

### Exercise 2.2: Build and run

The develop image is large because it uses the full `python:3.11` base image and installs everything in one stage. On a typical machine this is around 1 GB or more before optimization. The key takeaway is that the image is much heavier than the multi-stage production build.

### Exercise 2.3: Multi-stage build

- Stage 1 (`builder`): installs build dependencies such as `gcc` and `libpq-dev`, then installs Python packages.
- Stage 2 (`runtime`): copies only the built packages and runtime source code, runs as a non-root user, and starts the app with `uvicorn`.
- The image is smaller because build tools, caches, and temporary files never make it into the runtime stage, and the final image uses `python:3.11-slim`.

### Exercise 2.4: Docker Compose stack

The compose stack in `02-docker/production/docker-compose.yml` starts these services: `agent`, `redis`, `qdrant`, and `nginx`.

- `agent` runs the FastAPI app.
- `redis` stores session and cache data.
- `qdrant` is the vector database for RAG-style retrieval.
- `nginx` acts as reverse proxy and load balancer.

They communicate over the internal Docker bridge network. Nginx routes incoming requests to the `agent` service, while the agent talks to Redis and Qdrant by service name.

---

## Part 3: Cloud Deployment

### Exercise 3.1: Deploy Railway

The Railway flow is:

1. Set the project up with `railway init`.
2. Set environment variables such as `PORT` and `AGENT_API_KEY`.
3. Deploy with `railway up`.
4. Get the public URL with `railway domain`.
5. Test `/health` and `/ask` using `curl`.

I do not have a live Railway URL inside this workspace, so that field must be filled after deployment.

### Exercise 3.2: Compare `render.yaml` and `railway.toml`

- `render.yaml` is a full infrastructure blueprint: it declares the web service, Redis service, build/start commands, health check path, and environment variables.
- `railway.toml` is lighter and mostly defines build/start behavior plus health check and restart policy.
- Render keeps more of the infrastructure in the blueprint file, while Railway relies more on dashboard variables plus the config file.

### Exercise 3.3: Cloud Run config

- `cloudbuild.yaml` defines the CI/CD build-and-deploy pipeline.
- `service.yaml` defines the runtime service settings for Cloud Run, including container image, service config, and environment variables.

---

## Part 4: API Security

### Exercise 4.1: API key authentication

The API key check happens in the auth dependency: the server reads the `X-API-Key` header and compares it with the configured secret (`AGENT_API_KEY`). If the key is missing, the request returns `401 Unauthorized`; if the key is wrong, it also fails.

Key rotation is done by changing the environment variable and redeploying. That way the secret is not hardcoded in source code.

### Exercise 4.2: JWT authentication

JWT flow in `04-api-gateway/production/auth.py`:

1. User logs in with username and password.
2. The server creates a signed token with `JWT_SECRET`.
3. The client sends the token as `Authorization: Bearer <token>`.
4. The server verifies the signature and expiry on every request.

JWT is stateless, so the server does not need to look up session data in a database for each call.

### Exercise 4.3: Rate limiting

The rate limiter uses a **sliding window counter** based on timestamps stored in a deque.

- Default user limit: `10 requests / minute`.
- Admin limit: `100 requests / minute`.
- To bypass the normal limit for admin, use a token/role path that routes the request to the admin limiter.

### Exercise 4.4: Cost guard

The cost guard logic should:

- Track spending per user per month.
- Use Redis keys like `budget:{user_id}:{YYYY-MM}`.
- Allow requests while `current_spending + estimated_cost <= 10`.
- Reset automatically at the start of a new month.

Example implementation:

```python
from datetime import datetime

def check_budget(user_id: str, estimated_cost: float) -> bool:
    month_key = datetime.now().strftime("%Y-%m")
    key = f"budget:{user_id}:{month_key}"

    current = float(r.get(key) or 0)
    if current + estimated_cost > 10:
        return False

    r.incrbyfloat(key, estimated_cost)
    r.expire(key, 32 * 24 * 3600)
    return True
```

---

## Part 5: Scaling & Reliability

### Exercise 5.1: Health checks

`/health` is the liveness probe: it should return `200` when the process is alive.

`/ready` is the readiness probe: it should return `200` only when the app is ready to receive traffic, and `503` if dependencies such as Redis or the database are not available.

### Exercise 5.2: Graceful shutdown

On `SIGTERM`, the server should:

1. Stop accepting new requests.
2. Finish in-flight requests.
3. Close open connections.
4. Exit cleanly.

This is handled through lifespan shutdown and signal handling in the advanced examples.

### Exercise 5.3: Stateless design

State should not live in Python memory. Conversation history and session data should be stored in Redis so that any instance can serve the next request.

That is why `05-scaling-reliability/production/app.py` stores chat history in Redis and can be scaled horizontally without losing context.

### Exercise 5.4: Load balancing

The Nginx config uses an upstream pool that points to the `agent` service. With `docker compose up --scale agent=3`, requests are distributed across instances, and the `X-Served-By` header makes the routing visible.

### Exercise 5.5: Test stateless

The stateless test should show that:

- A session created on one instance can be read on another instance.
- Killing one instance does not break the conversation.
- The conversation survives because the session state is in Redis, not in process memory.

---

## Part 6: Final Project Summary

The combined solution in `06-lab-complete` already brings together the major production requirements:

- Environment-based config
- Structured JSON logging
- API key authentication
- Rate limiting
- Cost guard
- Health and readiness endpoints
- Graceful shutdown
- Docker and deployment config for Railway/Render

If this file is used for submission, the only missing part is the real deployment data such as the public URL and screenshots, which must be filled after a real deploy.
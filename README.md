# cdisc-workflows

Mediforce workflow definitions and container code for CDISC automation pipelines.

## Repository layout

```
<workflow-name>/
  Dockerfile                  # built with context = this directory
  .dockerignore
  container/                  # scripts copied into the image
  src/<workflow-name>.wd.json # workflow definition (registered via CLI)
  plugins/                    # agent skills (claude-code-agent steps)
  test/                       # stage scripts run inside the container
```

---

## Registering a workflow

### Prerequisites

1. **Mediforce CLI** — available inside the `mediforce` repo via `pnpm exec mediforce`.
2. **API key** — set `MEDIFORCE_API_KEY` (or source `.env.local`):
   ```bash
   set -a && source ../mediforce/packages/platform-ui/.env.local && set +a
   ```
3. **Namespace** — the namespace must already exist on the target instance.

### Local (http://localhost:9003)

```bash
# Start the dev server first (from the mediforce repo)
pnpm dev

# Sync the model registry (first time, or after new models are added)
pnpm exec mediforce model sync --base-url=http://localhost:9003

# Register
pnpm exec mediforce workflow register \
  --file=protocol-to-synthetic-sdtm/src/protocol-to-synthetic-sdtm.wd.json \
  --namespace=<your-namespace> \
  --base-url=http://localhost:9003
```

### Staging (https://staging.mediforce.ai)

```bash
MEDIFORCE_API_KEY=<key> pnpm exec mediforce workflow register \
  --file=protocol-to-synthetic-sdtm/src/protocol-to-synthetic-sdtm.wd.json \
  --namespace=<your-namespace> \
  --base-url=https://staging.mediforce.ai
```

### Dry-run (validate without hitting the API)

```bash
pnpm exec mediforce workflow register \
  --file=protocol-to-synthetic-sdtm/src/protocol-to-synthetic-sdtm.wd.json \
  --namespace=<your-namespace> \
  --dry-run
```

---

## Setting secrets

Workflows reference secrets by name (e.g. `{{GITHUB_TOKEN}}`). Set them per-namespace before starting a run:

```bash
pnpm exec mediforce secret set \
  --key=GITHUB_TOKEN \
  --value="<value>" \
  --namespace=<your-namespace> \
  --base-url=<url>

pnpm exec mediforce secret set --key=OPENROUTER_API_KEY --value="<value>" ...
pnpm exec mediforce secret set --key=CDISC_API_KEY      --value="<value>" ...
```

Secrets are workspace-level (shared across all workflows in the namespace) unless `--workflow` is specified.

---

## Starting a run

```bash
pnpm exec mediforce run start \
  --workflow=protocol-to-synthetic-sdtm \
  --namespace=<your-namespace> \
  --base-url=<url> \
  --json
```

Human steps (e.g. `provide-inputs`) are completed via the UI or `mediforce task complete`.

---

## Updating a workflow after code changes

1. Commit and push to `main`.
2. Copy the new commit SHA (`git rev-parse HEAD`).
3. Update every `"commit"` field in the `.wd.json` to the new SHA.
4. Re-register — the platform assigns the next version number automatically.

```bash
NEW_SHA=$(git rev-parse HEAD)
# edit the .wd.json commit fields, then:
pnpm exec mediforce workflow register --file=... --namespace=... --base-url=...
```

---

## Notes

- **Build context** — Docker images are built with the Dockerfile's own directory as context, not the repo root. `COPY` paths are relative to `<workflow-name>/`.
- **workspace.remoteAuth** — must be set to a secret name containing a GitHub token so the platform clones the repo over HTTPS instead of SSH (SSH is not available on all deployments).
- **`python3`** — use `python3` explicitly in `command` fields; `python` may not be symlinked on older golden image builds.

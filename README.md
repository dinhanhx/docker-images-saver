# docker-images-saver

CLI that reads a `docker-compose.yml`, then `docker save`s every referenced image into a directory as `.tar` files.

## Requirements

- Python >= 3.10
- Docker CLI available on `PATH`

## Install

For local development (run from within the project directory):

```bash
uv sync
```

To use the `docker-images-saver` command from any directory, install it as a uv tool:

```bash
uv tool install /path/to/docker-images-saver
```

After code changes, reinstall to pick them up:

```bash
uv tool install --force /path/to/docker-images-saver
```

Alternatively, run it without installing via `uvx`:

```bash
uvx --from /path/to/docker-images-saver docker-images-saver <compose_file> <out_dir>
```

## Usage

```bash
docker-images-saver <compose_file> <out_dir>
# or, from within the project directory during development:
uv run docker-images-saver <compose_file> <out_dir>
```

Options:

- `-f`, `--force` — re-save images even if a matching `.tar` already exists in `out_dir`
- `--dry-run` — print the `docker save` commands without executing them

### Example

```bash
uv run docker-images-saver docker-compose.yml ./saved-images/
```

Each image is saved as `<out_dir>/<sanitized-image-name>.tar` (e.g. `nginx:latest` -> `nginx_latest.tar`). Duplicate images across services are only saved once. Services without an `image:` key (e.g. `build`-only services) are skipped with a warning.

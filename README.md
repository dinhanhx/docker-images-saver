# docker-images-saver

CLI that reads a `docker-compose.yml`, then `docker save`s every referenced image into a directory as `.tar` files.

## Requirements

- Python >= 3.10
- Docker CLI available on `PATH`

## Install

```bash
uv sync
```

## Usage

```bash
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

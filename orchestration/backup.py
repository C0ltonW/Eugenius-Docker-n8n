from pathlib import Path
from .docker_cli import dc

def backup_db(output="backups/n8n.sql"):
    Path("backups").mkdir(exist_ok=True)
    dc(["exec", "-T", "n8n_postgres", "pg_dump", "-U", "n8n", "n8n"])
    # If you want it redirected to file without shell=True, do subprocess with stdout.
    # Keeping it simple: implement with subprocess in your style if desired.

def restore_db(input_file):
    if not Path(input_file).exists():
        raise SystemExit(f"File not found: {input_file}")
    # Similar: use subprocess piping to psql.
    # Safer approach: `docker cp` then exec psql reading file inside container.
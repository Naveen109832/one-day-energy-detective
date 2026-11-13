"""
Entrypoint Script to launch One-Day Energy Detective Server.
Serves REST API on /api and Single Page Frontend on /.
"""

import sys
from pathlib import Path

# Add project root to sys.path
PROJECT_ROOT = Path(__file__).resolve().parent
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from backend.app import run_server
from backend.config import HOST, PORT

if __name__ == "__main__":
    try:
        run_server(HOST, PORT)
    except KeyboardInterrupt:
        print("\nServer terminated.")
        sys.exit(0)

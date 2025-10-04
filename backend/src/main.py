"""Main FastAPI application entry point."""

import sys
import logging
from pathlib import Path
import uvicorn
from infrastructure.app_factory import create_app
from infrastructure.config import config

src_path = Path(__file__).parent
sys.path.insert(0, str(src_path))

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.StreamHandler(sys.stdout)
    ],
    force=True  # Force reconfiguration even if logging was already configured
)

# Set log level for our application modules
logging.getLogger('application').setLevel(logging.INFO)
logging.getLogger('domain').setLevel(logging.INFO)
logging.getLogger('adapters').setLevel(logging.INFO)

logger = logging.getLogger(__name__)

app = create_app()


if __name__ == "__main__":
    logger.info(f"Starting uvicorn server on {config.HOST}:{config.PORT}")
    uvicorn.run(
        "main:app",
        host=config.HOST,
        port=config.PORT,
        reload=True
    )


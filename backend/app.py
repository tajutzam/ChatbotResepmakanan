import os
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

if __package__ in {None, ""}:
    sys.path.insert(0, str(Path(__file__).resolve().parent.parent))

BACKEND_DIRECTORY = Path(__file__).resolve().parent
load_dotenv(BACKEND_DIRECTORY / ".env")


def create_app() -> Flask:
    from backend.routes.chatbot import chatbot_blueprint

    app = Flask(__name__)
    app.config["EMBEDDING_ADMIN_TOKEN"] = os.getenv("EMBEDDING_ADMIN_TOKEN", "").strip()
    app.register_blueprint(chatbot_blueprint, url_prefix="/api")

    return app


app = create_app()


if __name__ == "__main__":
    app.run(
        host=os.getenv("FLASK_HOST", "127.0.0.1"),
        port=int(os.getenv("FLASK_PORT", "5001")),
        debug=False,
    )

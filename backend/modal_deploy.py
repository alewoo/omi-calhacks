"""
Modal deployment configuration for FoodVoice API

To deploy:
1. Install Modal: pip install modal
2. Set up Modal account: modal setup
3. Deploy: modal deploy modal_deploy.py
"""
import modal

# Create Modal app
app = modal.App("foodvoice-omi")

# Define container image with all dependencies
image = (
    modal.Image.debian_slim(python_version="3.11")
    .pip_install(
        "fastapi==0.109.0",
        "uvicorn[standard]==0.27.0",
        "pydantic==2.5.3",
        "pydantic-settings==2.1.0",
        "anthropic==0.18.1",
        "redis==5.0.1",
        "httpx==0.26.0",
        "python-dotenv==1.0.0",
    )
)

# Define secrets (set these in Modal dashboard)
secrets = [
    modal.Secret.from_name("foodvoice-secrets"),  # Create this in Modal dashboard with your env vars
]


@app.function(
    image=image,
    secrets=secrets,
    min_containers=1,  # Keep 1 instance warm for fast responses
    timeout=300,  # 5 minute timeout
)
@modal.asgi_app()
def fastapi_app():
    """Mount FastAPI app to Modal"""
    # Import all modules directly
    import os
    import sys

    # Add current directory to path
    sys.path.insert(0, "/root")

    # Import the FastAPI app
    from main import app as fastapi_app
    return fastapi_app


@app.local_entrypoint()
def main():
    """Local entry point for testing"""
    print("🚀 FoodVoice API deployed to Modal!")
    print("📖 Check Modal dashboard for webhook URL")

"""Docker image management utilities."""

import subprocess
from pathlib import Path

try:
    from setup.environment import get_project_root
except ImportError:
    from pathlib import Path

    def get_project_root() -> Path:
        """Get the project root directory."""
        return Path(__file__).parent.parent.parent


def get_required_images() -> list[str]:
    """
    Get list of required Docker images for MCP development.

    Returns:
        List of required Docker image names
    """
    return [
        "postgres:14-alpine",
        "python:3.11-slim",
    ]


def check_required_images() -> dict[str, bool]:
    """
    Check if required Docker images are available locally.

    Returns:
        Dictionary mapping image names to availability status
    """
    required_images = get_required_images()
    image_status = {}

    try:
        # List all images
        result = subprocess.run(
            ["docker", "images", "--format", "{{.Repository}}:{{.Tag}}"],
            capture_output=True,
            text=True,
            check=True,
        )

        available_images = result.stdout.splitlines()

        # Check each required image
        for image in required_images:
            image_status[image] = image in available_images

    except Exception:
        # If we can't check, assume images are not available
        for image in required_images:
            image_status[image] = False

    return image_status


def pull_required_images() -> tuple[bool, list[str]]:
    """
    Pull required Docker images.

    Returns:
        Tuple of (success, error_messages)
    """
    required_images = get_required_images()
    errors = []

    for image in required_images:
        try:
            print(f"Pulling {image}...")
            result = subprocess.run(
                ["docker", "pull", image],
                capture_output=True,
                text=True,
                check=True,
            )
            print(f"✓ Successfully pulled {image}")
        except Exception as e:
            error_msg = f"✗ Failed to pull {image}: {str(e)}"
            print(error_msg)
            errors.append(error_msg)

    return len(errors) == 0, errors


def build_development_image(tag: str = "mcp-dev:latest") -> tuple[bool, str | None]:
    """
    Build the development Docker image.

    Args:
        tag: Tag for the built image

    Returns:
        Tuple of (success, error_message)
    """
    project_root = get_project_root()
    dockerfile_path = (
        project_root / "setup" / "docker" / "dockerfiles" / "Dockerfile.dev"
    )

    if not dockerfile_path.exists():
        # Circular import resolved by importing here
        from setup.docker.container_config import create_development_dockerfile

        dockerfile_path = create_development_dockerfile()

    try:
        print(f"Building development image {tag}...")
        result = subprocess.run(
            [
                "docker",
                "build",
                "-t",
                tag,
                "-f",
                str(dockerfile_path),
                str(project_root),
            ],
            capture_output=True,
            text=True,
            check=True,
        )
        print(f"✓ Successfully built {tag}")
        return True, None
    except Exception as e:
        error_msg = f"✗ Failed to build {tag}: {str(e)}"
        print(error_msg)
        return False, error_msg


def cleanup_unused_images() -> bool:
    """
    Clean up unused Docker images to free disk space.

    Returns:
        True if cleanup was successful, False otherwise
    """
    try:
        print("Cleaning up unused Docker images...")
        result = subprocess.run(
            ["docker", "image", "prune", "-f"],
            capture_output=True,
            text=True,
            check=True,
        )
        print("✓ Successfully cleaned up unused images")
        return True
    except Exception as e:
        print(f"✗ Failed to clean up unused images: {str(e)}")
        return False

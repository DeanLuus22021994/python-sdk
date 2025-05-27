import os
import shutil

BASE_DIR = os.path.abspath(os.path.dirname(__file__))
ROOT_DIR = os.path.abspath(os.path.join(BASE_DIR, ".."))


def move_file(src_rel, dest_rel):
    src_path = os.path.join(ROOT_DIR, src_rel)
    dest_path = os.path.join(ROOT_DIR, dest_rel)
    dest_dir = os.path.dirname(dest_path)

    os.makedirs(dest_dir, exist_ok=True)

    if os.path.exists(src_path):
        shutil.move(src_path, dest_path)
        print(f"MOVED: {src_rel} → {dest_rel}")
    else:
        print(f"WARNING: Source file not found → {src_rel}")


def run_batch(description, moves):
    print(f"\n{description}")
    for src, dest in moves:
        move_file(src, dest)
    input("\nPress Enter to continue...")


if __name__ == "__main__":
    print("=== STARTING ZATRUST BIO-MCP RESTRUCTURE ===")

    # Batch 1: Environment to config
    run_batch(
        "Moving environment files to setup/config/",
        [
            ("environment/constants.py", "setup/config/constants.py"),
            ("environment/manager.py", "setup/config/manager.py"),
            ("environment/utils.py", "setup/config/utils.py"),
        ],
    )

    # Batch 2: Docker to infra/docker
    run_batch(
        "Moving docker files to setup/infra/docker/",
        [
            ("docker/config.py", "setup/infra/docker/config.py"),
            ("docker/images.py", "setup/infra/docker/images.py"),
            ("docker/volume_config.py", "setup/infra/docker/volume_config.py"),
            ("docker/volumes.py", "setup/infra/docker/volumes.py"),
            (
                "docker/dockerfiles/Dockerfile.dev",
                "setup/infra/docker/dockerfiles/Dockerfile.dev",
            ),
        ],
    )

    # Batch 3: Host to infra/host
    run_batch(
        "Moving host files to setup/infra/host/",
        [
            ("host/package_manager.py", "setup/infra/host/package_manager.py"),
        ],
    )

    # Batch 4: Removing orphan environment.py if present
    env_py = os.path.join(ROOT_DIR, "environment.py")
    if os.path.exists(env_py):
        os.remove(env_py)
        print("REMOVED: environment.py (root-level, eliminated for clarity)")
    else:
        print("NOTE: No root-level environment.py found — skipping removal")

    print("\n=== RESTRUCTURE COMPLETED ===")
    print("Next steps:")
    print("✔ Update imports to match new paths")
    print("✔ Add __main__.py entry point in setup/")
    print("✔ Confirm CLI integration via setup.py")
    print("✔ Run static typing checks (pyright)")
    print("✔ Validate orchestration logic with test runs")

import os
import re

PYPROJECT_PATH = "./launkey/pyproject.toml"

def update_version(new_version):
    with open(PYPROJECT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    content_new = re.sub(
        r"(version\s*=\s*\")[^\"]+(\")",
        rf"\1{new_version}\2",
        content
    )

    with open(PYPROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(content_new)

if __name__ == "__main__":
    new_version = os.environ.get("NEW_VERSION")
    if not new_version:
        print("NEW_VERSION environment variable not set.")
        exit(1)
    update_version(new_version)
    print(f"Version updated to {new_version} in {PYPROJECT_PATH}")
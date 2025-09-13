import sys
import re

PYPROJECT_PATH = "./launkey/pyproject.toml"

def update_version(new_version):
    with open(PYPROJECT_PATH, "r", encoding="utf-8") as f:
        content = f.read()

    def replace_version(match):
        section = match.group(1)
        version_line = match.group(2)
        # Only replace version in [tool.briefcase] section
        version_line_new = re.sub(
            r'(version\s*=\s*")[^"]+(")',
            lambda m: f'{m.group(1)}{new_version}{m.group(2)}',
            version_line
        )
        return f"{section}{version_line_new}"

    # Replace only in [tool.briefcase] section
    content_new = re.sub(
        r'(\[tool\.briefcase\][^\[]*?)(version\s*=\s*"[^"]+")',
        replace_version,
        content,
        flags=re.DOTALL
    )

    with open(PYPROJECT_PATH, "w", encoding="utf-8") as f:
        f.write(content_new)

if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("Usage: python updateversion.py <new_version>")
        sys.exit()
    new_version = sys.argv[1]
    update_version(new_version)
    print(f"Version updated to {new_version} in {PYPROJECT_PATH}")
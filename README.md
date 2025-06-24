# Launkey

# How to test

## Linux
You need to run the project with root privileges to be able to access the input devices.
```bash
sudo su
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cd launkey
briefcase dev
```
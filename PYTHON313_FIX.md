# Python 3.13 Compatibility

Python 3.13 has limited package support. The recommended versions for this demo are **Python 3.11 or 3.12**.

---

## Check Your Python Version

```bash
python3 --version
```

---

## Option 1 — Use Minimal Requirements (Recommended for 3.13)

```bash
rm -rf venv
python3 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements-minimal.txt
```

---

## Option 2 — Install Python 3.11 via Homebrew (Mac)

```bash
brew install python@3.11
python3.11 -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt
```

---

## Option 3 — Manual Package Install

If requirements files fail, install packages individually:

```bash
pip install python-dotenv pyyaml elasticsearch faker rich click requests
```

---

## Verify Installation

```bash
source venv/bin/activate
python -c "import elasticsearch; print(elasticsearch.__version__)"
python scripts/utilities/test_connectivity.py
```

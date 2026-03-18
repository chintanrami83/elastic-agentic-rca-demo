# Quick Fix for Python 3.13 Installation Issues

## The Problem

Python 3.13 is very new (released in 2024) and many packages don't support it yet. 

The errors you're seeing:
- ❌ `httpx-mock==0.11.0` - doesn't exist for Python 3.13
- ❌ `ModuleNotFoundError: No module named 'elasticsearch'` - failed to install

## Quick Fix (Option 1 - Recommended)

Use the minimal requirements file I just created:

```bash
cd /path/to/elastic-agentic-rca-demo

# Download the new files:
# - requirements-minimal.txt
# - test_setup_fixed.sh

# Make script executable
chmod +x test_setup_fixed.sh

# Remove old venv
rm -rf venv

# Run new setup
./test_setup_fixed.sh
```

## Manual Fix (Option 2)

If the script still fails, install packages manually:

```bash
cd /path/to/elastic-agentic-rca-demo

# Remove old venv
rm -rf venv

# Create new venv
python3 -m venv venv

# Activate it
source venv/bin/activate

# Upgrade pip
pip install --upgrade pip

# Install packages one by one
pip install python-dotenv
pip install pyyaml
pip install elasticsearch
pip install faker
pip install rich
pip install click
pip install requests

# Test connection
python scripts/utilities/test_connectivity.py
```

## Verify Installation

After running either fix:

```bash
source venv/bin/activate
python -c "import elasticsearch; print(elasticsearch.__version__)"
# Should print: 8.x.x

python scripts/utilities/test_connectivity.py
# Should connect to Elasticsearch
```

## What Changed

**Old requirements.txt:**
- Had specific version pins (==)
- Included packages not compatible with Python 3.13
- Had testing packages we don't need yet

**New requirements-minimal.txt:**
- Uses flexible versions (>=)
- Only essential packages
- All Python 3.13 compatible
- Removed httpx-mock and other testing packages

## Next Steps

Once `test_connectivity.py` works:

```bash
source venv/bin/activate
python scripts/utilities/setup_elasticsearch.py
```

This will create all 10 Elasticsearch indices.

## Alternative: Use Python 3.11

If you want maximum compatibility, you could also:

```bash
# Install Python 3.11 using Homebrew
brew install python@3.11

# Create venv with Python 3.11
python3.11 -m venv venv

# Then continue with original requirements.txt
source venv/bin/activate
pip install -r requirements.txt
```

But the minimal requirements should work fine with Python 3.13!

## Files You Need

Download these NEW files:
1. **requirements-minimal.txt** - Python 3.13 compatible
2. **test_setup_fixed.sh** - Updated setup script

Replace your current:
- requirements.txt → requirements-minimal.txt
- test_setup.sh → test_setup_fixed.sh

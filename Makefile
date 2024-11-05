.PHONY: setup clean run tilemap-helper

# Default Python version
PYTHON=python3
VENV=stellar_haven_env
MAIN_SCRIPT=src/main.py
TILEMAP_HELPER=src/tools/launch_tilemap_helper.py

setup:
	# Create virtual environment if it doesn't exist
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	# Activate venv and install requirements
	. $(VENV)/bin/activate && \
	pip install --upgrade pip && \
	pip install -r requirements.txt

run:
	# Activate venv and run the main script
	. $(VENV)/bin/activate && \
	$(PYTHON) $(MAIN_SCRIPT)

tilemap-helper:
	# Activate venv and run the tilemap helper
	. $(VENV)/bin/activate && \
	$(PYTHON) $(TILEMAP_HELPER)

clean:
	# Remove virtual environment and cache files
	rm -rf $(VENV)
	find . -type d -name "__pycache__" -exec rm -rf {} +
	find . -type f -name "*.pyc" -delete
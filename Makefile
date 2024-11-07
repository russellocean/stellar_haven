.PHONY: setup clean run tilemap-helper

# Default Python version
PYTHON=python3
VENV=stellar_haven_env
MAIN_SCRIPT=src/main.py
TILEMAP_HELPER=src/tools/launch_tilemap_helper.py

ifeq ($(OS),Windows_NT)
    # Windows commands
    VENV_BIN=$(VENV)/Scripts
    RM_CMD=rd /s /q
    RM_CACHE=for /r %%x in (__pycache__) do if exist "%%x" rd /s /q "%%x"
    ACTIVATE=call $(VENV_BIN)/activate.bat &&
else
    # Unix commands
    VENV_BIN=$(VENV)/bin
    RM_CMD=rm -rf
    RM_CACHE=find . -type d -name "__pycache__" -exec rm -rf {} +
    ACTIVATE=. $(VENV_BIN)/activate &&
endif

setup:
	test -d $(VENV) || $(PYTHON) -m venv $(VENV)
	$(ACTIVATE) \
	$(PYTHON) -m pip install --upgrade pip && \
	$(PYTHON) -m pip install -r requirements.txt

run:
	$(ACTIVATE) \
	$(PYTHON) $(MAIN_SCRIPT)

tilemap-helper:
	$(ACTIVATE) \
	$(PYTHON) $(TILEMAP_HELPER)

clean:
	$(RM_CMD) $(VENV)
	$(RM_CACHE)
	find . -type f -name "*.pyc" -delete
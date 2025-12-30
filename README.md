# Captain - Dependency Management System

Captain is a minimalist system for converting dependency configuration files between different formats. It enables transformation of a `build.yaml` file into `requirements.txt` or `pyproject.toml`.

## Architecture

### Main Components

- **Core** (`core.py`) - application core with CLI and event-bus system
- **Parser Requirements** (`parser_requirements.py`) - module for generating `requirements.txt`
- **Parser PyProject** (`parser_pyproject.py`) - module for generating `pyproject.toml`
- **Validate Build** (`validator_build.py`) - module for checking `build.yaml` validity

### Module System

Captain uses a publish-subscribe architecture:
- Modules register for specific commands
- Core publishes events for commands from the configuration file
- Modules respond to their corresponding events

## Installing Dependencies

### Option 1: Via requirements.txt

```bash
pip install -r requirements.txt
```

### Option 2: Via pyproject.toml

```bash
# Install in editable mode (code changes work immediately)
pip install -e .

# OR standard installation
pip install .
```

### Option 3: Manual Installation

```bash
pip install typer pyyaml tomli-w
```

### Virtual Environment (optional)

```bash
# Create venv
python -m venv venv

# Activate
# Windows:
venv\Scripts\activate
# Linux/Mac:
source venv/bin/activate

# Then install dependencies using chosen method
```

### Dependency List

Captain requires the following packages:
- **typer** - CLI framework
- **pyyaml** - YAML file parser
- **tomli-w** - TOML file writer (for `pyproject.toml`)

### Requirements

```bash
Python 3.8+ and required libraries
```

### Project Structure

```
Captain/
├── .gitignore
├── captain/
│   ├── modules/
│   │   ├── __init__.py
│   │   ├── parser_pyproject.py
│   │   ├── parser_requirements.py
│   │   └── validator_build.py
│   ├── Output/                      # Output directory (generated)
│   │   ├── requirements.txt         # Generated from build.yaml
│   │   └── pyproject.toml          # Generated from build.yaml
│   ├── __init__.py
│   ├── build.yaml
│   ├── config.yaml
│   └── core.py
├── pyproject.toml                  
├── requirements.txt                 
└── README.md
```

## Configuration

### build.yaml

Source file with project and dependency definitions:

```yaml
myproject: "Captain"

dependencies:
  - typer
  - pyyaml
  - tomli-w
```

**Fields:**
- `myproject` (string) - project name
- `dependencies` (list) - list of packages with optional version constraints

### config.yaml

Configuration file specifying available modules and commands:

```yaml
version: "1.0-Beta"

modules:
  - core
  - parser_requirements  
  - parser_pyproject

commands:
  - req # convert -> requirements.txt
  - pyproject # convert -> pyproject.toml
  - validator build    # check source file validity
```

**Fields:**
- `version` - configuration version
- `modules` - list of modules to load
- `commands` - list of available commands (execution order preserved)

## Usage

### Basic Commands

```bash
# Run all commands from config.yaml
python core.py -c config.yaml

# Run specific command
python core.py -c config.yaml -r req

# Short syntax
python core.py -c config.yaml -r pyproject
```

### Usage Examples

1. **Generating requirements.txt:**
    
    ```bash
    python core.py -c config.yaml -r "req"
    ```
    
    Creates a `requirements.txt` file with content:
    
    ```text
    typer
    pyyaml
    tomli-w
    ```

2. **Generating pyproject.toml:**
    
    ```bash
    python core.py -c config.yaml -r "pyproject"
    ```
    
    Creates a `pyproject.toml` file:
    
    ```toml
    [project]
    name = "Captain"
    version = "0.1.0"
    dependencies = [
      "typer",
      "pyyaml",
      "tomli-w",
    ]

    [build-system]
    requires = ["setuptools", "wheel"]
    build-backend = "setuptools.build_meta"
    ```

## Module API

### Creating a New Module

Each module must implement a `register(core)` function:

```python
def register(core) -> None:
    """Register commands in the core system."""
    core.subscribe("command:command_name", handler_function)

def handler_function(topic: str, payload: Any) -> None:
    """Handle command."""
    # Module logic
    pass
```

### Core API

**Communication:**
- `core.subscribe(topic, callback)` - event subscription
- `core.publish(topic, payload)` - event publishing

**Context:**
- `core.ctx` - shared dictionary for modules
- `core.version` - application version

## Error Handling

- Errors in modules don't stop core execution
- Missing files trigger warning display
- Invalid YAML structure returns error code 2

### Common Messages

- `[OK] requirements.txt` - successful file generation
- `[WARN] missing module: modules.xyz` - module not found
- `[ERR] Cannot read build.yaml: ...` - file reading error
- `Error: 'commands' must be a list` - invalid config.yaml structure

## Extending the System

### Adding New Formats

1. Create a new module in `modules/parser_format.py`
2. Implement the `register(core)` function
3. Add command to `config.yaml`
4. Add module to the `modules` list in configuration

Example module:

```python
def register(core) -> None:
    core.subscribe("command:convert to format", convert_handler)

def convert_handler(topic: str, payload: Any) -> None:
    # Load build.yaml
    # Transform data
    # Save in new format
    print("[OK] output.format")
```

## Limitations

- Only YAML files as configuration source
- No dependency syntax validation
- Module names cannot contain dots (replaced with underscores)
- Commands executed sequentially (no parallelism)

## Versioning

Current version: `1.0-Beta`

The system uses semantic versioning with extended tags for development versions.
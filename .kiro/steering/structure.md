# Project Structure

## Directory Layout
```
cashense-simplified/
├── src/                    # Source code
│   ├── __init__.py        # Package initialization
│   ├── main.py            # Application entry point
│   └── gui.py             # Main GUI application class
├── tests/                 # Test files
│   ├── __init__.py        # Test package initialization
│   └── test_main.py       # Main test module
├── .kiro/                 # Kiro AI assistant configuration
│   └── steering/          # AI steering rules
├── venv/                  # Virtual environment (local)
├── .gitignore            # Git ignore rules
├── README.md             # Project documentation
└── requirements.txt      # Python dependencies
```

## File Organization Conventions

### Source Code (`src/`)
- `main.py` - Simple entry point that imports and runs the main GUI
- `gui.py` - Contains the main `CashenseApp` class with all GUI logic
- Keep GUI logic in the main app class
- Use descriptive method names for UI actions

### Tests (`tests/`)
- Mirror the source structure
- Use `test_` prefix for test files
- Include import path setup for testing source modules
- Handle optional dependencies gracefully (e.g., CustomTkinter)

### Configuration
- Virtual environment in `venv/` (not committed)
- Dependencies listed in `requirements.txt`
- Git configuration in `.gitignore`

## Naming Conventions
- Python files: lowercase with underscores (`main.py`, `gui.py`)
- Classes: PascalCase (`CashenseApp`)
- Methods: snake_case (`add_transaction`, `view_balance`)
- Constants: UPPER_SNAKE_CASE

## Import Patterns
- Relative imports within the src package
- External dependencies imported at module level
- Graceful handling of missing optional dependencies in tests
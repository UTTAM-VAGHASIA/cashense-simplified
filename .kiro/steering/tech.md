# Technology Stack

## Core Technologies
- **Python 3.12+** - Primary programming language
- **CustomTkinter** - Modern GUI framework for desktop interface
- **pytest** - Testing framework
- **black** - Code formatting tool

## Development Environment
- Virtual environment using `venv`
- Package management via `pip`
- Git version control

## Code Style & Standards
- **Black** code formatter enforced
- Dark theme UI as default
- Modern, clean interface design
- Object-oriented architecture with main app class
- Always fetch latest documentation from context7 before writing code

## Common Commands

### Environment Setup
```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# Windows:
venv\Scripts\activate
# Unix/macOS:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### Running the Application
```bash
python src/main.py
```

### Testing
```bash
pytest
```

### Code Formatting
```bash
black src/ tests/
```

## Dependencies
- `customtkinter` - GUI framework
- `pytest` - Testing
- `black` - Code formatting

## Architecture Notes
- Entry point: `src/main.py`
- Main application logic: `src/gui.py`
- GUI uses dark theme by default
- Modular design with separate GUI class
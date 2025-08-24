# Cashense-simplified

[![Python Version](https://img.shields.io/badge/python-3.12-blue.svg)](https://www.python.org/)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

A Simplified (Pre-app) version of Cashense. This project is a GUI-based personal finance tracker built in Python using CustomTkinter.

## 📱 Cashense: Your Intelligent Finance Companion

Welcome to **Cashense** — a smart, scalable, and culturally-rooted personal finance application, designed to revolutionize the way individuals manage, track, and optimize their finances.

---

## 🔥 Vision

To empower every individual — from college students to working professionals — to **understand**, **control**, and **grow** their money using intuitive tools, intelligent automation, and community-driven finance features.

> "More than just an app — it's your personal financial conscience."

---

## 🚀 Getting Started

### Prerequisites

*   Python 3.12 or higher
*   `pip` (Python package installer)
*   CustomTkinter for the GUI interface

### Installation

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/your-username/cashense-simplified.git
    cd cashense-simplified
    ```

2.  **Create and activate a virtual environment:**
    ```bash
    python -m venv venv
    source venv/bin/activate  # On Windows, use `venv\Scripts\activate`
    ```

3.  **Install the required dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

### Running the Application

To run the GUI application, execute the following command:

```bash
python src/main.py
```

The application will launch a modern GUI interface with dark theme support.

#### Navigation Features

The application now includes a complete navigation system:

- **Dashboard View**: Main landing screen showing recent cashbooks in a card-based layout
- **Cashbook Detail View**: Detailed view for individual cashbooks with expense entries
- **Breadcrumb Navigation**: Easy navigation back to dashboard with breadcrumb trail
- **Responsive Design**: Adapts to different window sizes and screen resolutions

**Navigation Usage:**
1. Click on any cashbook card in the dashboard to open its detail view
2. Use the "← Dashboard" button or breadcrumb navigation to return to the main dashboard
3. Window title updates to reflect the current view and selected cashbook

### Running Tests

To run the tests, use `pytest`:

```bash
pytest
```

---

## 📂 Project Structure

```
cashense-simplified/
├── src/
│   ├── __init__.py
│   ├── main.py
│   └── gui.py
├── tests/
│   ├── __init__.py
│   └── test_main.py
├── .gitignore
├── README.md
└── requirements.txt
```

---

## 🤝 Contributing

This is a proprietary project and contributions are not accepted at this time.

---

## 📝 License

This project is proprietary and not licensed for reuse. All rights are reserved by the author.

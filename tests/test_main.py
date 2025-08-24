import sys
import os
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

def test_gui_import():
    """Test that the GUI module can be imported successfully"""
    try:
        import gui
        assert hasattr(gui, 'CashenseApp')
        assert hasattr(gui, 'main')
    except ImportError as e:
        # Skip test if CustomTkinter is not installed
        if 'customtkinter' in str(e):
            import pytest
            pytest.skip("CustomTkinter not installed")
        else:
            raise

def test_main():
    assert True

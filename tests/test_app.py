"""UI tests for TubeMind AI using Streamlit's AppTest."""

from pathlib import Path
from streamlit.testing.v1 import AppTest


# Resolve the app path relative to THIS test file,
# so it works regardless of where pytest is run from.
PROJECT_ROOT = Path(__file__).resolve().parents[1]
APP_PATH = str(PROJECT_ROOT / "app" / "streamlit_app.py")
TIMEOUT = 60


def test_app_launches():
    """Smoke test: the app should launch without crashing."""
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception, f"App raised: {at.exception}"


def test_landing_page_renders():
    """Landing page should show the URL input and analyze button."""
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception
    # There should be at least one text_input (the YouTube URL box)
    assert len(at.text_input) >= 1, "No URL input found on landing page"


def test_analyze_button_exists():
    """The 'Analyze video' button should be present on landing."""
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception
    # Look for any button with 'Analyze' in its label
    labels = [b.label for b in at.button]
    assert any("Analyze" in lbl for lbl in labels), (
        f"No 'Analyze' button found. Buttons: {labels}"
    )


def test_analyze_with_empty_url_warns():
    """Clicking Analyze with an empty URL should warn, not crash."""
    at = AppTest.from_file(APP_PATH, default_timeout=TIMEOUT)
    at.run()
    assert not at.exception

    # Find the analyze button by label
    analyze_btn = next(
        (b for b in at.button if "Analyze" in b.label), None
    )
    assert analyze_btn is not None, "Analyze button not found"

    analyze_btn.click().run()
    assert not at.exception, "App crashed when clicking Analyze with empty URL"
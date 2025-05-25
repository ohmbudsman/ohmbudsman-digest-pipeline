import pytest
from src.render_pdf import lint_snap

@pytest.fixture
def sample_md():
    return "\n".join([
        *(f"# Section {i}" for i in range(1,10)),
        "- 📰 First bullet.",
        "- 💡 Second bullet."
    ])

def test_snap_lint_valid(sample_md):
    lint_snap(sample_md)

def test_snap_lint_invalid_heading(sample_md):
    with pytest.raises(ValueError):
        lint_snap(sample_md + "\n# Extra")

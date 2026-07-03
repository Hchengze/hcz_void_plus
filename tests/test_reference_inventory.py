from pathlib import Path


def test_reference_inventory_documents_exist():
    for path in [
        Path("docs/reference_inventory.md"),
        Path("docs/reference_algorithm_admission.md"),
        Path("docs/reference_backed_algorithm_plan.md"),
    ]:
        assert path.exists()
        assert path.read_text(encoding="utf-8")


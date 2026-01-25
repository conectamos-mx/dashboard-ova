from pathlib import Path

p = Path(__file__).resolve()
print(f"File: {p}")
print(f"Parent 1 (backend): {p.parent}")
print(f"Parent 2 (Dashboard OVA): {p.parent.parent}")
print(f"Frontend dir: {p.parent.parent / 'frontend'}")
print(f"Frontend exists: {(p.parent.parent / 'frontend').exists()}")

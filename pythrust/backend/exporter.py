# backend/exporter.py

import os
from pythrust.backend.models import ComponentOutput


def export_component(component: ComponentOutput, output_dir="exports"):
    os.makedirs(output_dir, exist_ok=True)

    with open(os.path.join(output_dir, "component.ts"), "w") as f:
        f.write(component.typescript)

    with open(os.path.join(output_dir, "component.html"), "w") as f:
        f.write(component.html)

    with open(os.path.join(output_dir, "component.css"), "w") as f:
        f.write(component.css)

    return output_dir
#!/usr/bin/env python3
"""
Valida la estructura y completitud de .cs-project.md para el plugin
Axxon Copilot Studio Builder.

Uso:
    python validate_cs_project.py .cs-project.md --require "Casos de uso relevados"

Exit code 0: gate pasado.
Exit code 1: gate bloqueado -- ver "blocking_reasons" en la salida JSON.
"""
import argparse
import json
import re
import sys

REQUIRED_SECTIONS = [
    "Agente",
    "Objetivo y audiencia",
    "Fuentes de referencia",
    "Casos de uso relevados",
    "Restricciones conocidas",
    "Estado",
]

PENDING_MARKERS = {"(pendiente)", "(a confirmar)", ""}


def parse_sections(text):
    sections = {}
    current = None
    buf = []
    for line in text.splitlines():
        m = re.match(r"^##\s+(.*)", line)
        if m:
            if current is not None:
                sections[current] = "\n".join(buf).strip()
            current = m.group(1).strip()
            buf = []
        else:
            buf.append(line)
    if current is not None:
        sections[current] = "\n".join(buf).strip()
    return sections


def section_is_empty(content):
    stripped = content.strip()
    if not stripped:
        return True
    lines = [l.strip("-* \t") for l in stripped.splitlines() if l.strip()]
    non_marker_lines = [
        l for l in lines
        if l.lower() not in PENDING_MARKERS and "(pendiente)" not in l.lower()
    ]
    return len(non_marker_lines) == 0


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("--require", action="append", default=[])
    args = parser.parse_args()

    try:
        with open(args.path, "r", encoding="utf-8") as f:
            text = f.read()
    except FileNotFoundError:
        print(json.dumps({
            "structurally_valid": False,
            "blocking_reasons": [
                f"No existe el archivo {args.path}. Correr agent-intake primero."
            ],
        }, ensure_ascii=False, indent=2))
        sys.exit(1)

    sections = parse_sections(text)
    missing_sections = [s for s in REQUIRED_SECTIONS if s not in sections]
    structurally_valid = len(missing_sections) == 0

    blocking_reasons = []
    if not structurally_valid:
        blocking_reasons.append(
            "Faltan secciones obligatorias: " + ", ".join(missing_sections) +
            ". El archivo esta incompleto o corrupto -- correr agent-intake para repararlo."
        )

    incomplete_required = []
    if structurally_valid:
        for req in args.require:
            if req not in sections:
                incomplete_required.append(f"{req} (seccion inexistente)")
            elif section_is_empty(sections[req]):
                incomplete_required.append(req)

    if incomplete_required:
        blocking_reasons.append(
            "Secciones requeridas incompletas: " + ", ".join(incomplete_required)
        )

    result = {
        "structurally_valid": structurally_valid,
        "sections_found": list(sections.keys()),
        "missing_sections": missing_sections,
        "required_checked": args.require,
        "incomplete_required": incomplete_required,
        "blocking_reasons": blocking_reasons,
    }

    print(json.dumps(result, ensure_ascii=False, indent=2))
    sys.exit(0 if not blocking_reasons else 1)


if __name__ == "__main__":
    main()

"""Genera o verifica la edición Markdown completa de la skill, sin acceso a red."""
from __future__ import annotations

import argparse
import hashlib
import json
from pathlib import Path
import re


def render(skill_root: Path) -> str:
    main = skill_root / "SKILL.md"
    refs = sorted((skill_root / "references").glob("*.md"))
    if len(refs) != 7:
        raise ValueError("Se esperan siete anexos; actualiza el generador si cambia el paquete.")
    anchors = {p.name: f"anexo-{p.stem}" for p in refs}
    anchors["ficha-ejemplo.json"] = "ficha-json"
    sources = [main, *refs]

    for path in sources:
        content = path.read_text(encoding="utf-8")
        for target in re.findall(r"\]\(([^)]+)\)", content):
            if target.startswith(("https://", "http://", "#")):
                continue
            if not (path.parent / target.split("#", 1)[0]).is_file():
                raise ValueError(f"Enlace local inexistente en {path.name}: {target}")
        if content.count("```") % 2:
            raise ValueError(f"Bloque de código sin cerrar: {path.name}")

    def rewrite(content: str) -> str:
        def replace(match: re.Match[str]) -> str:
            label, target = match.groups()
            anchor = anchors.get(Path(target).name)
            if anchor and not target.startswith(("https://", "http://")):
                return f"[{label}](#{anchor})"
            return match.group(0)
        return re.sub(r"\[([^\]]+)\]\(([^)]+)\)", replace, content)

    raw = (skill_root / "assets" / "original-ejemplo.txt").read_bytes()
    example = json.loads((skill_root / "assets" / "ficha-ejemplo.json").read_text(encoding="utf-8"))
    if example["archivo"]["sha256"] != hashlib.sha256(raw).hexdigest():
        raise ValueError("El SHA-256 del ejemplo no coincide con el TXT sintético.")
    if example["archivo"]["tamano_bytes"] != len(raw):
        raise ValueError("El tamaño del ejemplo no coincide con el TXT sintético.")

    body = re.sub(r"\A---\n.*?\n---\n", "", main.read_text(encoding="utf-8"), count=1, flags=re.S)
    index = "\n".join(
        f"- [{p.read_text(encoding='utf-8').splitlines()[0].lstrip('# ')}](#{anchors[p.name]})"
        for p in refs
    )
    parts = [
        "# Skill completa para implementar CargaDocumentosDocIAPlus\n\n"
        "Edición unificada para adjuntar a cualquier asistente de IA. Contiene la skill, "
        "sus siete anexos y una ficha sintética. Se genera desde `skills/carga-documentos-docia-s3/`; "
        "edita allí las fuentes y vuelve a generar este archivo.\n\n"
        "Define una implementación con Python, S3 privado, MVC y separación hexagonal. "
        "Es una especificación de desarrollo; no ejecuta la aplicación ni crea recursos AWS.\n\n"
        "## Índice de anexos\n\n" + index + "\n- [Ficha JSON y original sintéticos](#ficha-json)\n",
        rewrite(body).strip(),
    ]
    for path in refs:
        parts.append(f'<a id="{anchors[path.name]}"></a>\n\n' + rewrite(path.read_text(encoding="utf-8")).strip())
    parts.append(
        '<a id="ficha-json"></a>\n\n# Ficha JSON y original sintéticos\n\n'
        "No corresponde a un objeto ya subido a S3. El SHA-256 y tamaño se calculan sobre "
        "`assets/original-ejemplo.txt` del paquete, con codificación UTF-8 y finales de línea LF. "
        "Si un editor cambia los bytes, cambia también la huella.\n\n"
        "```json\n" + json.dumps(example, ensure_ascii=False, indent=2) + "\n```\n\n"
        "Contenido del original de ejemplo:\n\n```text\n" + raw.decode("utf-8") + "```"
    )
    output = "\n\n".join(parts) + "\n"
    for anchor in re.findall(r"\]\(#([^)]*)\)", output):
        if f'id="{anchor}"' not in output:
            raise ValueError(f"Ancla no encontrada: {anchor}")
    return output


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, default=root.parents[1] / "docs" / "SKILL_CargaDocumentosDocIAPlus.md")
    parser.add_argument("--check", action="store_true", help="Comprueba que la edición generada está actualizada sin escribir.")
    args = parser.parse_args()
    expected = render(root)
    if args.check:
        if not args.output.is_file() or args.output.read_text(encoding="utf-8") != expected:
            parser.error("La edición completa falta o está desactualizada. Ejecuta este script sin --check.")
        print("Skill y edición completa coherentes; enlaces y ficha sintética verificados.")
        return 0
    args.output.parent.mkdir(parents=True, exist_ok=True)
    args.output.write_text(expected, encoding="utf-8", newline="\n")
    print(f"Edición generada: {args.output}")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())

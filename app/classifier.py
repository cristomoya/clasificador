#!/usr/bin/env python3
"""
Clasificador de documentos municipales de contratación.
Fase 1: reglas sobre el nombre del fichero (gratis).
Fase 2: IA (Haiku) solo para los campos que las reglas no resolvieron.
"""

import os
import re
import csv
import json
import shutil
import logging
from pathlib import Path

import anthropic
from tqdm import tqdm

from taxonomy import REGLAS, TIPOS_CONTRATO, TIPOS_PROCEDIMIENTO, TIPOS_ACTO

# ─── Configuración ────────────────────────────────────────────────────────────
INPUT_DIR   = Path("/data/input")
OUTPUT_DIR  = Path("/data/output")
RESULTS_DIR = Path("/data/results")
CSV_PATH    = RESULTS_DIR / "clasificacion.csv"

SUPPORTED_EXT = {".doc", ".docx", ".odt", ".pdf", ".txt"}
SKIP_FILES    = {"sub recorreryremplazarpalabrasentriellav.vb"}   # ficheros a ignorar

logging.basicConfig(level=logging.INFO, format="%(levelname)s %(message)s")
log = logging.getLogger(__name__)

client = anthropic.Anthropic(api_key=os.environ["ANTHROPIC_API_KEY"])


# ─── Fase 1: reglas sobre el nombre ──────────────────────────────────────────

def apply_rules(filename: str) -> dict:
    """Aplica las reglas de taxonomy.py sobre el nombre del fichero."""
    upper = filename.upper()
    result = {"contrato": None, "procedimiento": None, "acto": None}

    for patron, contrato, procedimiento, acto in REGLAS:
        if patron.upper() in upper:
            if contrato      and not result["contrato"]:
                result["contrato"] = contrato
            if procedimiento and not result["procedimiento"]:
                result["procedimiento"] = procedimiento
            if acto          and not result["acto"]:
                result["acto"] = acto

    return result


def is_complete(r: dict) -> bool:
    return all(r[k] for k in ("contrato", "procedimiento", "acto"))


# ─── Extracción de texto (solo primeras líneas para ahorrar tokens) ───────────

def extract_snippet(path: Path, max_chars: int = 600) -> str:
    """Extrae los primeros max_chars del texto del documento."""
    ext = path.suffix.lower()
    try:
        if ext == ".txt":
            return path.read_text(errors="ignore")[:max_chars]

        if ext in (".doc", ".docx"):
            from docx import Document
            doc = Document(str(path))
            text = "\n".join(p.text for p in doc.paragraphs)
            return text[:max_chars]

        if ext == ".odt":
            from odf.opendocument import load
            from odf.text import P
            doc = load(str(path))
            paras = doc.getElementsByType(P)
            text = "\n".join(
                "".join(n.data for n in p.childNodes if hasattr(n, "data"))
                for p in paras
            )
            return text[:max_chars]

        if ext == ".pdf":
            from pypdf import PdfReader
            reader = PdfReader(str(path))
            text = ""
            for page in reader.pages[:2]:
                text += page.extract_text() or ""
                if len(text) >= max_chars:
                    break
            return text[:max_chars]

    except Exception as e:
        log.warning(f"No se pudo leer {path.name}: {e}")

    return ""


# ─── Fase 2: clasificación con IA (Haiku) ─────────────────────────────────────

SYSTEM_PROMPT = f"""Eres un asistente experto en contratación pública municipal española.
Clasifica el documento según estas listas EXACTAS (usa el texto exactamente como aparece):

TIPOS_CONTRATO: {json.dumps(TIPOS_CONTRATO, ensure_ascii=False)}
TIPOS_PROCEDIMIENTO: {json.dumps(TIPOS_PROCEDIMIENTO, ensure_ascii=False)}
TIPOS_ACTO: {json.dumps(TIPOS_ACTO, ensure_ascii=False)}

Responde ÚNICAMENTE con un objeto JSON con las claves:
  "contrato", "procedimiento", "acto"

Si no puedes determinarlo, usa null.
Sin explicaciones. Sin markdown. Solo el JSON."""


def classify_with_ai(filename: str, snippet: str, partial: dict) -> dict:
    """Llama a Haiku solo para los campos que faltan."""
    missing = [k for k in ("contrato", "procedimiento", "acto") if not partial[k]]
    if not missing:
        return partial

    already = {k: v for k, v in partial.items() if v}
    prompt = (
        f"Nombre del fichero: {filename}\n"
        f"Primeras líneas del documento:\n{snippet}\n\n"
        f"Ya clasificado: {json.dumps(already, ensure_ascii=False)}\n"
        f"Necesito determinar: {missing}"
    )

    try:
        response = client.messages.create(
            model="claude-haiku-4-5-20251001",
            max_tokens=150,
            system=SYSTEM_PROMPT,
            messages=[{"role": "user", "content": prompt}],
        )
        raw = response.content[0].text.strip()
        # Limpiar posibles backticks
        raw = re.sub(r"```(?:json)?", "", raw).strip()
        ai_result = json.loads(raw)

        # Fusionar: las reglas tienen prioridad, la IA rellena los huecos
        for k in missing:
            if ai_result.get(k):
                partial[k] = ai_result[k]

    except Exception as e:
        log.warning(f"Error IA para {filename}: {e}")

    return partial


# ─── Copia de ficheros ────────────────────────────────────────────────────────

def safe_folder_name(name: str) -> str:
    """Elimina caracteres no válidos en nombres de carpeta."""
    return re.sub(r'[<>:"/\\|?*]', "-", name).strip()


def copy_to_output(src: Path, classification: dict) -> str:
    contrato     = safe_folder_name(classification["contrato"]     or "_Sin_Contrato")
    procedimiento = safe_folder_name(classification["procedimiento"] or "_Sin_Procedimiento")
    acto         = safe_folder_name(classification["acto"]         or "_Sin_Acto")

    dest_dir = OUTPUT_DIR / contrato / procedimiento / acto
    dest_dir.mkdir(parents=True, exist_ok=True)

    dest = dest_dir / src.name
    # Si ya existe un fichero con el mismo nombre, añadir sufijo
    if dest.exists():
        dest = dest_dir / f"{src.stem}__{src.parent.name}{src.suffix}"

    shutil.copy2(src, dest)
    return str(dest.relative_to(OUTPUT_DIR))


# ─── Bucle principal ──────────────────────────────────────────────────────────

def main():
    files = [
        f for f in INPUT_DIR.rglob("*")
        if f.is_file()
        and f.suffix.lower() in SUPPORTED_EXT
        and f.name.lower() not in SKIP_FILES
    ]

    if not files:
        log.error(f"No se encontraron documentos en {INPUT_DIR}")
        return

    log.info(f"Documentos encontrados: {len(files)}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)

    stats = {"reglas": 0, "ia": 0, "sin_clasificar": 0}
    rows  = []

    for path in tqdm(files, desc="Clasificando"):
        classification = apply_rules(path.name)
        fuente = "reglas"

        if not is_complete(classification):
            snippet = extract_snippet(path)
            classification = classify_with_ai(path.name, snippet, classification)
            fuente = "ia+reglas" if any(classification.values()) else "ia"
            stats["ia"] += 1
        else:
            stats["reglas"] += 1

        if not any(classification.values()):
            stats["sin_clasificar"] += 1

        dest_path = copy_to_output(path, classification)

        rows.append({
            "nombre_original":  path.name,
            "contrato":         classification["contrato"]      or "",
            "procedimiento":    classification["procedimiento"] or "",
            "acto":             classification["acto"]          or "",
            "fuente":           fuente,
            "ruta_destino":     dest_path,
        })

    # Escribir CSV
    with open(CSV_PATH, "w", newline="", encoding="utf-8-sig") as f:
        writer = csv.DictWriter(f, fieldnames=rows[0].keys())
        writer.writeheader()
        writer.writerows(rows)

    log.info("─" * 50)
    log.info(f"✓ Clasificados por reglas : {stats['reglas']}")
    log.info(f"✓ Clasificados con IA     : {stats['ia']}")
    log.info(f"✗ Sin clasificar          : {stats['sin_clasificar']}")
    log.info(f"CSV generado en           : {CSV_PATH}")
    log.info(f"Documentos copiados en    : {OUTPUT_DIR}")


if __name__ == "__main__":
    main()

import os
import re
import json
import sys
import io
from rich.console import Console
from rich.table import Table
from rich.panel import Panel

# Forzar encoding UTF-8 para evitar errores en Windows con emojis
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

console = Console()

MANDATORY_HEADERS = [
    r"^#\s+\[?[\w\-]+\]?\s+—\s+.+",      # Title
    r"^>\s+Milestone:\s+[\w\-]+",  # Metadata
    r"## Objetivo",
    r"## Dependencias consumidas",
    r"## Archivos",
    r"## Tipos esperados",
    r"## Decisiones técnicas",
    r"### Datos",
    r"### Acceso / Seguridad",
    r"### UI / Contrato de componentes",
    r"## Tests",
    r"## Estados UI requeridos",
    r"## Fuera de scope",
    r"## Criterio de salida"
]

HEADER_LABELS = {
    MANDATORY_HEADERS[0]: "Título Estándar",
    MANDATORY_HEADERS[1]: "Metadatos (Milestone)",
    MANDATORY_HEADERS[2]: "Objetivo",
    MANDATORY_HEADERS[3]: "Dependencias",
    MANDATORY_HEADERS[4]: "Archivos",
    MANDATORY_HEADERS[5]: "Tipos esperados",
    MANDATORY_HEADERS[6]: "Decisiones técnicas",
    MANDATORY_HEADERS[7]: "Decisión: Datos",
    MANDATORY_HEADERS[8]: "Decisión: Seguridad",
    MANDATORY_HEADERS[9]: "Decisión: UI",
    MANDATORY_HEADERS[10]: "Tests",
    MANDATORY_HEADERS[11]: "Estados UI",
    MANDATORY_HEADERS[12]: "Fuera de scope",
    MANDATORY_HEADERS[13]: "Criterio de salida"
}

def audit_description(task_id, description):
    """Audita la descripción de una tarea contra los 14 puntos del Antigravity Standard.
    
    Args:
        task_id: Identificador de la tarea.
        description: Texto completo en Markdown de la descripción de la tarea.
    
    Returns:
        Tupla (score: int, findings: list[str]) con el porcentaje de fidelidad y los hallazgos.
    """
    score = 100
    findings = []
    
    if not description or len(description) < 50:
        return 0, ["Descripción vacía o demasiado corta"]

    # 0. Normalización Total (Tirano Standard)
    # Eliminamos tags, normalizamos saltos de linea y quitamos espacios en extremos
    clean_desc = re.sub(r"<.*?>", "", description)
    clean_desc = clean_desc.replace('\r\n', '\n').strip()

    # 1. Headers Obligatorios (Deducción: -5 por cada uno)
    for pattern in MANDATORY_HEADERS:
        if not re.search(pattern, clean_desc, re.MULTILINE | re.IGNORECASE):
            score -= 5
            findings.append(f"Falta: {HEADER_LABELS.get(pattern, 'Sección desconocida')}")

    # 2. Extracción Centralizada de Archivos Declarados (Contrato Maestro)
    files_to_create = []
    archivos_section = re.search(r"## Archivos(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
    if archivos_section:
        files_to_create = re.findall(r"[`'](.*?)['`]", archivos_section.group(1))

    # 3. Consistencia: CREATE -> Tipos
    if archivos_section:
        files_with_create = re.findall(r"[`'](.*?)['`].*?\|\s*CREATE", archivos_section.group(1), re.IGNORECASE)
        if files_with_create:
            if "## Tipos esperados" in clean_desc:
                tipos_content = clean_desc.split("## Tipos esperados")[-1].split("##")[0]
                if "```" not in tipos_content:
                    score -= 10
                    findings.append("Contrato: Se declaran CREATE pero falta bloque de código en Tipos")
            else:
                score -= 10
                findings.append("Contrato: Se declaran CREATE pero falta header '## Tipos esperados'")

    # 4. Paridad Relacional Estricta: Tests vs Archivos Declarados
    tests_section = re.search(r"## Tests(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
    if tests_section:
        test_mentions = re.findall(r"[`'](.*?)['`]", tests_section.group(1))
        for tm in test_mentions:
            if not tm.strip(): continue
            # Debe estar declarado en los archivos a tocar (create o modify)
            is_declared = any(tm in f for f in files_to_create) if files_to_create else False
            
            if not is_declared:
                score -= 10
                findings.append(f"Violación de Contrato: Test '{tm}' no declarado en sección Archivos")

    # 4.5. Prevención de Orfandad de UI (Integration-Last Rule)
    if archivos_section:
        visual_creates = re.findall(r"[`'](.*?\.tsx|.*?\.jsx|.*?\.vue|.*?\.html)['`].*?\|\s*CREATE", archivos_section.group(1), re.IGNORECASE)
        if visual_creates:
            files_with_modify = re.findall(r"[`'](.*?)['`].*?\|\s*MODIFY", archivos_section.group(1), re.IGNORECASE)
            has_integration = any(any(k in f.lower() for k in ['page', 'layout', 'app', 'index', 'router', 'main']) for f in files_with_modify)
            
            if not has_integration and "Integration" not in clean_desc:
                score -= 5
                findings.append(f"Orfandad UI: Se crea visual ({visual_creates[0]}) sin MODIFY en router/layout")

    # 5. Granularidad: ## Objetivo >= 30 palabras
    objetivo_match = re.search(r"## Objetivo(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
    if objetivo_match:
        obj_text = objetivo_match.group(1).strip()
        word_count = len(obj_text.split())
        if word_count < 30:
            score -= 10
            findings.append(f"Objetivo vago ({word_count} palabras, requiere 30+)")

    # 6. Densidad Semántica (Anti-Filler)
    filler_patterns = [r"N/A", r"TBD", r"Por definir", r"Completar"]
    for fp in filler_patterns:
        if re.search(fp, clean_desc, re.IGNORECASE):
            score -= 5
            findings.append(f"Baja densidad: Uso de '{fp}' detectado")
            break

    return max(0, min(100, int(score))), findings


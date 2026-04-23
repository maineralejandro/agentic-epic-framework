import os
import re
import json
import sys
import io
from rich.console import Console
from rich.table import Table
from rich.panel import Panel


console = Console()

MANDATORY_HEADERS = [
    r"^#\s+\[?[\w\-]+\]?\s+—\s+.+",      # Title
    r"^\>\s+Milestone:\s+[\w\-]+",  # Metadata
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

# Regex para detectar filas separadoras de tabla MD (|---|, |:---|, |:---:|, |---:|)
_TABLE_SEPARATOR_RE = re.compile(r'^\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)*\|?$')

def _is_table_separator(line):
    """Detecta separadores de tabla MD en cualquier variante de alineación."""
    return bool(_TABLE_SEPARATOR_RE.match(line.strip()))

def extract_table_data(section_content):
    """Extrae datos estructurados de una tabla Markdown.
    
    Detecta headers y separadores de forma estructural (no por nombre de columna),
    lo que lo hace agnóstico al idioma y al formato de tabla.
    
    Retorna una lista de tuplas (columna_1, fila_completa) para validaciones semánticas.
    """
    if not section_content:
        return []
    
    results = []
    lines = section_content.strip().split('\n')
    table_lines = [l for l in lines if l.strip().startswith('|') and l.count('|') >= 2]
    
    for i, line in enumerate(table_lines):
        stripped = line.strip()
        
        # Saltar separadores (|---|:---:|---:| etc.)
        if _is_table_separator(stripped):
            continue
        
        # Saltar header (fila inmediatamente antes de un separador)
        next_line = table_lines[i + 1] if i + 1 < len(table_lines) else None
        if next_line and _is_table_separator(next_line):
            continue
        
        # Extraer celdas y limpiar backticks/espacios
        cells = [re.sub(r"[`']", "", c).strip() for c in stripped.split('|')]
        # cells[0] es '' (antes del primer |), cells[1] es la primera columna real
        if len(cells) > 1 and cells[1]:
            results.append((cells[1], line))
    
    return results


def audit_description(task_id, description):
    """Audita la descripción de una tarea con el modelo de Dos Gates.
    
    Gate 1 — Integridad Estructural (binario PASS/BLOCK):
        Valida que la tarea contiene toda la información necesaria para que
        un agente autónomo pueda ejecutarla sin ambigüedad.
        Cualquier fallo en Gate 1 bloquea la compilación de la tarea.
    
    Gate 2 — Calidad de Diseño (score 0-100, informativo):
        Evalúa la robustez del diseño. Un score bajo no bloquea, pero
        señala oportunidades de mejora visibles en los metadatos del JSON.
    
    Returns:
        dict: {
            "integrity": {"pass": bool, "blockers": [str]},
            "quality": {"score": int, "findings": [str]}
        }
    """
    gate1_blockers = []
    quality_score = 100
    quality_findings = []
    
    if not description or len(description) < 50:
        return {
            "integrity": {"pass": False, "blockers": ["Descripción vacía o demasiado corta"]},
            "quality": {"score": 0, "findings": []}
        }

    # 0. Normalización Segura (Preserva genéricos como Array<string>)
    clean_desc = description.replace('\r\n', '\n').strip()

    # ═══════════════════════════════════════════════════════════
    # GATE 1: INTEGRIDAD ESTRUCTURAL (Cualquier fallo = BLOCK)
    # ═══════════════════════════════════════════════════════════

    # 1.1 Headers Obligatorios — Sin ellos, el agente no sabe qué hacer
    for pattern in MANDATORY_HEADERS:
        if not re.search(pattern, clean_desc, re.MULTILINE | re.IGNORECASE):
            gate1_blockers.append(f"Falta sección: {HEADER_LABELS.get(pattern, 'Desconocida')}")

    # 1.2 Anti-Filler — Placeholders causan alucinación en agentes
    filler_patterns = [r"\bN/A\b", r"\bTBD\b", r"\bPor definir\b", r"\bCompletar\b"]
    for fp in filler_patterns:
        if re.search(fp, clean_desc, re.IGNORECASE):
            gate1_blockers.append(f"Placeholder no permitido: '{fp.replace(chr(92) + 'b', '')}'")
            break

    # 1.3 Contrato CREATE → Tipos — Archivos sin tipos = agente adivina
    files_declared = set()
    files_to_create = set()
    
    archivos_section = re.search(r"## Archivos(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
    if archivos_section:
        table_data = extract_table_data(archivos_section.group(1))
        for filename, full_line in table_data:
            files_declared.add(filename)
            if "CREATE" in full_line.upper():
                files_to_create.add(filename)

    if files_to_create:
        tipos_section = re.search(r"## Tipos esperados(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
        tipos_content = tipos_section.group(1) if tipos_section else ""
        if "```" not in tipos_content:
            gate1_blockers.append(
                f"Contrato roto: {len(files_to_create)} archivos CREATE sin bloque de código en Tipos"
            )

    # 1.4 Tests: tabla no vacía y cada test con casos clave descritos
    tests_section = re.search(r"## Tests(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
    if tests_section:
        test_table = extract_table_data(tests_section.group(1))
        files_in_tests = {t[0] for t in test_table}
        
        # Gate 1: Al menos un test declarado
        if len(test_table) == 0:
            gate1_blockers.append(
                "Tests vacíos: La sección ## Tests no contiene ningún test declarado"
            )
        else:
            # Gate 1: Verificar que "Casos clave" (tercera columna) no esté vacía
            for filename, full_line in test_table:
                cells = [c.strip() for c in full_line.strip().split('|')]
                # cells: ['', col1, col2, col3, ''] para | col1 | col2 | col3 |
                if len(cells) >= 4:
                    casos_clave = cells[3].strip()
                    if not casos_clave or casos_clave.lower() in ['tbd', 'n/a', 'por definir', '']:
                        gate1_blockers.append(
                            f"Test '{filename}' sin casos clave descritos"
                        )
        
        # Gate 1: Referencias fantasma — test que no existe en Archivos
        unknown_tests = files_in_tests - files_declared
        for ut in unknown_tests:
            # Heurística: Si no tiene punto o slash, es texto vago, no un archivo real
            if "." in ut or "/" in ut:
                gate1_blockers.append(f"Test fantasma: '{ut}' no declarado en sección Archivos")

    # ═══════════════════════════════════════════════════════════
    # GATE 2: CALIDAD DE DISEÑO (Score informativo, no bloquea)
    # ═══════════════════════════════════════════════════════════

    # 2.1 Granularidad: ## Objetivo >= 30 palabras
    objetivo_match = re.search(r"## Objetivo(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
    if objetivo_match:
        obj_text = objetivo_match.group(1).strip()
        word_count = len(obj_text.split())
        if word_count < 30:
            quality_score -= 10
            quality_findings.append(f"Objetivo corto ({word_count} palabras, recomendado 30+)")

    # 2.2 Prevención de Orfandad de UI (Integration-Last Rule)
    if archivos_section:
        visual_extensions = ('.tsx', '.jsx', '.vue', '.html')
        visual_creates = [f for f in files_to_create if any(f.endswith(ext) for ext in visual_extensions)]
        
        if visual_creates:
            files_with_modify = files_declared - files_to_create  # MODIFY = declarados pero no CREATE
            has_integration = any(
                any(k in f.lower() for k in ['page', 'layout', 'app', 'index', 'router', 'main'])
                for f in files_with_modify
            )
            
            if not has_integration and "Integration" not in clean_desc:
                quality_score -= 5
                quality_findings.append(
                    f"Orfandad UI: Se crea visual ({visual_creates[0]}) sin MODIFY en router/layout"
                )

    # 2.3 Ratio de cobertura de tests (informativo, sin penalización)
    if tests_section and files_declared:
        test_table_data = extract_table_data(tests_section.group(1))
        files_in_tests_set = {t[0] for t in test_table_data}
        covered = len(files_in_tests_set & files_declared)
        total = len(files_declared)
        coverage_ratio = (covered / total) * 100 if total > 0 else 0
        quality_findings.append(
            f"Cobertura de tests: {coverage_ratio:.0f}% ({covered}/{total} archivos)"
        )

    return {
        "integrity": {
            "pass": len(gate1_blockers) == 0,
            "blockers": gate1_blockers
        },
        "quality": {
            "score": max(0, min(100, int(quality_score))),
            "findings": quality_findings
        }
    }

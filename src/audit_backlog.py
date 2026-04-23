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

# Regex para detectar filas separadoras de tabla MD (|---|, |:---|, |:---:|, |---:|)
_TABLE_SEPARATOR_RE = re.compile(r'^\|?\s*:?-{2,}:?\s*(?:\|\s*:?-{2,}:?\s*)*\|?$')

def _is_table_separator(line):
    """Detecta separadores de tabla MD en cualquier variante de alineación."""
    return bool(_TABLE_SEPARATOR_RE.match(line.strip()))

def _is_table_header(line, is_first_data_row, next_line=None):
    """Detecta si una fila de tabla es el header (la fila antes del separador)."""
    if next_line and _is_table_separator(next_line):
        return True
    return is_first_data_row

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
    """Audita la descripción de una tarea contra los 14 puntos del Antigravity Standard.
    
    Utiliza un enfoque de "Contrato Maestro" basado en conjuntos (Sets) para
    eliminar falsos positivos y asegurar integridad referencial estricta.
    """
    score = 100
    findings = []
    
    if not description or len(description) < 50:
        return 0, ["Descripción vacía o demasiado corta"]

    # 0. Normalización Segura (Preserva genéricos como Array<string>)
    clean_desc = description.replace('\r\n', '\n').strip()

    # 1. Headers Obligatorios (Deducción: -5 por cada uno)
    for pattern in MANDATORY_HEADERS:
        if not re.search(pattern, clean_desc, re.MULTILINE | re.IGNORECASE):
            score -= 5
            findings.append(f"Falta: {HEADER_LABELS.get(pattern, 'Sección desconocida')}")

    # 2. Extracción del "Contrato Maestro" (Sección Archivos)
    files_declared = set()
    files_to_create = set()
    
    archivos_section = re.search(r"## Archivos(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
    if archivos_section:
        table_data = extract_table_data(archivos_section.group(1))
        for filename, full_line in table_data:
            files_declared.add(filename)
            if "CREATE" in full_line.upper():
                files_to_create.add(filename)
    else:
        # Si no hay sección de archivos, ya se restó en el paso 1, pero aquí evitamos crash
        pass

    # 3. Consistencia: CREATE -> Tipos
    if files_to_create:
        if "## Tipos esperados" in clean_desc:
            tipos_section = re.search(r"## Tipos esperados(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
            tipos_content = tipos_section.group(1) if tipos_section else ""
            if "```" not in tipos_content:
                score -= 10
                findings.append(f"Contrato: Se declaran CREATE ({len(files_to_create)} archivos) pero falta bloque de código en Tipos")
        else:
            score -= 10
            findings.append("Contrato: Se declaran CREATE pero falta header '## Tipos esperados'")

    # 4. Paridad Relacional Estricta: Tests vs Archivos Declarados
    tests_section = re.search(r"## Tests(.*?)(##|$)", clean_desc, re.DOTALL | re.IGNORECASE)
    if tests_section:
        test_table = extract_table_data(tests_section.group(1))
        files_in_tests = {t[0] for t in test_table}
        
        # Violación: Archivo en Tests que no existe en la sección Archivos
        unknown_tests = files_in_tests - files_declared
        for ut in unknown_tests:
            # Heurística: Si no tiene punto o slash, probablemente sea un error de parseo o texto vago
            if "." in ut or "/" in ut:
                score -= 10
                findings.append(f"Violación de Contrato: Test '{ut}' no declarado en sección Archivos")
        
        # Auditoría Proactiva (Staff level): Archivos sin tests
        uncovered = files_declared - files_in_tests
        if uncovered:
            # No restamos score por ahora para no ser punitivos, pero informamos
            findings.append(f"Calidad: {len(uncovered)} archivos declarados no tienen test asociado (ej: {list(uncovered)[0]})")

    # 4.5. Prevención de Orfandad de UI (Integration-Last Rule)
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


import re
import json
import os
from datetime import datetime

# ============================================================================
# PATRONES DE ID GENERALIZADOS
# ============================================================================
# Formato de IDs soportado (flexible para cualquier proyecto):
#   Epic:      [PREFIJO]-[NN]         → E-01, FEAT-01, CORE-03, INFRA-01
#   Milestone: [PREFIJO]-[NN]         → M1-01, MS-01, MILE-03
#   Task:      [PREFIJO][NN]-T[NN]    → E01-T01, FEAT01-T03, CORE03-T12
#
# Reglas (Git-safe + AI-safe):
#   - Solo alfanuméricos y guiones (válido para branches de Git)
#   - El delimitador " — " (espacio-guión largo-espacio) separa ID de Título
#   - Sin emojis en los IDs (los emojis son decorativos, no parseables)
# ============================================================================

# Regex para capturar IDs de tareas: cualquier WORD seguido de -T y dígitos
TASK_ID_PATTERN = r'[\w]+-T\d+'
# Regex para el header de la épica (acepta emoji opcional antes del ID)
EPIC_HEADER_PATTERN = r'#\s+(?:[\U00010000-\U0010ffff]\s+)?([\w]+-\d+)\s+—\s+(.+)'
# Regex para milestones
MILESTONE_PATTERN = r'###\s+([\w]+-\d+)\s+—\s+([^\n]+)\n\*\*Transición\*\*:\s*`([^`]+)`\s*\n\n\*\*Test de integración de milestone\*\*:\s*([^\n]+)'


def parse_epic_md(file_path):
    """Parsea un archivo Markdown de épica y retorna un diccionario JSON estructurado.
    
    Soporta cualquier formato de ID que siga la convención:
    - Epic: PREFIX-NN (ej. E-01, FEAT-01)
    - Task: PREFIXNN-TNN (ej. E01-T01, FEAT01-T03)
    - Milestone: PREFIX-NN (ej. M1-01, MS-01)
    """
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()

    # Estructura del JSON resultante
    epic_json = {
        "epic": {},
        "milestones": [],
        "execution_metadata": {
            "generated_at": datetime.now().isoformat(),
            "source_file": os.path.basename(file_path),
            "signature": {
                "status": "DRAFT",
                "approved_by": None,
                "approved_at": None
            }
        },
        "tasks": []
    }

    # 1. Parsear Resumen de la Épica (Header)
    epic_header_match = re.search(EPIC_HEADER_PATTERN, content)
    if epic_header_match:
        epic_json["epic"]["id"] = epic_header_match.group(1).strip()
        epic_json["epic"]["name"] = epic_header_match.group(2).strip()

    # Parsear tabla de resumen para extraer estados y stack
    stack_match = re.search(r'\|\s*Stack\s*\|\s*(.+?)\s*\|', content)
    if stack_match:
        epic_json["epic"]["stack"] = [s.strip() for s in stack_match.group(1).split('·')]

    initial_state = re.search(r'\|\s*Estado inicial\s*\|\s*(.+?)\s*\|', content)
    if initial_state:
        epic_json["epic"]["initial_state"] = initial_state.group(1).strip()

    final_state = re.search(r'\|\s*Estado final\s*\|\s*(.+?)\s*\|', content)
    if final_state:
        epic_json["epic"]["final_state"] = final_state.group(1).strip()

    # 2. Parsear Milestones
    milestones_section = re.search(r'## Milestones(.*?)## Tasks', content, re.DOTALL)
    if milestones_section:
        ms_blocks = re.findall(MILESTONE_PATTERN, milestones_section.group(1))
        for ms_id, ms_name, transition, test in ms_blocks:
            epic_json["milestones"].append({
                "id": ms_id.strip(),
                "name": ms_name.strip(),
                "transition": transition.strip(),
                "integration_test": test.strip()
            })

    # 3. Parsear Tareas
    # Dividimos el contenido en bloques usando el patrón generalizado de tareas
    task_split_pattern = rf'\n# (?={TASK_ID_PATTERN} — )'
    task_blocks = re.split(task_split_pattern, content)
    
    # El primer bloque es el intro (Epic, Milestones), lo ignoramos
    for block in task_blocks[1:]:
        # Re-agregamos el "# " que el split quitó
        full_block = "# " + block
        
        # Extraer ID y Título (generalizado)
        title_match = re.match(rf'# ({TASK_ID_PATTERN}) — ([^\n]+)', full_block)
        if not title_match:
            continue
            
        task_id = title_match.group(1).strip()
        task_title = title_match.group(2).strip()
        
        # Extraer Milestone y Riesgo (generalizado)
        meta_match = re.search(r'> Milestone: ([\w]+-\d+)[^·]+· Risk: (Bajo|Medio|Alto)', full_block)
        milestone_id = meta_match.group(1).strip() if meta_match else ""
        risk = meta_match.group(2).strip().upper() if meta_match else "MEDIO"

        # Generar branch name limpio (git-safe)
        epic_id = epic_json['epic'].get('id', 'unknown')
        epic_name = epic_json['epic'].get('name', 'feature')
        branch_name = re.sub(r'[^a-zA-Z0-9\-]', '-', epic_name).strip('-').lower()

        epic_json["tasks"].append({
            "id": task_id,
            "title": task_title,
            "milestone_id": milestone_id,
            "target_branch": f"epic/{epic_id}-{branch_name}",
            "priority": risk,
            "status": "draft",
            "created_at": datetime.now().isoformat(),
            "description": full_block.strip()
        })

    # Actualizar contadores
    epic_json["execution_metadata"]["total_tasks"] = len(epic_json["tasks"])

    return epic_json

if __name__ == "__main__":
    import sys
    import io
    
    # Forzar encoding UTF-8 para evitar errores en Windows con emojis
    if sys.stdout.encoding != 'utf-8':
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')
        
    input_file = sys.argv[1] if len(sys.argv) > 1 else "EPIC-EXAMPLE.md"
    output_file = input_file.replace('.md', '.json')
    
    try:
        result_json = parse_epic_md(input_file)
        with open(output_file, 'w', encoding='utf-8') as f:
            json.dump(result_json, f, indent=2, ensure_ascii=False)
        print(f"✅ ¡Éxito! JSON generado correctamente en: {output_file}")
        print(f"   - Milestones extraídos: {len(result_json['milestones'])}")
        print(f"   - Tareas extraídas: {len(result_json['tasks'])}")
    except Exception as e:
        print(f"❌ Error al parsear el archivo MD: {e}")

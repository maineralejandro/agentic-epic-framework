import sys
import os
import json
import io
from rich.console import Console

# Agregar el directorio src/ al path para que los imports funcionen
# independientemente de desde dónde se ejecute el script
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from epic_to_json import parse_epic_md
from audit_backlog import audit_description

# Forzar encoding UTF-8 para evitar errores en Windows con emojis
if sys.stdout.encoding != 'utf-8':
    sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

console = Console()

def compile_epic(md_file_path):
    # Validar que el archivo existe y es .md
    if not os.path.isfile(md_file_path):
        console.print(f"[red]Error: El archivo '{md_file_path}' no existe.[/red]")
        sys.exit(1)
    if not md_file_path.endswith('.md'):
        console.print(f"[red]Error: El archivo debe ser un .md (recibido: '{md_file_path}').[/red]")
        sys.exit(1)

    console.print(f"🚀 [bold cyan]Iniciando Nexus Compiler para:[/bold cyan] {md_file_path}")
    
    # 1. Convertir MD a JSON Base (Pipeline 1)
    console.print("[yellow]1. Extrayendo estructura del archivo Markdown...[/yellow]")
    epic_json = parse_epic_md(md_file_path)
    
    total_tasks = len(epic_json["tasks"])
    console.print(f"   ✅ Se encontraron {total_tasks} tareas y {len(epic_json['milestones'])} milestones.")

    if total_tasks == 0:
        console.print("[red]⚠️  No se encontraron tareas. Verifica que el formato del Markdown coincide con el epic_template.md del Playbook.[/red]")
        sys.exit(1)
    
    # 2. Ejecutar Auditoría (Pipeline 2)
    console.print("\n[yellow]2. Ejecutando Auditoría Antigravity Standard (14 puntos)...[/yellow]")
    total_score = 0
    passed_tasks = 0
    
    for task in epic_json["tasks"]:
        score, findings = audit_description(task["id"], task["description"])
        
        # Inyectar el resultado de la auditoría en la tarea
        task["audit"] = {
            "score": score,
            "status": "PASS" if score >= 90 else "FAIL",
            "findings": findings
        }
        
        total_score += score
        if score >= 90:
            passed_tasks += 1
            
        color = "green" if score >= 90 else ("yellow" if score >= 70 else "red")
        console.print(f"   - {task['id']}: [{color}]{score}%[/] " + (f"({len(findings)} findings)" if findings else ""))
        
    # 3. Enriquecer Metadatos Globales (Pipeline 3)
    console.print("\n[yellow]3. Generando métricas enriquecidas...[/yellow]")
    avg_health = (total_score / total_tasks) if total_tasks > 0 else 0
    
    epic_json["execution_metadata"]["backlog_health"] = f"{avg_health:.1f}%"
    epic_json["execution_metadata"]["audit_summary"] = {
        "passed": passed_tasks,
        "failed": total_tasks - passed_tasks
    }
    
    # 4. Guardar JSON Final
    json_path = md_file_path.replace('.md', '.json')
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(epic_json, f, indent=2, ensure_ascii=False)
        
    console.print(f"\n[bold green]✨ ¡Compilación exitosa! JSON enriquecido guardado en:[/bold green] {json_path}")
    console.print(f"📊 [bold]Backlog Health Global:[/bold] {avg_health:.1f}%")

def main():
    """Entry point para uso como CLI instalado vía pip."""
    if len(sys.argv) < 2:
        console.print("[red]Uso: nexus-compiler <archivo.md>[/red]")
        sys.exit(1)
        
    compile_epic(sys.argv[1])

if __name__ == "__main__":
    main()

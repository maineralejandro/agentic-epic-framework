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


console = Console()

class CompilationError(Exception):
    """Excepción personalizada para errores específicos del Nexus Compiler."""
    pass

def compile_epic(md_file_path):
    """Compila un archivo Markdown a JSON enriquecido con auditoría de Dos Gates.
    
    Gate 1 — Integridad Estructural: Binario PASS/BLOCK por tarea.
    Gate 2 — Calidad de Diseño: Score 0-100 informativo por tarea.
    
    Raises:
        FileNotFoundError: Si el archivo no existe.
        ValueError: Si el archivo no es .md.
        CompilationError: Si el archivo no contiene tareas válidas.
    """
    # Validar que el archivo existe y es .md
    if not os.path.isfile(md_file_path):
        raise FileNotFoundError(f"El archivo '{md_file_path}' no existe.")
        
    if not md_file_path.endswith('.md'):
        raise ValueError(f"El archivo debe ser un .md (recibido: '{md_file_path}').")

    console.print(f"🚀 [bold cyan]Iniciando Nexus Compiler para:[/bold cyan] {md_file_path}")
    
    # 1. Convertir MD a JSON Base (Pipeline 1)
    console.print("[yellow]1. Extrayendo estructura del archivo Markdown...[/yellow]")
    epic_json = parse_epic_md(md_file_path)
    
    total_tasks = len(epic_json["tasks"])
    console.print(f"   ✅ Se encontraron {total_tasks} tareas y {len(epic_json['milestones'])} milestones.")

    if total_tasks == 0:
        raise CompilationError("No se encontraron tareas. Verifica que el formato del Markdown coincide con el epic_template.md.")
    
    # 2. Ejecutar Auditoría de Dos Gates (Pipeline 2)
    console.print("\n[yellow]2. Ejecutando Auditoría Antigravity Standard (Dos Gates)...[/yellow]")
    
    # Agregador de métricas para observabilidad total
    stats = {
        "integrity_pass": 0,
        "integrity_block": 0,
        "quality_total": 0,
        "errors": 0
    }
    
    for task in epic_json["tasks"]:
        try:
            result = audit_description(task["id"], task["description"])
            
            gate1 = result["integrity"]
            gate2 = result["quality"]
            
            task["audit"] = {
                "integrity": "PASS" if gate1["pass"] else "BLOCK",
                "blockers": gate1["blockers"],
                "quality_score": gate2["score"],
                "quality_findings": gate2["findings"]
            }
            
            stats["quality_total"] += gate2["score"]
            if gate1["pass"]:
                stats["integrity_pass"] += 1
            else:
                stats["integrity_block"] += 1
            
            # Formato visual del reporte
            if gate1["pass"]:
                color = "green" if gate2["score"] >= 90 else "yellow"
                icon = "✅"
                blocker_info = ""
            else:
                color = "red"
                icon = "🔴"
                blocker_info = f" — {len(gate1['blockers'])} blocker(s)"
            
            console.print(
                f"   - {task['id']}: [{color}]{icon} Gate 1: {'PASS' if gate1['pass'] else 'BLOCK'}[/] "
                f"| Quality: {gate2['score']}%{blocker_info}"
            )
            
            # Mostrar blockers en detalle si los hay
            if gate1["blockers"]:
                for blocker in gate1["blockers"]:
                    console.print(f"     [red]↳ {blocker}[/red]")
            
        except Exception as e:
            stats["errors"] += 1
            console.print(f"   - {task['id']}: [bold red]FATAL ERROR[/] - {str(e)}")
            task["audit"] = {
                "integrity": "SYSTEM_ERROR",
                "blockers": [str(e)],
                "quality_score": 0,
                "quality_findings": []
            }

    # 3. Enriquecer Metadatos Globales (Pipeline 3)
    console.print("\n[yellow]3. Generando métricas enriquecidas...[/yellow]")
    
    # Cálculos separados: Integridad (binario) vs Calidad (score)
    auditable_tasks = stats["integrity_pass"] + stats["integrity_block"]
    avg_quality = (stats["quality_total"] / auditable_tasks) if auditable_tasks > 0 else 0
    integrity_rate = (stats["integrity_pass"] / total_tasks) * 100 if total_tasks > 0 else 0
    
    # Determinar estado global del compilado
    if stats["errors"] > 0:
        global_status = "INCOMPLETE"
    elif stats["integrity_block"] > 0:
        global_status = "BLOCKED"
    else:
        global_status = "READY"
    
    # Metadatos de alta fidelidad para procesos downstream
    epic_json["execution_metadata"]["audit_model"] = "two-gate-v1"
    epic_json["execution_metadata"]["backlog_health"] = f"{avg_quality:.1f}%"
    epic_json["execution_metadata"]["audit_summary"] = {
        "status": global_status,
        "gate_1_integrity": {
            "pass": stats["integrity_pass"],
            "blocked": stats["integrity_block"],
            "rate": f"{integrity_rate:.1f}%"
        },
        "gate_2_quality": {
            "average_score": f"{avg_quality:.1f}%"
        },
        "system_errors": stats["errors"]
    }
    
    # 4. Guardar JSON Final (safe path handling)
    file_base, _ = os.path.splitext(md_file_path)
    json_path = f"{file_base}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(epic_json, f, indent=2, ensure_ascii=False)
    
    # Reporte final
    if global_status == "READY":
        console.print(f"\n[bold green]✨ Compilación exitosa (READY)[/bold green]")
    elif global_status == "BLOCKED":
        console.print(f"\n[bold red]🚫 Compilación BLOQUEADA — {stats['integrity_block']} tarea(s) no pasan Gate 1[/bold red]")
    else:
        console.print(f"\n[bold yellow]⚠️ Compilación INCOMPLETA — {stats['errors']} error(es) de sistema[/bold yellow]")
    
    console.print(f"📊 [bold]Integridad:[/bold] {integrity_rate:.1f}% | [bold]Calidad Promedio:[/bold] {avg_quality:.1f}%")
    
    return json_path

def main():
    """Entry point para uso como CLI."""
    # Configuración defensiva de encoding para terminales Windows
    if sys.platform == "win32" and hasattr(sys.stdout, 'buffer') and sys.stdout.encoding != 'utf-8':
        import io
        sys.stdout = io.TextIOWrapper(sys.stdout.buffer, encoding='utf-8')

    if len(sys.argv) < 2:
        console.print("[red]Uso: nexus-compiler <archivo.md>[/red]")
        sys.exit(1)
        
    try:
        compile_epic(sys.argv[1])
    except FileNotFoundError as e:
        console.print(f"[red]❌ Error de archivo:[/red] {e}")
        sys.exit(1)
    except ValueError as e:
        console.print(f"[red]❌ Error de validación:[/red] {e}")
        sys.exit(1)
    except CompilationError as e:
        console.print(f"[red]❌ Error de compilación:[/red] {e}")
        sys.exit(1)
    except Exception as e:
        console.print(f"[bold red]❌ Error inesperado:[/bold red] {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()

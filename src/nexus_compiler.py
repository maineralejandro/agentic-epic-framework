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
    """Compila un archivo Markdown a JSON enriquecido con auditoría.
    
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
    
    # 2. Ejecutar Auditoría (Pipeline 2)
    console.print("\n[yellow]2. Ejecutando Auditoría Antigravity Standard (14 puntos)...[/yellow]")
    
    # Agregador de métricas para observabilidad total
    stats = {
        "passed": 0,
        "failed": 0,
        "errors": 0,
        "total_score": 0
    }
    
    for task in epic_json["tasks"]:
        try:
            score, findings = audit_description(task["id"], task["description"])
            
            task["audit"] = {
                "score": score,
                "status": "PASS" if score >= 90 else "FAIL",
                "findings": findings
            }
            
            stats["total_score"] += score
            if score >= 90:
                stats["passed"] += 1
            else:
                stats["failed"] += 1
                
            color = "green" if score >= 90 else ("yellow" if score >= 70 else "red")
            console.print(f"   - {task['id']}: [{color}]{score}%[/] " + (f"({len(findings)} findings)" if findings else ""))
            
        except Exception as e:
            stats["errors"] += 1
            console.print(f"   - {task['id']}: [bold red]FATAL ERROR[/] - {str(e)}")
            task["audit"] = {
                "score": 0,
                "status": "SYSTEM_ERROR",
                "error_detail": str(e)
            }

    # 3. Enriquecer Metadatos Globales (Pipeline 3)
    console.print("\n[yellow]3. Generando métricas enriquecidas...[/yellow]")
    
    # Cálculo Staff: Separamos fidelidad (calidad) de cobertura (integridad)
    auditable_tasks = stats["passed"] + stats["failed"]
    avg_health = (stats["total_score"] / auditable_tasks) if auditable_tasks > 0 else 0
    coverage = (auditable_tasks / total_tasks) * 100 if total_tasks > 0 else 0
    
    # Metadatos de alta fidelidad para procesos downstream
    epic_json["execution_metadata"]["backlog_health"] = f"{avg_health:.1f}%"
    epic_json["execution_metadata"]["audit_summary"] = {
        "status": "COMPLETED" if stats["errors"] == 0 else "INCOMPLETE",
        "metrics": {
            "passed": stats["passed"],
            "failed": stats["failed"],
            "system_errors": stats["errors"],
            "audit_coverage": f"{coverage:.1f}%"
        }
    }
    
    # 4. Guardar JSON Final (safe path handling)
    file_base, _ = os.path.splitext(md_file_path)
    json_path = f"{file_base}.json"
    with open(json_path, 'w', encoding='utf-8') as f:
        json.dump(epic_json, f, indent=2, ensure_ascii=False)
        
    status_color = "green" if stats["errors"] == 0 else "yellow"
    console.print(f"\n[bold {status_color}]✨ Compilación finalizada ({epic_json['execution_metadata']['audit_summary']['status']})[/bold {status_color}]")
    console.print(f"📊 [bold]Backlog Health Global:[/bold] {avg_health:.1f}% | [bold]Cobertura:[/bold] {coverage:.1f}%")
    
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

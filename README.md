# Agentic Epic Framework

**Es un compilador de documentación. Trata el Markdown escrito por humanos como código fuente, lo lintea evaluando reglas de calidad semántica, y lo compila en un JSON enriquecido que los Agentes de IA pueden consumir determinísticamente sin alucinar.**

Un framework de ingeniería de requerimientos para inteligencia artificial que estandariza el ciclo de vida del desarrollo guiado por agentes.

## 🚀 Características Principales

*   **Compilador de Épicas**: Parsea un archivo Markdown con un formato estructurado y extrae metadata estratégica y tareas tácticas.
*   **Linter Semántico**: Audita tus descripciones de tareas contra 14 reglas estrictas de calidad y genera métricas de fidelidad.
*   **Generador JSON Determinista**: Emite un `.json` listo para que agentes autónomos de IA consuman sin necesidad de inferir detalles del proyecto.
*   **IDs Flexibles y Git-Safe**: Acepta cualquier prefijo alfanumérico para épicas (`E-01`, `FEAT-01`, `CORE-03`) y tareas (`E01-T01`, `FEAT01-T03`).

## 🔄 El Flujo de Trabajo (Workflow)

El ciclo de vida completo bajo este framework sigue esta canalización exacta:

1. **Idea:** Nace un requerimiento o funcionalidad.
2. **Playbook:** Se consulta el *Antigravity Standard* (`ENGINEERING_PLAYBOOK.md`) para entender las reglas del juego.
3. **MD:** El usuario le pide a una IA que escriba la épica utilizando el Playbook y el `epic_template.md`.
4. **MD to JSON:** `nexus_compiler.py` extrae las tareas, contexto y arquitectura.
5. **Audit Log:** El compilador ejecuta `audit_backlog.py` para asegurar que las tareas cumplan con los 14 puntos de fidelidad.
6. **JSON:** Se emite el artefacto final enriquecido, 100% determinista y listo para que un agente de IA lo ejecute sin desviaciones.

## 📂 Estructura del Proyecto

```
agentic-epic-framework/
├── README.md
├── requirements.txt
├── pyproject.toml
├── .gitignore
│
├── standard/
│   ├── ENGINEERING_PLAYBOOK.md    # Manifiesto y reglas de oro
│   └── epic_template.md           # Plantilla lista para llenar
│
├── src/
│   ├── nexus_compiler.py          # Orquestador principal
│   ├── epic_to_json.py            # Parser MD → JSON
│   └── audit_backlog.py           # Linter semántico (14 puntos)
│
└── examples/
    ├── EPIC-EXAMPLE.md            # Caso de éxito (demo)
    └── EPIC-EXAMPLE.json          # Output esperado
```

## 📦 Instalación y Uso

### 1. Clonar e instalar dependencias
```bash
git clone https://github.com/maineralejandro/agentic-epic-framework.git
cd agentic-epic-framework
pip install -r requirements.txt
```

### 2. Compilar una épica
```bash
python src/nexus_compiler.py examples/EPIC-EXAMPLE.md
```

### 3. Instalación como CLI global (opcional)
```bash
pip install -e .
nexus-compiler mi-epica.md
```

## 🛠️ Cómo integrarlo en tus proyectos

1.  **Como Submódulo de Git:**
    ```bash
    git submodule add https://github.com/maineralejandro/agentic-epic-framework.git tools/epic-framework
    python tools/epic-framework/src/nexus_compiler.py docs/MI-EPICA.md
    ```

2.  **Como Plantilla (Template Repository):**
    Marca este repositorio como "Template" en GitHub. Al iniciar un proyecto con IA, presiona "Use this template" y tendrás el Playbook y el Compilador pre-instalados.

3.  **Como paquete CLI global:**
    Gracias al `pyproject.toml`, puedes instalar vía `pip install -e .` y ejecutar `nexus-compiler epic.md` desde cualquier ruta.

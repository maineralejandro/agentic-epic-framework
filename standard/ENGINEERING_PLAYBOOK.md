# 🌀 Staff Engineering Playbook: The Antigravity Standard (Nexus V3.0)
**Proyecto**: [Nombre de tu Proyecto Aquí]

## 1. Filosofía: Radical Simplicity & Agentic-First Development
El objetivo de este estándar es garantizar que cada unidad de trabajo (Ticket) sea un **átomo de contexto perfecto** para un desarrollador autónomo. Reducimos la entropía eliminando la ambigüedad y maximizando la densidad semántica útil.

### 1.1 La Arquitectura del Milestone: "State Transition" Mindset
Un Milestone no es una fecha; es una **mutación de la capacidad del sistema**.

- **Definición de Valor**: Cada Milestone debe declarar explícitamente su transición: `Estado A (Limitación) → Estado B (Capacidad)`.
- **Test de Integración de Milestone**: No se considera "Done" por la suma de sus tareas, sino por una validación de "caja negra" que demuestre la nueva capacidad.
- **Vertical Slicing**: Cada Milestone debe tocar todas las capas necesarias (Core, API, DB, UI). Prohibidos los hitos puramente técnicos que no entreguen una capacidad observable.
- **Integration-Last Rule**: Toda Épica que construya múltiples paneles o módulos desconectados DEBE incluir obligatoriamente una Tarea Final (ej. `TASK-XX: Final Layout Integration`). El `<CONTRACT>` de esta tarea final debe listar exclusivamente acciones `[MODIFY]` sobre las vistas principales (ej. `page.tsx`, `App.js`) con la responsabilidad explícita de importar y posicionar los componentes creados en las tareas anteriores.

---

## 2. Anatomía de la Tarea (Los 14 Puntos Obligatorios)
Para optimizar el contexto del agente (LLM), utilizamos **Delimitadores Semánticos** que jerarquizan la información.

### Estructura del Template Maestro

#### `<CONTEXT>` (El Porqué y el Origen)
1. **Título de Identidad**: `# [ID] — [Título]`
2. **Metadatos de Riesgo**: `> Milestone: [ID] — [Nombre] · Risk: [Bajo/Medio/Alto]`
3. **## Objetivo**: Definición clara del valor técnico y funcional.
4. **## Dependencias consumidas**: Tabla `Tarea | Qué aporta`. Explica el componente o conocimiento heredado.

#### `<CONTRACT>` (La Fuente de la Verdad)
5. **## Archivos**: Tabla `Archivo | Acción | Responsabilidad`. 
   - Acciones: `CREATE`, `MODIFY`, `REFACTOR`.
   - *Regla*: El agente autónomo tiene prohibido tocar archivos no listados aquí.
6. **## Tipos esperados**: Bloques de código con `dataclasses`, `enums` o `interfaces`.
   - *Regla de Oro*: Si hay un `CREATE`, debe haber un bloque de código aquí para evitar alucinaciones de nombres.

#### `<CONSTRAINTS>` (Límites y Decisiones)
7. **## Decisiones técnicas**:
   - **### Datos**: Estrategia de persistencia y flujo.
   - **### Acceso / Seguridad**: Aislamiento y permisos.
   - **### UI / Contrato de componentes**: Interfaz expuesta.
8. **## Fuera de scope**: El "Muro de Contención". Define qué **no** se hará para evitar el scope creep.
9. **## Estados UI requeridos**: Lista de estados (Loading, Empty, Error, Success).

#### `<VALIDATION>` (El Criterio de Done)
10. **## Tests**: Tabla `Archivo | Tipo | Casos clave`.
    - *Regla*: Si el archivo no existe, debe estar en la tabla de Archivos como `CREATE` (Promesa de Creación).
11. **## Criterio de salida**: Tabla `Escenario | Resultado esperado`. Validación final determinista.

---

## 3. Estándares Técnicos (Definidos por el Proyecto)

### 3.1 [Ej. Arquitectura de Base de Datos]
[Define aquí si usas PostgreSQL, MongoDB, SQLite y las reglas estrictas de esquemas lógicos o colecciones]

### 3.2 [Ej. Protocolos de Comunicación]
[Define si usas REST, GraphQL, SSE, WebSockets y las reglas de implementación]

### 3.3 [Ej. Estrategia de Migraciones/Infraestructura]
[Define cómo el agente debe manejar los cambios destructivos y constructivos en la infraestructura de datos o código]

### 3.5 Descentralización de Repositorios (Dynamic Repository Protocol)
Para habilitar el soporte multi-proyecto, el sistema debe ser agnóstico al repositorio global:
1. **Source of Truth**: El repositorio objetivo se define a nivel de **Épica**. El archivo Markdown debe incluir el campo `Repositorio` en su tabla de resumen inicial.
2. **Inyección Dinámica**: El parser `epic_to_json.py` extrae este valor y lo inyecta en cada tarea para su persistencia en la base de datos.
3. **Aislamiento Semántico**: Cada repositorio genera su propia colección en ChromaDB basada en el slug del repo.

---

## 4. Protocolos de Gobernanza

### 4.1 Auditoría de Dos Gates (Zero-Tolerance Mode)
El compilador (`nexus_compiler.py`) evalúa cada tarea con un modelo de **Dos Gates independientes**:

#### Gate 1 — Integridad Estructural (Binario: PASS / BLOCK)
Valida que la tarea es **ejecutable sin ambigüedad** por un agente autónomo. **Cualquier fallo bloquea la compilación de la tarea.**

| Regla | Qué valida | Fallo = |
|---|---|---|
| Headers obligatorios | Las 14 secciones del template deben existir | BLOCK |
| Anti-Filler | Prohibido: `N/A`, `TBD`, `Por definir`, `Completar` | BLOCK |
| Contrato CREATE→Tipos | Si hay archivos `CREATE`, debe haber código en `## Tipos esperados` | BLOCK |
| Tests no vacíos | `## Tests` debe tener ≥ 1 fila con casos clave descritos | BLOCK |
| Tests sin fantasmas | Archivos en `## Tests` deben estar declarados en `## Archivos` | BLOCK |

**Regla crítica para la IA generadora**: Si una sección no aplica a la tarea, NUNCA usar `N/A`. En su lugar, explicar brevemente por qué no aplica. Ejemplo: en vez de `N/A`, escribir `"No hay componentes visuales — tarea de migración de base de datos."`

#### Gate 2 — Calidad de Diseño (Score 0-100, informativo)
Evalúa la **robustez del diseño**. Un score bajo no bloquea, pero genera warnings visibles en el JSON.

| Métrica | Qué evalúa |
|---|---|
| Granularidad del Objetivo | ≥ 30 palabras en `## Objetivo` |
| Orfandad de UI | Visual creado sin `MODIFY` en layout/router |
| Cobertura de tests | Ratio de archivos con test asociado (informativo) |

El autor de la épica decide qué archivos necesitan tests. El framework solo asegura que **la pregunta no fue ignorada**.

### 4.2 Protocolo de Rescate (Ghost Task Protection)
Si se identifica una tarea marcada como `done` pero cuya infraestructura física no existe o está degradada (Fallo de Fidelidad), el sistema debe:
1. Pausar el Milestone actual.
2. Generar una **Épica de Rescate** para reconstruir los cimientos.
3. Re-mapear las dependencias de las tareas de producto hacia los nuevos habilitadores.

### 4.3 Extensión de Contrato
Si durante la ejecución se descubre una dependencia imprevista:
1. Se emite una **Solicitud de Extensión**.
2. Se pausa la sesión (preservando estado).
3. Tras la aprobación humana, se muta el `<CONTRACT>` y se reanuda.

---

## 5. Firma de Diseño
El flujo de compilación de épicas (vía `nexus_compiler.py`) requiere siempre una **Firma de Aprobación Humana**. La IA propone o estructura el diseño; el humano lo valida y "firma" (hace commit/aprueba) antes de que pase a ejecución activa.

Una épica solo puede pasar a estado `TODO` si:
1. **Gate 1 = PASS** en todas las tareas (status global: `READY`).
2. **Gate 2** ha sido revisado por el humano (el score de calidad es informativo pero debe ser consciente).
3. La **Firma de Aprobación** al final del documento está completa.

# 🌀 E-XX — [Nombre de la Épica]
**[Tu Estándar] · [Nombre del Proyecto]**

---

## Resumen de la Épica

| Campo | Valor |
|---|---|
| ID | E-XX |
| Nombre | [Nombre descriptivo] |
| Estado inicial | [Capacidad actual del sistema antes de esta épica] |
| Estado final | [Capacidad deseada después de completarla] |
| Stack | [Ej. Next.js 14 · TypeScript · Supabase] |
| Total milestones | [N] |
| Total tareas | [N] |

---

## Milestones

### M1-01 — [Nombre del Milestone]
**Transición**: `[Estado A (Limitación) → Estado B (Capacidad)]`

**Test de integración de milestone**: [Descripción determinista de cómo validar que este milestone está completo]

---

*(Repetir para cada milestone)*

---

## Tasks

---

# EXX-T01 — [Título descriptivo y determinista]
> Milestone: M1-01 — [Nombre del Milestone] · Risk: [Bajo/Medio/Alto]

## Objetivo
[Definición clara del valor técnico y funcional de esta tarea. Mínimo 30 palabras. Explica el POR QUÉ, el QUÉ y el impacto si no se hace.]

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| [DEP-ID] | [Componente o conocimiento heredado] |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `ruta/al/archivo.py` | CREATE | [Qué hace este archivo] |
| `ruta/al/otro.py` | MODIFY | [Qué se modifica y por qué] |

## Tipos esperados
```python
# Definir dataclasses, enums o interfaces aquí
# Obligatorio si hay al menos un CREATE en la tabla de Archivos
```

## Decisiones técnicas

### Datos
[Estrategia de persistencia y flujo de datos]

### Acceso / Seguridad
[Aislamiento, permisos, reglas de acceso]

### UI / Contrato de componentes
[Interfaz expuesta, props, eventos]

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `tests/test_ejemplo.py` | Unit | [Descripción de los casos de prueba] |

## Estados UI requeridos
- Loading
- Empty
- Error
- Success

## Fuera de scope
- [Punto explícitamente fuera de alcance para esta tarea]

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| [Escenario de validación] | [Resultado determinista esperado] |

---

*(Repetir la estructura de tareas según sea necesario)*
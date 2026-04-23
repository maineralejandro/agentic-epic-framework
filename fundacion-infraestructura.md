# 🌀 E-01 — Fundación e Infraestructura
**Nexus Antigravity Standard V3.0 · POS SaaS**

---

## Resumen de la Épica

| Campo | Valor |
|---|---|
| ID | E-01 |
| Nombre | Fundación e Infraestructura |
| Estado inicial | Repositorio vacío, sin base de datos, sin pipeline |
| Estado final | SaaS multi-tenant con RLS activo, capa de acceso tipada y CI/CD operativo |
| Stack | Next.js 14 · TypeScript · Supabase (PostgreSQL 16) · Vercel · GitHub Actions |
| Total milestones | 4 |
| Total tareas | 17 |

---

## Milestones

### M1-01 — Entorno base operativo
**Transición**: `Sin proyecto → Repositorio Next.js 14 con TypeScript, Tailwind, estructura de carpetas, tooling de calidad y entorno local conectado a Supabase`

**Test de integración de milestone**: `npm run dev` levanta en puerto 3000 sin errores. `npm run lint` y `npm run type-check` pasan en verde. Variable `NEXT_PUBLIC_SUPABASE_URL` resuelve y `supabase.auth.getSession()` no lanza error de conexión.

---

### M1-02 — Base de datos multi-tenant con RLS activo
**Transición**: `Sin esquema de datos → PostgreSQL con todas las tablas del dominio de negocio, RLS habilitado y aislamiento físico entre organizations garantizado a nivel de base de datos`

**Test de integración de milestone**: Crear organizations A y B con sus respectivos usuarios. Autenticar como usuario de Org A y ejecutar `SELECT * FROM products` — devuelve únicamente productos de Org A. Autenticar como usuario de Org B — devuelve únicamente productos de Org B. Intento de INSERT sin `organization_id` válido devuelve error de política RLS.

---

### M1-03 — Capa de acceso tipada operativa
**Transición**: `Sin capa de acceso → Cliente Supabase server-side y client-side tipados con tipos generados, middleware de Next.js que resuelve tenant y rol en cada request autenticado`

**Test de integración de milestone**: Request GET a ruta protegida sin JWT → redirect a `/login`. Request con JWT válido de Org A → `organizationId` resuelto en headers. Request con JWT válido intentando query cross-tenant → bloqueado por RLS antes de llegar a la capa de aplicación.

---

### M1-04 — Pipeline CI/CD operativo
**Transición**: `Sin pipeline → Cada push dispara lint + typecheck + tests unitarios; merge a main despliega automáticamente a Vercel con migraciones de Supabase aplicadas en orden transaccional`

**Test de integración de milestone**: Push con error de TypeScript → pipeline falla y bloquea merge. Push limpio → pipeline verde y deploy completado en staging en menos de 5 minutos. Migración nueva en `/supabase/migrations/` → aplicada automáticamente en staging tras el deploy.

---

## Tasks

---

# E01-T01 — Inicializar repositorio Next.js 14 con estructura de carpetas
> Milestone: M1-01 — Entorno base operativo · Risk: Bajo

## Objetivo
Crear el repositorio del proyecto inicializando Next.js 14 con App Router, TypeScript strict mode, Tailwind CSS y la estructura de carpetas que respetará toda la épica y las posteriores. Esta tarea establece las convenciones de rutas, nomenclatura de módulos y separación de capas (app, components, lib, types, supabase) que serán el contrato físico del proyecto. Sin esta base, ninguna tarea posterior tiene dónde aterrizar. La estructura de Route Groups de Next.js define los tres contextos principales: autenticación pública, dashboard de tenant y panel del founder.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| — | Primera tarea de la épica, sin dependencias previas |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `package.json` | CREATE | Dependencias base: next@14, react, typescript, tailwindcss, @supabase/supabase-js, @supabase/ssr |
| `tsconfig.json` | CREATE | TypeScript strict mode, path aliases (@/components, @/lib, @/types) |
| `tailwind.config.ts` | CREATE | Configuración base de Tailwind con content paths correctos |
| `next.config.ts` | CREATE | Configuración Next.js 14: App Router habilitado, variables de entorno públicas listadas |
| `app/layout.tsx` | CREATE | Root layout con fuente Inter, html y body base, sin lógica de negocio |
| `app/page.tsx` | CREATE | Página raíz temporal que hace redirect a /dashboard o /login según sesión |
| `app/(auth)/layout.tsx` | CREATE | Layout del grupo de rutas de autenticación (login, register) |
| `app/(dashboard)/layout.tsx` | CREATE | Layout del grupo de rutas del tenant (POS, inventario, reportes) |
| `app/(founder)/layout.tsx` | CREATE | Layout del grupo de rutas del founder panel |
| `lib/utils.ts` | CREATE | Utilidad `cn()` para merge de clases Tailwind sin conflictos |
| `types/index.ts` | CREATE | Re-exports de tipos globales del dominio |
| `.env.local.example` | CREATE | Plantilla documentada de todas las variables de entorno requeridas |
| `.gitignore` | CREATE | Ignorar .env.local, .next, node_modules, supabase/.branches |
| `__tests__/setup.test.ts` | CREATE | Test unitario de configuración base y path aliases |

## Tipos esperados
```typescript
// types/index.ts — Tipos globales base del dominio
export type UserRole = 'founder' | 'business_owner' | 'cashier'

export type PlanTier = 'free' | 'basic' | 'pro' | 'business'

export type BusinessTemplate =
  | 'food_to_go'
  | 'minimarket'
  | 'bakery'
  | 'ice_cream_cafe'
  | 'bazaar'
  | 'generic'

// Respuesta estándar de todas las APIs internas
export type ApiResponse<T> = {
  data: T | null
  error: string | null
}
```

## Decisiones técnicas

### Datos
No hay persistencia en esta tarea. La estructura de carpetas sigue el patrón App Router de Next.js con Route Groups: `(auth)` para rutas públicas, `(dashboard)` para el panel del tenant y `(founder)` para el panel del SaaS owner. Esta separación permite layouts, middlewares y políticas de acceso distintas por contexto sin conflicto de rutas.

### Acceso / Seguridad
No hay lógica de seguridad en esta tarea. Se establece la convención de que ningún secreto vivirá en el código — todo en variables de entorno. El `.env.local.example` documenta las variables requeridas con descripción pero sin valores reales.

### UI / Contrato de componentes
No se crean componentes visuales. Los layouts son wrappers vacíos que serán poblados en épicas posteriores. El root layout provee únicamente fuente, etiquetas html/body y el `suppressHydrationWarning` necesario para temas de color.

## Fuera de scope
- Instalación de librerías de componentes UI (se hará en E-02)
- Configuración del cliente Supabase (E01-T02)
- Lógica de autenticación o middleware (E01-T15)
- Páginas reales de cualquier módulo funcional

## Estados UI requeridos
No aplica — tarea de scaffolding sin componentes visuales con estado.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `__tests__/setup.test.ts` | Unit | Path alias "@/lib/utils" resuelve correctamente; "cn()" merges clases sin duplicados; build de producción completa sin errores |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| `npm run dev` | Levanta en localhost:3000 sin errores de compilación |
| `npm run type-check` | 0 errores TypeScript |
| `npm run lint` | 0 warnings ni errores ESLint |
| Navegar a `/` | Renderiza sin error (página temporal de redirect) |
| Import `@/lib/utils` desde cualquier archivo | Resuelve correctamente gracias al path alias |

---

# E01-T02 — Configurar Supabase CLI, variables de entorno y clientes base
> Milestone: M1-01 — Entorno base operativo · Risk: Medio

## Objetivo
Inicializar Supabase CLI en el proyecto, configurar la instancia local de desarrollo con Docker, establecer todas las variables de entorno requeridas y crear los tres clientes base de Supabase usando `@supabase/ssr`: cliente server-side (para Server Components y Route Handlers via cookies), cliente client-side (para Client Components con interactividad) y cliente admin con service_role (solo para operaciones del Founder Panel). Esta tarea es el puente entre Next.js y la base de datos — ninguna migración ni consulta posterior es posible sin ella.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T01 | Estructura de carpetas, `package.json` con `@supabase/supabase-js` y `@supabase/ssr` instalados |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/config.toml` | CREATE | Configuración del proyecto Supabase local: puertos, auth settings, storage |
| `supabase/.gitignore` | CREATE | Ignorar `.branches`, `functions/.env` y archivos generados localmente |
| `lib/supabase/server.ts` | CREATE | Cliente server-side con cookie store (Server Components y Route Handlers) |
| `lib/supabase/client.ts` | CREATE | Cliente client-side para Client Components con estado reactivo |
| `lib/supabase/admin.ts` | CREATE | Cliente con service_role key — bypasea RLS, solo para operaciones founder |
| `lib/supabase/middleware.ts` | CREATE | Helper para refrescar sesión en el middleware de Next.js sin romper cookies |
| `.env.local.example` | MODIFY | Agregar variables: NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_ANON_KEY, SUPABASE_SERVICE_ROLE_KEY |
| `__tests__/lib/supabase.test.ts` | CREATE | Test de inicialización de clientes Supabase (server, client, admin) |

## Tipos esperados
```typescript
// lib/supabase/server.ts
import { createServerClient } from '@supabase/ssr'
import { cookies } from 'next/headers'
import type { Database } from '@/types/supabase' // Generado en E01-T14

export function createClient() {
  const cookieStore = cookies()
  return createServerClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.NEXT_PUBLIC_SUPABASE_ANON_KEY!,
    {
      cookies: {
        get: (name) => cookieStore.get(name)?.value,
        set: (name, value, options) => cookieStore.set({ name, value, ...options }),
        remove: (name, options) => cookieStore.set({ name, value: '', ...options }),
      },
    }
  )
}

// lib/supabase/admin.ts
import { createClient } from '@supabase/supabase-js'
import type { Database } from '@/types/supabase'

// ⚠️ ADVERTENCIA: Este cliente bypasea RLS completamente.
// Solo usar en operaciones del Founder Panel desde server-side.
// NUNCA importar en Client Components ni exponer al browser.
export function createAdminClient() {
  return createClient<Database>(
    process.env.NEXT_PUBLIC_SUPABASE_URL!,
    process.env.SUPABASE_SERVICE_ROLE_KEY!
  )
}
```

## Decisiones técnicas

### Datos
Los tres clientes tienen niveles de privilegio distintos y usos exclusivos. `server.ts` usa la anon key con RLS activo — es el cliente estándar para todas las operaciones de negocio del sistema. `admin.ts` usa service_role que bypasea RLS — solo para el Founder Panel (suspender tenants, token tracking, impersonation). `client.ts` es para Client Components que necesitan suscripciones realtime o interactividad sin server round-trip.

### Acceso / Seguridad
`SUPABASE_SERVICE_ROLE_KEY` no puede tener prefijo `NEXT_PUBLIC_` — cualquier variable con ese prefijo se expone al browser. El `admin.ts` lleva un comentario de advertencia explícito; su importación en un Client Component debe ser detectada como error de lint (regla personalizada a agregar en E01-T03). Los secrets nunca se loguean — usar variables de entorno directamente sin interpolación en strings de log.

### UI / Contrato de componentes
No hay componentes visuales. Este módulo es infraestructura pura de acceso a datos consumida por todas las épicas posteriores.

## Fuera de scope
- Tipos generados de Supabase (se generan en E01-T14 una vez que existan las migraciones)
- Lógica de autenticación completa (E01-T15)
- Edge Functions (E-06)
- Queries de negocio (épicas E-03 a E-09)

## Estados UI requeridos
No aplica — módulo de infraestructura sin componentes visuales.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `__tests__/lib/supabase.test.ts` | Unit | "createClient()" retorna instancia válida con URL correcta; "createAdminClient()" retorna instancia con service role; variables de entorno faltantes lanzan error descriptivo, no "undefined" silencioso |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| `supabase start` | Instancia local levanta con Postgres, Studio y Auth en puertos configurados |
| `supabase status` | Muestra URL local y keys activas sin error |
| Import de `createClient` en Server Component | Compila y conecta sin error de runtime |
| Import de `createAdminClient` en archivo client-side | TypeScript arroja error por regla de lint |
| Variable de entorno ausente | Error descriptivo en startup, no `undefined` silencioso |

---

# E01-T03 — Configurar tooling de calidad (ESLint, Prettier, Husky, commitlint)
> Milestone: M1-01 — Entorno base operativo · Risk: Bajo

## Objetivo
Establecer y forzar los estándares de calidad de código que todos los agentes de IA respetarán al generar código a lo largo del proyecto. Configura ESLint con reglas para Next.js y TypeScript strict, Prettier para formato determinista, Husky para pre-commit hooks que bloqueen código que no pase los checks, y commitlint para convención de commits semánticos con scopes del dominio. Sin esta tarea, múltiples agentes generando código en paralelo producirán un codebase inconsistente e inauditable.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T01 | `package.json` base, estructura del proyecto existente |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `.eslintrc.json` | CREATE | Reglas: next/core-web-vitals, @typescript-eslint/recommended, no-console en producción, prohibir import de admin.ts en client components |
| `.prettierrc` | CREATE | Formato: semicolons true, singleQuote true, trailingComma 'es5', printWidth 100, tabWidth 2 |
| `.prettierignore` | CREATE | Ignorar .next, node_modules, supabase/migrations (SQL autogenerado), types/supabase.ts |
| `.husky/pre-commit` | CREATE | Hook que ejecuta lint-staged sobre archivos staged antes de cada commit |
| `.husky/commit-msg` | CREATE | Hook que valida formato del mensaje de commit con commitlint |
| `lint-staged.config.js` | CREATE | Ejecutar prettier --write + eslint --fix solo sobre archivos staged (no el proyecto entero) |
| `commitlint.config.js` | CREATE | Convención con types y scopes del dominio del producto |
| `package.json` | MODIFY | Agregar scripts: `lint`, `format`, `format:check`, `type-check`, `prepare` (husky install) |
| `__tests__/tooling/lint.test.ts` | CREATE | Test de validación de reglas de lint personalizadas y hooks |

## Tipos esperados
```typescript
// commitlint.config.js
module.exports = {
  extends: ['@commitlint/config-conventional'],
  rules: {
    'type-enum': [2, 'always', [
      'feat',      // Nueva funcionalidad
      'fix',       // Corrección de bug
      'chore',     // Mantenimiento, deps
      'refactor',  // Refactoring sin cambio funcional
      'test',      // Agregar o corregir tests
      'docs',      // Documentación
      'migration', // Migraciones de base de datos
      'perf'       // Mejora de performance
    ]],
    'scope-enum': [2, 'always', [
      'auth', 'pos', 'inventory', 'agents',
      'founder', 'owner', 'infra', 'db',
      'cashier', 'notifications', 'onboarding'
    ]]
  }
}
```

## Decisiones técnicas

### Datos
No hay persistencia. Los archivos de configuración son estáticos.

### Acceso / Seguridad
El pre-commit hook incluye una regla ESLint personalizada que detecta `import { createAdminClient }` en archivos bajo `app/` que no sean Route Handlers (`route.ts`). Esto previene que el cliente admin sea accidentalmente expuesto al browser. También bloquea `console.log` en archivos fuera de `__tests__/` y `scripts/`.

### UI / Contrato de componentes
No hay componentes visuales. Las reglas de ESLint incluirán reglas de accesibilidad JSX (`jsx-a11y`) que entrarán en efecto cuando se creen componentes en E-02.

## Fuera de scope
- Configuración de testing framework Vitest (E01-T16)
- Reglas ESLint específicas de componentes React de UI (E-02)
- SonarQube o herramientas de análisis estático avanzado

## Estados UI requeridos
No aplica — tarea de configuración de tooling sin componentes visuales.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `__tests__/tooling/lint.test.ts` | Integration | Archivo con "console.log" falla lint; commit con mensaje sin convención falla commitlint; commit con "fix(pos): descripción" pasa; import de "createAdminClient" en archivo de página falla lint |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| `npm run lint` sobre codebase limpio | 0 errores, 0 warnings |
| `npm run format:check` | 0 archivos con diferencias de formato |
| Commit con mensaje `"arreglar bug"` | Hook commitlint rechaza con mensaje de error de convención |
| Commit con mensaje `"fix(pos): corregir cálculo de total"` | Hook acepta, commit creado |
| Archivo `.tsx` con `console.log` en staged | Pre-commit bloquea y muestra el archivo y línea violadores |

---

# E01-T04 — Migración 001: tabla organizations y enums globales
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Alto

## Objetivo
Crear la migración fundacional del sistema multi-tenant. La tabla `organizations` es el anchor de toda la arquitectura RLS — cada registro de cualquier entidad del sistema pertenecerá a una organización. Esta migración también define todos los enums globales de PostgreSQL que serán referenciados por tablas en migraciones posteriores, garantizando integridad de tipos a nivel de base de datos y evitando strings mágicos en el código de aplicación. Un error en esta migración requiere `DROP CASCADE` en producción — de ahí el riesgo Alto.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T02 | Supabase CLI inicializado, runner de migraciones disponible con `supabase db push` |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000000_create_organizations_and_enums.sql` | CREATE | Enums globales + tabla organizations con constraints y triggers de updated_at |
| `supabase/seed.sql` | CREATE | Seed de desarrollo: 2 organizations de prueba (food_to_go y minimarket) con datos mínimos |
| `supabase/tests/migrations/001_organizations.test.sql` | CREATE | Test de integración: validación de esquema, constraints y triggers de organizations |

## Tipos esperados
```sql
-- =============================================
-- ENUMS GLOBALES (definidos aquí, referenciados en todo el sistema)
-- =============================================
CREATE TYPE plan_tier AS ENUM ('free', 'basic', 'pro', 'business');

CREATE TYPE business_template AS ENUM (
  'food_to_go',
  'minimarket',
  'bakery',
  'ice_cream_cafe',
  'bazaar',
  'generic'
);

CREATE TYPE org_status AS ENUM ('trial', 'active', 'suspended', 'cancelled');

CREATE TYPE user_role AS ENUM ('business_owner', 'cashier');

-- =============================================
-- TABLA ORGANIZATIONS
-- =============================================
CREATE TABLE organizations (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  name            TEXT NOT NULL,
  slug            TEXT NOT NULL UNIQUE CHECK (slug ~ '^[a-z0-9-]+$'),
  template        business_template NOT NULL DEFAULT 'generic',
  plan            plan_tier NOT NULL DEFAULT 'free',
  status          org_status NOT NULL DEFAULT 'trial',
  trial_ends_at   TIMESTAMPTZ DEFAULT (now() + INTERVAL '7 days'),
  logo_url        TEXT,
  primary_color   TEXT DEFAULT '#000000' CHECK (primary_color ~ '^#[0-9A-Fa-f]{6}$'),
  owner_id        UUID NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Trigger para mantener updated_at sincronizado
CREATE OR REPLACE FUNCTION update_updated_at_column()
RETURNS TRIGGER AS $$
BEGIN
  NEW.updated_at = now();
  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER organizations_updated_at
  BEFORE UPDATE ON organizations
  FOR EACH ROW EXECUTE FUNCTION update_updated_at_column();
```

## Decisiones técnicas

### Datos
El `slug` es UNIQUE y será la base del white-labeling v1 (`miproducto.com/[slug]`). El regex `^[a-z0-9-]+$` garantiza URLs válidas sin encoding. El campo `owner_id` referencia `auth.users` directamente (no nuestra tabla `profiles` que viene en E01-T08) para que la FK sea manejada por el sistema de auth nativo de Supabase. El `primary_color` acepta solo hex válido para prevenir XSS vía CSS injection en el white-labeling.

### Acceso / Seguridad
RLS se habilitará en E01-T12. Esta migración solo crea la estructura. La tabla `organizations` tendrá política especial: un usuario autenticado puede leer su propia organization, pero solo el Founder (via service_role) puede crear, suspender o cancelar organizations. El `owner_id` con `ON DELETE RESTRICT` previene borrar un usuario que sea dueño de una organización activa.

### UI / Contrato de componentes
No hay componentes visuales. Los tipos TypeScript correspondientes se generarán automáticamente en E01-T14 via `supabase gen types typescript`.

## Fuera de scope
- Tabla `profiles` de usuarios (E01-T08)
- Políticas RLS (E01-T12)
- Validación de slug duplicado a nivel de aplicación (E-02)
- Lógica de billing y trial management (E-09)
- Soporte de subdominio por tenant (v2)

## Estados UI requeridos
No aplica — migración de base de datos sin componentes visuales.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/migrations/001_organizations.test.sql` | Integration (pgTAP) | INSERT con slug válido crea registro; slug con mayúsculas viola CHECK; slug duplicado viola UNIQUE; primary_color inválido viola CHECK; owner_id inexistente en auth.users viola FK; UPDATE actualiza updated_at automáticamente |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| `supabase db reset` | Migración aplica sin errores, enums creados |
| INSERT con slug `"Mi Tienda"` (tiene mayúsculas y espacio) | Viola CHECK, error descriptivo |
| INSERT con slug `"mi-tienda"` | Éxito, UUID generado |
| INSERT duplicando slug | Error UNIQUE constraint |
| UPDATE de name | `updated_at` se actualiza automáticamente via trigger |

---

# E01-T05 — Migración 002: tablas de catálogo
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Alto

## Objetivo
Crear las tablas que modelan el catálogo completo de un negocio: categorías, ingredientes con su stock, productos, la relación producto→ingredientes con cantidades (recetas), y modificadores con sus opciones. Esta es la migración más compleja del dominio porque introduce la separación arquitectural entre producto (lo que se vende y tiene precio) e ingrediente (lo que tiene stock físico y se descuenta). Un producto puede no tener receta (ítem simple) o tener varios ingredientes (plato elaborado). Toda la lógica del POS depende de este esquema.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T04 | Tabla `organizations` disponible para FKs; enums `plan_tier`, `business_template` definidos |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000100_create_catalog_tables.sql` | CREATE | Tablas: categories, ingredients, products, recipe_ingredients, modifiers; enums modifier_type y unit_type |
| `supabase/tests/migrations/002_catalog.test.sql` | CREATE | Test de integración: validación de integridad referencial y lógica de negocio del catálogo |

## Tipos esperados
```sql
CREATE TYPE modifier_type AS ENUM ('add', 'change', 'remove');
CREATE TYPE unit_type AS ENUM (
  'unit', 'gram', 'kilogram', 'liter', 'milliliter', 'portion'
);

CREATE TABLE categories (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  icon            TEXT,
  sort_order      INTEGER NOT NULL DEFAULT 0,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE ingredients (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  unit            unit_type NOT NULL DEFAULT 'unit',
  stock_quantity  NUMERIC(10,3) NOT NULL DEFAULT 0 CHECK (stock_quantity >= 0),
  critical_stock  NUMERIC(10,3) NOT NULL DEFAULT 0 CHECK (critical_stock >= 0),
  cost_per_unit   NUMERIC(10,2),
  supplier_id     UUID, -- FK agregada en E01-T08 tras crear suppliers
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE products (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  category_id     UUID REFERENCES categories(id) ON DELETE SET NULL,
  name            TEXT NOT NULL,
  description     TEXT,
  price           NUMERIC(10,2) NOT NULL CHECK (price >= 0),
  is_active       BOOLEAN NOT NULL DEFAULT true,
  image_url       TEXT,
  has_recipe      BOOLEAN NOT NULL DEFAULT false,
  sort_order      INTEGER NOT NULL DEFAULT 0,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE recipe_ingredients (
  id             UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  product_id     UUID NOT NULL REFERENCES products(id) ON DELETE CASCADE,
  ingredient_id  UUID NOT NULL REFERENCES ingredients(id) ON DELETE RESTRICT,
  quantity       NUMERIC(10,3) NOT NULL CHECK (quantity > 0),
  UNIQUE(product_id, ingredient_id)
);

CREATE TABLE modifiers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  type            modifier_type NOT NULL,
  price_delta     NUMERIC(10,2) NOT NULL DEFAULT 0,
  ingredient_id   UUID REFERENCES ingredients(id) ON DELETE SET NULL,
  ingredient_qty  NUMERIC(10,3) CHECK (ingredient_qty > 0),
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);
```

## Decisiones técnicas

### Datos
`ingredients.stock_quantity` es el campo canónico de stock — se actualiza via trigger en E01-T07 cada vez que hay un movimiento de inventario. Los `products` sin receta (`has_recipe=false`) no requieren `recipe_ingredients` — funcionan como ítems simples para negocios de catálogo básico. El `price_delta` de modifiers puede ser positivo (agrega costo), negativo (descuento al ítem) o cero (cambio sin impacto en precio, ej: "sin sal"). La FK `recipe_ingredients.ingredient_id` es `ON DELETE RESTRICT` para prevenir eliminar ingredientes en uso activo.

### Acceso / Seguridad
Todas las tablas llevan `organization_id` para el aislamiento RLS en E01-T12. Los productos de una organización no pueden referenciar categorías de otra (la FK de `category_id` a `categories` naturalmente previene esto porque RLS aislará las categorías visibles).

### UI / Contrato de componentes
No hay componentes visuales. El esquema es consumido por el módulo de Inventario (E-04) y el POS (E-03).

## Fuera de scope
- Stock por variante de talla/color (v2 — zapatería/ropa)
- Precios diferenciados por sucursal
- Combos y promociones (v2)
- Imágenes: solo URL; el bucket de Supabase Storage se configura en E-02

## Estados UI requeridos
No aplica — migración de base de datos.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/migrations/002_catalog.test.sql` | Integration (pgTAP) | Product con price negativo viola CHECK; recipe_ingredient con quantity=0 viola CHECK; ingrediente en uso activo no puede eliminarse (RESTRICT); modifier tipo "add" sin ingredient_id es válido; modifier con ingredient_id y qty=NULL viola lógica (CHECK); UNIQUE en recipe_ingredients por par product+ingredient |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| `supabase db reset` | Todas las tablas del catálogo creadas sin errores |
| Crear producto sin receta (`has_recipe=false`) | Éxito sin necesidad de recipe_ingredients |
| Intentar eliminar ingrediente referenciado en receta activa | Error RESTRICT con mensaje descriptivo |
| Crear modifier tipo 'change' sin ingredient_id | Éxito (cambio cosmético sin descuento de stock) |

---

# E01-T06 — Migración 003: tablas de ventas
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Alto

## Objetivo
Crear el esquema de ventas que registra cada transacción del POS: la cabecera (`sales`), cada ítem vendido con precio desnormalizado al momento de la venta (`sale_items`), y los modificadores aplicados (`sale_item_modifiers`). El precio y nombre se desnormalizan deliberadamente para preservar el valor histórico con independencia de cambios futuros en el catálogo. Esta es la tabla de mayor volumen del sistema y la fuente principal de eventos para los agentes.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T04 | Tabla `organizations` |
| E01-T05 | Tablas `products` y `modifiers` para FKs opcionales |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000200_create_sales_tables.sql` | CREATE | Tablas: sales, sale_items, sale_item_modifiers; enums payment_method, sale_status |
| `supabase/tests/migrations/003_sales.test.sql` | CREATE | Test de integración: validación de transacciones de venta y desnormalización de datos |

## Tipos esperados
```sql
CREATE TYPE payment_method AS ENUM ('cash', 'transfer');
CREATE TYPE sale_status AS ENUM ('completed', 'cancelled', 'refunded');

CREATE TABLE sales (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  cash_session_id UUID,           -- FK a cash_sessions — se agrega en E01-T09
  seller_id       UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  status          sale_status NOT NULL DEFAULT 'completed',
  payment_method  payment_method NOT NULL DEFAULT 'cash',
  subtotal        NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0),
  total           NUMERIC(10,2) NOT NULL CHECK (total >= 0),
  notes           TEXT,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
  -- No tiene updated_at: las ventas son inmutables. Solo cambia status.
);

CREATE TABLE sale_items (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sale_id         UUID NOT NULL REFERENCES sales(id) ON DELETE CASCADE,
  product_id      UUID REFERENCES products(id) ON DELETE SET NULL,
  product_name    TEXT NOT NULL,  -- DESNORMALIZADO: nombre al momento de la venta
  unit_price      NUMERIC(10,2) NOT NULL CHECK (unit_price >= 0),
  quantity        INTEGER NOT NULL CHECK (quantity > 0),
  subtotal        NUMERIC(10,2) NOT NULL CHECK (subtotal >= 0),
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE sale_item_modifiers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  sale_item_id    UUID NOT NULL REFERENCES sale_items(id) ON DELETE CASCADE,
  modifier_id     UUID REFERENCES modifiers(id) ON DELETE SET NULL,
  modifier_name   TEXT NOT NULL,  -- DESNORMALIZADO
  price_delta     NUMERIC(10,2) NOT NULL DEFAULT 0
);
```

## Decisiones técnicas

### Datos
El precio unitario, nombre del producto y nombre del modificador se desnormalizan en cada venta — esto es intencional y correcto. Si el dueño cambia el precio mañana, el historial de hoy debe mostrar los valores originales. Las FKs a `products` y `modifiers` son `ON DELETE SET NULL` para preservar el registro histórico si el catálogo cambia. Las ventas nunca se eliminan físicamente — solo cambian `status` a `cancelled` o `refunded`.

### Acceso / Seguridad
Los cajeros pueden INSERT en `sales` solo dentro de su organización. No pueden UPDATE ni DELETE ventas — ese es privilegio del `business_owner`. La cancelación es una mutación de `status`, no una eliminación.

### UI / Contrato de componentes
No hay componentes visuales. Cada INSERT en `sales` es el evento que puede disparar al sistema de agentes (E-06) via un trigger de PostgreSQL que notifica a Supabase Realtime.

## Fuera de scope
- Boleta electrónica SII (v2)
- Webpay, MercadoPago QR (v2)
- Devoluciones y notas de crédito (v2)
- Descuentos a nivel de venta total (v2)

## Estados UI requeridos
No aplica — migración de base de datos.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/migrations/003_sales.test.sql` | Integration (pgTAP) | Venta con total negativo viola CHECK; sale_item con quantity=0 viola CHECK; cancelar venta cambia status sin eliminar; sale_item preserva product_name aunque el product sea eliminado posterior |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| INSERT de venta completa con ítems y modificadores | Todos los registros creados con UUIDs generados |
| DELETE product referenciado en sale_item | `sale_item.product_id = NULL`, `product_name` preservado intacto |
| `UPDATE sales SET status = 'cancelled'` | Éxito, registro no eliminado |
| INSERT sale con total = -1 | Falla con CHECK violation |

---

# E01-T07 — Migración 004: tablas de inventario y movimientos de stock
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Medio

## Objetivo
Crear las tablas que implementan el modelo de inventario event-sourced: cada cambio de stock es un movimiento registrado (`inventory_movements`), y el campo `stock_quantity` de `ingredients` es un valor desnormalizado que se mantiene sincronizado via trigger. Las alertas de stock crítico (`stock_alerts`) son el artefacto observable que conecta el inventario con el sistema de agentes. Este diseño permite auditoría completa del stock histórico y es la fuente de verdad para el Guardián y el Analista.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T05 | Tabla `ingredients` con `stock_quantity` y `critical_stock` como campos target |
| E01-T06 | Tabla `sale_items` para vincular movimientos de salida a ventas específicas |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000300_create_inventory_tables.sql` | CREATE | Tablas: inventory_movements, stock_alerts; trigger de actualización de stock en ingredients; trigger de creación de alertas al cruzar umbral crítico |
| `supabase/tests/migrations/004_inventory.test.sql` | CREATE | Test de integración: validación de triggers de stock y generación de alertas automáticas |

## Tipos esperados
```sql
CREATE TYPE movement_type AS ENUM (
  'sale_out',     -- Salida automática por venta (generado por trigger)
  'purchase_in',  -- Entrada por compra a proveedor (manual)
  'adjustment',   -- Ajuste manual del business_owner
  'waste',        -- Merma declarada
  'initial'       -- Stock inicial al configurar el negocio
);

CREATE TYPE alert_status AS ENUM ('pending', 'read', 'actioned');

CREATE TABLE inventory_movements (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ingredient_id   UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
  sale_item_id    UUID REFERENCES sale_items(id) ON DELETE SET NULL,
  type            movement_type NOT NULL,
  quantity_delta  NUMERIC(10,3) NOT NULL, -- Positivo = entrada, Negativo = salida
  notes           TEXT,
  created_by      UUID REFERENCES auth.users(id) ON DELETE SET NULL,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE stock_alerts (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  ingredient_id   UUID NOT NULL REFERENCES ingredients(id) ON DELETE CASCADE,
  current_stock   NUMERIC(10,3) NOT NULL,
  critical_stock  NUMERIC(10,3) NOT NULL,
  status          alert_status NOT NULL DEFAULT 'pending',
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  resolved_at     TIMESTAMPTZ
);

-- Trigger: actualizar stock_quantity en ingredients tras cada movimiento
CREATE OR REPLACE FUNCTION sync_ingredient_stock()
RETURNS TRIGGER AS $$
BEGIN
  UPDATE ingredients
  SET stock_quantity = stock_quantity + NEW.quantity_delta,
      updated_at = now()
  WHERE id = NEW.ingredient_id;

  -- Si el nuevo stock es <= critical_stock, crear alerta
  INSERT INTO stock_alerts (organization_id, ingredient_id, current_stock, critical_stock)
  SELECT NEW.organization_id, i.id, i.stock_quantity, i.critical_stock
  FROM ingredients i
  WHERE i.id = NEW.ingredient_id
    AND i.stock_quantity <= i.critical_stock
    AND NOT EXISTS (
      SELECT 1 FROM stock_alerts sa
      WHERE sa.ingredient_id = NEW.ingredient_id
        AND sa.status = 'pending'
    );

  RETURN NEW;
END;
$$ LANGUAGE plpgsql;

CREATE TRIGGER after_inventory_movement
  AFTER INSERT ON inventory_movements
  FOR EACH ROW EXECUTE FUNCTION sync_ingredient_stock();
```

## Decisiones técnicas

### Datos
El trigger `sync_ingredient_stock` es atómico con la inserción del movimiento — si el UPDATE de stock falla, el movimiento entero hace rollback. La condición `NOT EXISTS` en la creación de alertas previene duplicados: solo se crea una nueva alerta si no hay una `pending` ya existente para ese ingrediente. El modelo event-sourced garantiza que siempre se puede auditar el stock: `SUM(quantity_delta) WHERE ingredient_id = X` debe igualar `ingredients.stock_quantity`.

### Acceso / Seguridad
Solo el sistema (via trigger) puede crear movimientos de tipo `sale_out`. Los cajeros no tienen permiso de INSERT directo en `inventory_movements`. Los ajustes manuales (`adjustment`, `waste`, `purchase_in`) requieren rol `business_owner`. Las políticas RLS se definen en E01-T12.

### UI / Contrato de componentes
No hay componentes visuales. `stock_alerts` es la tabla que el Guardián (agente) monitorea para generar notificaciones inteligentes.

## Fuera de scope
- Inventario físico / conteo cíclico (v2)
- Notificaciones push al cruzar umbral (se hace via agentes en E-06)
- Stock negativo controlado (v2 — para negocios que permiten pedidos anticipados)

## Estados UI requeridos
No aplica — migración de base de datos con trigger.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/migrations/004_inventory.test.sql` | Integration (pgTAP) | Movimiento de salida (-5) actualiza stock del ingrediente en -5; movimiento de entrada (+10) actualiza en +10; stock que cruza umbral crítico crea stock_alert; segunda alerta no se crea si ya hay una pending; trigger es atómico (falla en UPDATE revierte INSERT) |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| INSERT `inventory_movements` con `quantity_delta=-5` | `ingredients.stock_quantity` baja 5 automáticamente |
| Stock de ingrediente llega a nivel crítico | Registro creado en `stock_alerts` con status='pending' |
| Segunda venta que mantiene stock crítico | No crea segunda alerta (ya hay una pending) |
| `supabase db reset` | Trigger y tablas creados sin errores |

---

# E01-T08 — Migración 005: usuarios, roles y proveedores
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Alto

## Objetivo
Crear la tabla `profiles` que extiende `auth.users` de Supabase con datos del negocio, la tabla `organization_members` que implementa el RBAC multi-tenant (un usuario puede tener rol `business_owner` en una tienda y `cashier` en otra), y la tabla `suppliers` con los proveedores de cada tenant. También agrega la FK faltante de `ingredients.supplier_id` que fue declarada nullable en E01-T05, y los triggers que automatizan la creación de `profiles` y la membresía del owner al registrar una organización.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T04 | Enum `user_role`, tabla `organizations` con `owner_id` |
| E01-T05 | Tabla `ingredients` con `supplier_id` nullable pendiente de FK |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000400_create_users_and_suppliers.sql` | CREATE | Tablas: profiles, organization_members, suppliers; FK suppliers→ingredients; triggers de auto-creación |
| `supabase/tests/migrations/005_users_suppliers.test.sql` | CREATE | Test de integración: validación de perfiles automáticos y membresías RBAC |

## Tipos esperados
```sql
CREATE TABLE profiles (
  id          UUID PRIMARY KEY REFERENCES auth.users(id) ON DELETE CASCADE,
  full_name   TEXT,
  avatar_url  TEXT,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Auto-crear profile cuando se registra un usuario en auth.users
CREATE OR REPLACE FUNCTION handle_new_user()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO profiles (id) VALUES (NEW.id);
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_auth_user_created
  AFTER INSERT ON auth.users
  FOR EACH ROW EXECUTE FUNCTION handle_new_user();

CREATE TABLE organization_members (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  user_id         UUID NOT NULL REFERENCES auth.users(id) ON DELETE CASCADE,
  role            user_role NOT NULL DEFAULT 'cashier',
  is_active       BOOLEAN NOT NULL DEFAULT true,
  invited_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  joined_at       TIMESTAMPTZ,
  UNIQUE(organization_id, user_id)
);

-- Auto-crear membresía del owner cuando se crea una organización
CREATE OR REPLACE FUNCTION handle_new_organization()
RETURNS TRIGGER AS $$
BEGIN
  INSERT INTO organization_members (organization_id, user_id, role, joined_at)
  VALUES (NEW.id, NEW.owner_id, 'business_owner', now());
  RETURN NEW;
END;
$$ LANGUAGE plpgsql SECURITY DEFINER;

CREATE TRIGGER on_organization_created
  AFTER INSERT ON organizations
  FOR EACH ROW EXECUTE FUNCTION handle_new_organization();

CREATE TABLE suppliers (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  name            TEXT NOT NULL,
  contact_name    TEXT,
  phone           TEXT,
  email           TEXT,
  notes           TEXT,
  is_active       BOOLEAN NOT NULL DEFAULT true,
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- FK faltante: ingredients → suppliers
ALTER TABLE ingredients
  ADD CONSTRAINT fk_ingredients_supplier
  FOREIGN KEY (supplier_id) REFERENCES suppliers(id) ON DELETE SET NULL;
```

## Decisiones técnicas

### Datos
La tabla `profiles` se puebla automáticamente cuando Supabase crea un usuario en `auth.users` — esto garantiza que siempre existe un perfil sin intervención manual. El owner de una organización también queda automáticamente en `organization_members` con role `business_owner`. Un usuario puede pertenecer a múltiples organizations con distintos roles — la UNIQUE constraint es por par `(organization_id, user_id)`, no por `user_id` solo.

### Acceso / Seguridad
La verificación de rol para autorización en la aplicación se hace leyendo `organization_members.role` del usuario autenticado. El middleware de Next.js (E01-T15) inyectará este rol como header en cada request. El flag `is_active` permite deshabilitar un cajero sin eliminarlo — preserva el historial de ventas asociado a ese usuario.

### UI / Contrato de componentes
No hay componentes visuales. Esta tabla es consumida por el Business Owner Panel (E-08) para la gestión de RBAC (invitar cajeros, desactivar miembros).

## Fuera de scope
- Pantalla de invitación por email (E-02)
- Permisos granulares por feature dentro de un rol (v2)
- SSO / SAML enterprise

## Estados UI requeridos
No aplica — migración de base de datos.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/migrations/005_users_suppliers.test.sql` | Integration (pgTAP) | Crear organización genera automáticamente organization_member del owner con role=business_owner; crear auth.users genera profile automáticamente; usuario en misma org dos veces viola UNIQUE; eliminar supplier deja ingredients.supplier_id=NULL; usuario puede pertenecer a dos orgs con roles distintos |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| INSERT en `organizations` | `organization_members` contiene fila con `owner_id` y role='business_owner' automáticamente |
| INSERT en `auth.users` | `profiles` contiene fila correspondiente automáticamente |
| Mismo usuario en misma organización dos veces | Error UNIQUE constraint |
| DELETE de supplier con ingredientes asociados | Ingredientes quedan con `supplier_id=NULL`, no error |

---

# E01-T09 — Migración 006: tablas de caja
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Medio

## Objetivo
Crear el esquema de gestión de caja que registra la apertura y cierre de turnos por cajero, el monto inicial declarado, y el cuadre al cierre (efectivo esperado calculado vs efectivo real declarado por el cajero). También agrega la FK de `sales.cash_session_id` que quedó nullable en E01-T06. Un índice único parcial garantiza que un cajero no puede tener dos sesiones abiertas simultáneamente.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T06 | Tabla `sales` con `cash_session_id` nullable pendiente de FK |
| E01-T08 | Tabla `organization_members` para validar que el cajero pertenece a la org |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000500_create_cash_tables.sql` | CREATE | Tabla: cash_sessions; índice único parcial; FK sales→cash_sessions |
| `supabase/tests/migrations/006_cash.test.sql` | CREATE | Test de integración: validación de apertura/cierre de turnos y restricción de sesión única |

## Tipos esperados
```sql
CREATE TYPE session_status AS ENUM ('open', 'closed');

CREATE TABLE cash_sessions (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  cashier_id       UUID NOT NULL REFERENCES auth.users(id) ON DELETE RESTRICT,
  status           session_status NOT NULL DEFAULT 'open',
  opening_amount   NUMERIC(10,2) NOT NULL CHECK (opening_amount >= 0),
  expected_cash    NUMERIC(10,2), -- Se calcula al cerrar: opening + sum de ventas cash
  actual_cash      NUMERIC(10,2), -- Declarado por el cajero al cerrar
  difference       NUMERIC(10,2), -- actual_cash - expected_cash
  opened_at        TIMESTAMPTZ NOT NULL DEFAULT now(),
  closed_at        TIMESTAMPTZ,
  notes            TEXT,
  -- Si está cerrada, debe tener closed_at
  CHECK (status = 'open' OR (status = 'closed' AND closed_at IS NOT NULL))
);

-- Un cajero solo puede tener UNA sesión abierta a la vez
CREATE UNIQUE INDEX cash_sessions_one_open_per_cashier
  ON cash_sessions(cashier_id)
  WHERE status = 'open';

-- FK faltante en sales
ALTER TABLE sales
  ADD CONSTRAINT fk_sales_cash_session
  FOREIGN KEY (cash_session_id) REFERENCES cash_sessions(id) ON DELETE SET NULL;
```

## Decisiones técnicas

### Datos
`expected_cash` se calcula en la capa de aplicación al cerrar la sesión como: `opening_amount + SUM(sales.total WHERE payment_method='cash' AND cash_session_id=id AND status='completed')`. Se almacena desnormalizado para que el cuadre histórico sea inmutable. El índice único parcial `WHERE status = 'open'` es la solución más eficiente para la restricción de sesión única sin locks ni lógica de aplicación.

### Acceso / Seguridad
Un cajero puede abrir y cerrar su propia sesión. No puede ver ni modificar sesiones de otros cajeros. El `business_owner` puede ver todas las sesiones de su organización. La columna `difference` (cuadre de caja) es un dato sensible visible solo para `business_owner`.

### UI / Contrato de componentes
No hay componentes visuales. Esta tabla es el corazón de la Gestión de Caja en el Business Owner Panel (E-08) y en la pantalla de apertura/cierre del cajero (E-03).

## Fuera de scope
- Múltiples cajas físicas por sucursal (v2, plan Business)
- Reporte de caja imprimible (v2)
- Arqueo parcial durante el turno

## Estados UI requeridos
No aplica — migración de base de datos.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/migrations/006_cash.test.sql` | Integration (pgTAP) | Cajero con sesión abierta no puede abrir segunda (índice único parcial); cerrar sesión sin closed_at viola CHECK; cajero puede abrir nueva sesión tras cerrar la anterior; FK sales→cash_sessions funciona bidireccional |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| Cajero abre sesión | `cash_sessions` con status='open' y opened_at |
| Mismo cajero intenta abrir segunda sesión | Error de índice único parcial |
| Cajero cierra sesión | status='closed', closed_at poblado |
| Mismo cajero abre nueva sesión tras cerrar | Éxito — el índice solo bloquea las 'open' |

---

# E01-T10 — Migración 007: tablas del sistema de agentes
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Alto

## Objetivo
Crear el esquema de persistencia para los tres agentes de IA. `agent_structured_memory` almacena el perfil de inteligencia del negocio actualizado por el Analista nocturno (patrones de ventas por día/hora, ingredientes recurrentemente críticos). `agent_episodic_memory` registra eventos relevantes con contexto temporal y TTL de retención. `agent_notifications` es el output observable del sistema — las sugerencias que el Business Owner y el Cajero verán en tiempo real. Este esquema es el diferencial técnico central del producto.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T04 | Tabla `organizations` |
| E01-T07 | Tabla `stock_alerts` (fuente de eventos para la memoria episódica) |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000600_create_agent_tables.sql` | CREATE | Tablas: agent_structured_memory, agent_episodic_memory, agent_notifications; enums agent_type, notification_priority, notification_status |
| `supabase/tests/migrations/007_agents.test.sql` | CREATE | Test de integración: validación de esquemas de memoria y notificaciones de agentes |

## Tipos esperados
```sql
CREATE TYPE agent_type AS ENUM ('analyst', 'anticipator', 'guardian');
CREATE TYPE notification_priority AS ENUM ('info', 'warning', 'critical');
CREATE TYPE notification_status AS ENUM ('unread', 'read', 'actioned', 'dismissed');

-- Un perfil de inteligencia por tenant — actualizado cada noche por el Analista
CREATE TABLE agent_structured_memory (
  id               UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id  UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  version          INTEGER NOT NULL DEFAULT 1,
  -- Patrones: ventas por día semana (1-7), por hora (0-23), por ingrediente
  sales_patterns   JSONB NOT NULL DEFAULT '{}',
  -- Ingredientes con historial de criticidad recurrente
  risk_ingredients JSONB NOT NULL DEFAULT '{}',
  -- Días de historial disponible para el agente
  data_range_days  INTEGER NOT NULL DEFAULT 0,
  last_analyzed_at TIMESTAMPTZ,
  created_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at       TIMESTAMPTZ NOT NULL DEFAULT now(),
  UNIQUE(organization_id)  -- Un perfil por tenant
);

-- Eventos relevantes con TTL — fuente de razonamiento episódico
CREATE TABLE agent_episodic_memory (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  agent           agent_type NOT NULL,
  event_type      TEXT NOT NULL,  -- 'stock_critical', 'unusual_sales_spike', 'holiday_impact'
  context         JSONB NOT NULL, -- Contexto completo del evento
  occurred_at     TIMESTAMPTZ NOT NULL DEFAULT now(),
  expires_at      TIMESTAMPTZ DEFAULT (now() + INTERVAL '90 days')
);

-- Output observable del sistema de agentes
CREATE TABLE agent_notifications (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  agent           agent_type NOT NULL,
  priority        notification_priority NOT NULL DEFAULT 'info',
  status          notification_status NOT NULL DEFAULT 'unread',
  title           TEXT NOT NULL,
  body            TEXT NOT NULL,
  context         JSONB DEFAULT '{}', -- Datos para acciones contextuales en UI
  is_simulated    BOOLEAN NOT NULL DEFAULT false,  -- Para el trial con agente simulado
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now(),
  read_at         TIMESTAMPTZ,
  actioned_at     TIMESTAMPTZ
);
```

## Decisiones técnicas

### Datos
`agent_structured_memory` usa UNIQUE por `organization_id` — exactamente un perfil por tenant, que el Analista actualiza via UPSERT cada noche. El campo `data_range_days` permite que la UI muestre al usuario "Tu agente lleva N días aprendiendo", gestionando las expectativas de los primeros días de uso. La `episodic_memory` tiene TTL de 90 días para control de costos de storage. El campo `is_simulated` en notificaciones permite que el trial muestre notificaciones verosímiles con un badge "preview" sin confundir al usuario.

### Acceso / Seguridad
Los agentes escriben en estas tablas via Edge Functions con `service_role`. El Business Owner y Cajero solo pueden leer `agent_notifications` de su organización. Nadie puede insertar notificaciones manualmente — solo el sistema de agentes via Edge Functions. `agent_episodic_memory` y `agent_structured_memory` son completamente opacas para los usuarios finales.

### UI / Contrato de componentes
`agent_notifications` alimenta el componente de notificaciones en tiempo real (E-07) via Supabase Realtime con la política RLS como guardia de seguridad. El campo `context JSONB` permite renderizar acciones contextuales (ej: botón "Ver ingrediente" cuando la notificación es sobre stock crítico).

## Fuera de scope
- Vector store para RAG semántico (v2 si los patrones JSONB resultan insuficientes)
- Historial de prompts y respuestas del LLM (auditoría avanzada v2)
- Canal WhatsApp para entrega de notificaciones (v2)

## Estados UI requeridos
No aplica — migración de base de datos.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/migrations/007_agents.test.sql` | Integration (pgTAP) | UPSERT en agent_structured_memory respeta UNIQUE; segunda llamada actualiza misma fila; notificación con is_simulated=true es válida; notificación sin title viola NOT NULL; episodic_memory con expires_at pasado es purgable |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| Primera ejecución del Analista: INSERT structured_memory | Éxito, 1 registro por organización |
| Segunda ejecución: UPSERT | Actualiza mismo registro, version++ |
| INSERT notification con context JSONB complejo | Éxito, consultable con operadores JSONB `->` y `->>` |
| `supabase db reset` | Tablas y enums creados limpiamente |

---

# E01-T11 — Migración 008: tablas del Founder Panel
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Medio

## Objetivo
Crear las tablas de telemetría y control cross-tenant del Founder Panel: `token_usage_logs` para rastrear el costo de LLM por tenant (base del Token Tracker), `feature_flags` para activar y desactivar capacidades por plan o por tenant específico sin redeploy, y `system_audit_logs` para trazabilidad de acciones administrativas. Estas tablas son exclusivas del service_role — ningún usuario normal puede acceder a ellas.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T04 | Tabla `organizations`, enum `plan_tier` |
| E01-T10 | Enum `agent_type` (para categorizar el uso de tokens por agente) |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000700_create_founder_tables.sql` | CREATE | Tablas: token_usage_logs, feature_flags, system_audit_logs; revocar permisos a roles authenticated y anon |
| `supabase/tests/migrations/008_founder.test.sql` | CREATE | Test de integración: validación de telemetría, flags y seguridad restrictiva (REVOKE) |

## Tipos esperados
```sql
CREATE TABLE token_usage_logs (
  id              UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  organization_id UUID NOT NULL REFERENCES organizations(id) ON DELETE CASCADE,
  agent           agent_type NOT NULL,
  model           TEXT NOT NULL,            -- 'claude-sonnet-4-5', etc.
  input_tokens    INTEGER NOT NULL CHECK (input_tokens >= 0),
  output_tokens   INTEGER NOT NULL CHECK (output_tokens >= 0),
  cost_usd        NUMERIC(10,6) CHECK (cost_usd >= 0),
  invocation_id   TEXT UNIQUE,              -- Deduplicación por llamada al LLM
  created_at      TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE feature_flags (
  id                   UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  key                  TEXT NOT NULL UNIQUE, -- 'agent_guardian_enabled', 'multi_branch'
  description          TEXT,
  enabled_for_plans    plan_tier[] DEFAULT NULL,  -- NULL = aplica a todos los planes
  enabled_for_orgs     UUID[] DEFAULT NULL,        -- Override por tenant específico
  is_globally_enabled  BOOLEAN NOT NULL DEFAULT false,
  created_at           TIMESTAMPTZ NOT NULL DEFAULT now(),
  updated_at           TIMESTAMPTZ NOT NULL DEFAULT now()
);

CREATE TABLE system_audit_logs (
  id          UUID PRIMARY KEY DEFAULT gen_random_uuid(),
  actor_id    UUID,           -- NULL si la acción es del sistema automático
  actor_type  TEXT NOT NULL,  -- 'founder', 'system', 'agent'
  action      TEXT NOT NULL,  -- 'tenant.suspend', 'impersonate.start', 'flag.toggle'
  target_type TEXT,           -- 'organization', 'user', 'feature_flag'
  target_id   UUID,
  metadata    JSONB DEFAULT '{}',
  ip_address  INET,
  created_at  TIMESTAMPTZ NOT NULL DEFAULT now()
);

-- Revocar todo acceso a usuarios normales — solo service_role puede acceder
REVOKE ALL ON token_usage_logs FROM authenticated, anon;
REVOKE ALL ON feature_flags FROM authenticated, anon;
REVOKE ALL ON system_audit_logs FROM authenticated, anon;
```

## Decisiones técnicas

### Datos
`token_usage_logs.cost_usd` se calcula en la Edge Function antes de insertar, basado en la tarifa del modelo en el momento de la llamada. Para el Token Tracker del Founder Panel, la query es `GROUP BY organization_id, date_trunc('month', created_at)` con `SUM(cost_usd)`. El campo `invocation_id` previene duplicados en caso de reintentos de Edge Functions. Los `system_audit_logs` son append-only por diseño — el founder puede leer pero no modificar.

### Acceso / Seguridad
Estas tablas no usan RLS habitual — directamente se revocan los permisos para `authenticated` y `anon`. Solo el `service_role` puede acceder. El Founder Panel usa `createAdminClient()` de E01-T02 exclusivamente. El REVOKE es más seguro que RLS aquí porque no depende de que las políticas estén correctamente configuradas.

### UI / Contrato de componentes
No hay componentes visuales. Consumido exclusivamente por el Founder Panel (E-09): Token Tracker, Feature Flag Management y Audit Logs.

## Fuera de scope
- Alertas automáticas cuando un tenant supera cuota de tokens (v2)
- Billing real basado en token_usage con Fintoc/Flow (v2)
- Retención configurable de audit logs por plan

## Estados UI requeridos
No aplica — migración de base de datos.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/migrations/008_founder.test.sql` | Integration (pgTAP) | feature_flag key UNIQUE; token_usage con cost negativo viola CHECK; audit_log con actor_id=NULL es válido; usuario authenticated recibe error de permiso al hacer SELECT en cualquiera de las tres tablas |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| INSERT token_usage con input_tokens negativos | Error CHECK constraint |
| INSERT feature_flag con key duplicado | Error UNIQUE constraint |
| SELECT en token_usage_logs con rol authenticated | Error de permisos (REVOKE efectivo) |
| INSERT system_audit_log con actor_id=NULL | Éxito (acción del sistema) |
| service_role puede SELECT/INSERT en las tres tablas | Éxito |

---

# E01-T12 — Implementar políticas RLS: tablas de negocio
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Alto

## Objetivo
Activar Row Level Security en todas las tablas de negocio y definir las políticas de aislamiento por tenant y por rol. Esta tarea es el hardening de seguridad más crítico del sistema — las políticas aquí garantizan que aunque exista un bug en la capa de aplicación que intente acceder a datos de otro tenant, PostgreSQL lo bloqueará antes de devolver una sola fila. Las funciones helper `get_user_org_id()` y `user_has_role()` centralizan la lógica de resolución de tenant y rol, evitando duplicación en cada política.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T04 al E01-T09 | Todas las tablas de negocio con `organization_id` existentes |
| E01-T08 | Tabla `organization_members` para resolución de tenant y rol del usuario autenticado |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000800_enable_rls_business_tables.sql` | CREATE | ENABLE RLS + políticas CRUD para todas las tablas de negocio; funciones helper SECURITY DEFINER |
| `supabase/tests/rls/business_isolation.test.sql` | CREATE | Test de seguridad: validación de aislamiento multi-tenant y acceso por rol en negocio |

## Tipos esperados
```sql
-- =============================================
-- FUNCIONES HELPER (SECURITY DEFINER para acceso privilegiado)
-- =============================================

-- Resuelve el organization_id del usuario autenticado actual
CREATE OR REPLACE FUNCTION get_user_org_id()
RETURNS UUID AS $$
  SELECT organization_id
  FROM organization_members
  WHERE user_id = auth.uid()
    AND is_active = true
  LIMIT 1;
$$ LANGUAGE SQL SECURITY DEFINER STABLE;

-- Verifica si el usuario tiene un rol específico en su organización
CREATE OR REPLACE FUNCTION user_has_role(required_role user_role)
RETURNS BOOLEAN AS $$
  SELECT EXISTS (
    SELECT 1 FROM organization_members
    WHERE user_id = auth.uid()
      AND role = required_role
      AND is_active = true
  );
$$ LANGUAGE SQL SECURITY DEFINER STABLE;

-- =============================================
-- EJEMPLO COMPLETO: políticas para products
-- (mismo patrón se repite en: categories, ingredients,
-- recipe_ingredients, modifiers, suppliers, sales,
-- sale_items, sale_item_modifiers, inventory_movements,
-- stock_alerts, cash_sessions)
-- =============================================

ALTER TABLE products ENABLE ROW LEVEL SECURITY;

-- SELECT: cualquier miembro activo ve sus productos
CREATE POLICY "products_select_own_org"
  ON products FOR SELECT
  USING (organization_id = get_user_org_id());

-- INSERT: solo business_owner puede crear productos
CREATE POLICY "products_insert_owner_only"
  ON products FOR INSERT
  WITH CHECK (
    organization_id = get_user_org_id()
    AND user_has_role('business_owner')
  );

-- UPDATE: solo business_owner puede editar
CREATE POLICY "products_update_owner_only"
  ON products FOR UPDATE
  USING (organization_id = get_user_org_id())
  WITH CHECK (user_has_role('business_owner'));

-- DELETE: solo business_owner puede eliminar
CREATE POLICY "products_delete_owner_only"
  ON products FOR DELETE
  USING (
    organization_id = get_user_org_id()
    AND user_has_role('business_owner')
  );

-- EXCEPCIÓN: sales INSERT también permitido para cashier
ALTER TABLE sales ENABLE ROW LEVEL SECURITY;
CREATE POLICY "sales_insert_any_member"
  ON sales FOR INSERT
  WITH CHECK (organization_id = get_user_org_id());
-- (SELECT y UPDATE de sales solo para business_owner)
```

## Decisiones técnicas

### Datos
Las funciones helper usan `SECURITY DEFINER` y `STABLE` (no modifica datos, mismos parámetros = misma respuesta en una transacción). El atributo `STABLE` permite a PostgreSQL cachear el resultado dentro de la misma transacción, reduciendo el overhead de RLS. Para v1 mono-tenant (un usuario pertenece a una sola organización), `LIMIT 1` en `get_user_org_id()` es correcto. En v2 multi-sucursal, se necesitará un JWT claim adicional para especificar el tenant activo en sesión.

### Acceso / Seguridad
La tabla `organizations` tiene política especial: SELECT para el owner (`owner_id = auth.uid()`), pero INSERT/UPDATE/DELETE solo via service_role (no se crean políticas para authenticated en estas operaciones = denegado por defecto). Esto previene que cualquier usuario se cree organizaciones fraudulentas.

### UI / Contrato de componentes
No hay componentes visuales. Esta es infraestructura de seguridad pura.

## Fuera de scope
- Políticas para tablas de agentes (E01-T13)
- Políticas multi-tenant por sesión activa (v2)
- Auditoría de accesos via triggers RLS

## Estados UI requeridos
No aplica — migración de base de datos.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/rls/business_isolation.test.sql` | Security (pgTAP) | Usuario Org A no puede SELECT products de Org B; cajero no puede INSERT product; business_owner puede INSERT/UPDATE/DELETE products; cajero puede INSERT sales; usuario sin organización activa recibe 0 filas en todas las tablas |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| Auth como usuario Org A, `SELECT * FROM products` | Solo productos de Org A |
| Auth como usuario Org A, `SELECT * FROM products WHERE organization_id = 'org-b-id'` | 0 filas (RLS filtra silenciosamente, sin error) |
| Auth como cajero, `INSERT INTO products` | Error de política RLS |
| Auth como business_owner, `INSERT INTO products` | Éxito |
| Sin auth (anon), cualquier SELECT | 0 filas |

---

# E01-T13 — Implementar políticas RLS: tablas de agentes
> Milestone: M1-02 — Base de datos multi-tenant con RLS activo · Risk: Medio

## Objetivo
Implementar el hardening RLS para las tablas del sistema de agentes. `agent_notifications` tiene la política más compleja: Business Owner y Cajero pueden leer las notificaciones de su organización y actualizar su status (leída/accionada), pero solo el sistema puede crear nuevas. `agent_structured_memory` es visible únicamente para el Business Owner — es información estratégica del negocio. `agent_episodic_memory` es completamente opaca para todos los usuarios finales.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T10 | Tablas del sistema de agentes |
| E01-T12 | Funciones helper `get_user_org_id()` y `user_has_role()` disponibles |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `supabase/migrations/20240001000900_enable_rls_agent_tables.sql` | CREATE | ENABLE RLS + políticas para agent_notifications, agent_structured_memory, agent_episodic_memory |
| `supabase/tests/rls/agent_isolation.test.sql` | CREATE | Test de seguridad: validación de aislamiento en tablas de agentes y memoria |

## Tipos esperados
```sql
-- agent_notifications: lectura para todos los miembros, UPDATE de status, INSERT solo sistema
ALTER TABLE agent_notifications ENABLE ROW LEVEL SECURITY;

CREATE POLICY "notifications_select_own_org"
  ON agent_notifications FOR SELECT
  USING (organization_id = get_user_org_id());

-- UPDATE solo para cambiar campos de status — se usa función RPC para validar
-- que no se modifiquen title, body ni otros campos inmutables
CREATE POLICY "notifications_update_status"
  ON agent_notifications FOR UPDATE
  USING (organization_id = get_user_org_id());
-- (sin política INSERT para authenticated = solo service_role puede crear)

-- agent_structured_memory: solo business_owner puede leer, sistema escribe
ALTER TABLE agent_structured_memory ENABLE ROW LEVEL SECURITY;

CREATE POLICY "structured_memory_select_owner"
  ON agent_structured_memory FOR SELECT
  USING (
    organization_id = get_user_org_id()
    AND user_has_role('business_owner')
  );
-- (sin políticas INSERT/UPDATE para authenticated = solo service_role)

-- agent_episodic_memory: completamente opaca para usuarios
ALTER TABLE agent_episodic_memory ENABLE ROW LEVEL SECURITY;
-- (sin políticas para authenticated = 0 filas siempre, solo service_role)
```

## Decisiones técnicas

### Datos
El UPDATE en `agent_notifications` está intencionalmente sin restricción de campos a nivel de política — se controlará via función RPC en E-07 que valida que solo `status`, `read_at` y `actioned_at` puedan ser modificados por usuarios. Intentar modificar `title` o `body` via RPC lanzará un error de validación antes de llegar a la DB.

### Acceso / Seguridad
El cajero puede leer `agent_notifications` pero no `agent_structured_memory` — la memoria del negocio es información estratégica solo para el dueño. La `episodic_memory` es el "diario interno" del sistema — nunca visible para ningún usuario final, solo para el motor de agentes.

### UI / Contrato de componentes
Las políticas aquí habilitan que el componente de notificaciones en tiempo real (E-07) use Supabase Realtime con seguridad: la suscripción a `agent_notifications` solo recibirá notificaciones de la propia organización del usuario.

## Fuera de scope
- Purga automática de episodic_memory por TTL (script de mantenimiento, v2)
- Conteo separado de notificaciones no leídas por rol

## Estados UI requeridos
No aplica — migración de base de datos.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `supabase/tests/rls/agent_isolation.test.sql` | Security (pgTAP) | Cajero puede SELECT agent_notifications de su org; cajero no puede INSERT agent_notifications; business_owner puede SELECT agent_structured_memory; cajero no puede SELECT agent_structured_memory; usuario autenticado no puede SELECT agent_episodic_memory; usuario Org A no ve notificaciones de Org B |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| Auth como cajero, SELECT agent_notifications | Solo notificaciones de su organización |
| Auth como cajero, INSERT agent_notifications | Error de política RLS |
| Auth como business_owner, SELECT agent_structured_memory | Perfil de su organización |
| Auth como cajero, SELECT agent_structured_memory | 0 filas |
| Auth authenticated, SELECT agent_episodic_memory | 0 filas |

---

# E01-T14 — Generar tipos Supabase y contrato de tipos TypeScript
> Milestone: M1-03 — Capa de acceso tipada operativa · Risk: Medio

## Objetivo
Con todas las migraciones de M1-02 aplicadas, generar los tipos TypeScript desde el schema de Supabase y construir el módulo de tipos del dominio que el resto del codebase importará. Este módulo es el contrato entre la base de datos y la capa de aplicación — cualquier query a la DB que use un campo inexistente será detectada en tiempo de compilación, antes del runtime. Actualizar los clientes Supabase para usar los tipos concretos generados.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T04 al E01-T13 | Todas las migraciones del dominio aplicadas en la instancia local |
| E01-T02 | Clientes Supabase base sin tipado concreto (usan `Database` genérico) |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `types/supabase.ts` | CREATE | Generado por `supabase gen types typescript --local` — NUNCA editar manualmente |
| `types/database.ts` | CREATE | Re-exports convenientes con helpers Row/Insert/Update sobre los tipos generados |
| `lib/supabase/server.ts` | MODIFY | Actualizar import de `Database` desde `@/types/supabase` |
| `lib/supabase/client.ts` | MODIFY | Actualizar import de `Database` desde `@/types/supabase` |
| `lib/supabase/admin.ts` | MODIFY | Actualizar import de `Database` desde `@/types/supabase` |
| `package.json` | MODIFY | Agregar script `"db:types": "supabase gen types typescript --local > types/supabase.ts"` |
| `__tests__/types/database.test.ts` | CREATE | Test de tipos: validación de esquemas Row, Insert y Update |

## Tipos esperados
```typescript
// types/database.ts — Contrato estable del dominio (NO el archivo generado)
import type { Database } from './supabase'

type Tables = Database['public']['Tables']
type Enums = Database['public']['Enums']

// Tipos Row (resultado de SELECT)
export type Organization = Tables['organizations']['Row']
export type Product = Tables['products']['Row']
export type Ingredient = Tables['ingredients']['Row']
export type Category = Tables['categories']['Row']
export type RecipeIngredient = Tables['recipe_ingredients']['Row']
export type Modifier = Tables['modifiers']['Row']
export type Supplier = Tables['suppliers']['Row']
export type Sale = Tables['sales']['Row']
export type SaleItem = Tables['sale_items']['Row']
export type CashSession = Tables['cash_sessions']['Row']
export type OrganizationMember = Tables['organization_members']['Row']
export type AgentNotification = Tables['agent_notifications']['Row']
export type AgentStructuredMemory = Tables['agent_structured_memory']['Row']

// Tipos Insert (campos requeridos para INSERT)
export type NewSale = Tables['sales']['Insert']
export type NewProduct = Tables['products']['Insert']
export type NewIngredient = Tables['ingredients']['Insert']

// Tipos Update (todos los campos opcionales para UPDATE)
export type UpdateProduct = Tables['products']['Update']
export type UpdateIngredient = Tables['ingredients']['Update']

// Enums de la base de datos
export type PlanTier = Enums['plan_tier']
export type UserRole = Enums['user_role']
export type AgentType = Enums['agent_type']
export type BusinessTemplate = Enums['business_template']
export type PaymentMethod = Enums['payment_method']
export type MovementType = Enums['movement_type']
```

## Decisiones técnicas

### Datos
`types/supabase.ts` es el archivo generado — la fuente de verdad es la base de datos. `types/database.ts` es el contrato estable que el resto del codebase importa — si el schema cambia, solo `database.ts` necesita actualización, no todos los archivos que usan los tipos. El script `db:types` debe correr después de cada nueva migración aplicada.

### Acceso / Seguridad
No hay lógica de seguridad aquí. Los tipos son únicamente para type-safety en tiempo de compilación.

### UI / Contrato de componentes
Los tipos generados son el contrato maestro para el desarrollo de componentes. Un componente que renderiza una lista de productos usará `Product[]`. Un formulario de creación usará `NewProduct`. Ningún componente definirá sus propias interfaces para entidades del dominio — siempre importarán desde `@/types/database`.

## Fuera de scope
- ORM adicional (Prisma, Drizzle) — Supabase client tipado es suficiente para v1
- Tipos para payloads de Edge Functions (se definen en E-06)
- Zod schemas de validación (se agregan en E-03 para el POS)

## Estados UI requeridos
No aplica — El módulo de tipos provee interfaces estáticas para el compilador de TypeScript, no posee representación visual ni estados de interfaz.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `__tests__/types/database.test.ts` | Unit (type-level con tsd) | "Organization" tiene campo "slug"; "NewSale" no requiere "id"; "UpdateProduct" tiene todos los campos opcionales; query con campo inexistente lanza error de compilación |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| `npm run db:types` | Genera `types/supabase.ts` sin errores |
| `npm run type-check` | 0 errores TypeScript en todo el proyecto |
| Usar campo inexistente en query Supabase | Error en compilación, no en runtime |
| Import de `Sale` en cualquier archivo | Autocomplete muestra todos los campos de la tabla |
| `types/supabase.ts` modificado manualmente | `git diff` muestra cambios — señal de que debe regenerarse |

---

# E01-T15 — Middleware de Next.js: autenticación y tenant resolution
> Milestone: M1-03 — Capa de acceso tipada operativa · Risk: Alto

## Objetivo
Crear el middleware de Next.js que intercepta cada request, valida el JWT de Supabase, refresca el token si está por expirar, y resuelve el `organization_id` y `role` del usuario validado inyectándolos como headers en la request. Es la única puerta de entrada a todas las rutas protegidas. Sin él, las rutas del dashboard y del founder son accesibles sin auth. También crea la página de login mínima funcional necesaria para el test de integración del milestone.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T02 | Helper `lib/supabase/middleware.ts` para refresh de sesión sin romper cookies |
| E01-T14 | Tipos `OrganizationMember`, `UserRole`, `PlanTier` |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `middleware.ts` | CREATE | Middleware principal: auth check, refresh de token, tenant resolution, inyección de headers |
| `lib/auth/get-session.ts` | CREATE | Helper para leer la sesión resuelta en Server Components via headers |
| `lib/auth/constants.ts` | CREATE | Rutas públicas, rutas de founder, rutas de redirect por estado |
| `app/(auth)/login/page.tsx` | CREATE | Página de login funcional mínima (formulario email+password) para tests de integración |
| `app/(auth)/login/actions.ts` | CREATE | Server Action para auth con Supabase Auth |
| `__tests__/middleware.test.ts` | CREATE | Test de resolución de tenants y protección de rutas en middleware |

## Tipos esperados
```typescript
// lib/auth/constants.ts
export const PUBLIC_ROUTES = ['/login', '/register', '/'] as const
export const FOUNDER_ROUTES_PREFIX = '/founder'
export const DASHBOARD_ROUTES_PREFIX = '/dashboard'

// lib/auth/get-session.ts
export type SessionContext = {
  userId: string
  organizationId: string
  role: UserRole
  plan: PlanTier
  orgStatus: string
}

export async function getSessionContext(): Promise<SessionContext | null> {
  // Lee headers inyectados por el middleware
  // Retorna null si no hay sesión válida o headers ausentes
}

// middleware.ts — lógica principal
export async function middleware(request: NextRequest) {
  // 1. Refrescar token si es necesario
  // 2. Verificar JWT válido
  // 3. Resolver organization_id y role desde organization_members
  // 4. Inyectar headers: X-Organization-Id, X-User-Role, X-Plan-Tier
  // 5. Verificar claim is_founder para rutas /founder
  // 6. Redirect a /login si no validado en rutas protegidas
}

export const config = {
  matcher: ['/((?!_next/static|_next/image|favicon.ico|api/health).*)'],
}
```

## Decisiones técnicas

### Datos
El middleware consulta `organization_members` una vez por request para resolver el rol. En v1 este overhead es aceptable. En v2 se migrará a JWT custom claims para eliminar la query de DB en cada request. La resolución de `plan` se obtiene desde `organizations.plan` en la misma query (JOIN). El resultado se inyecta como headers `X-Organization-Id`, `X-User-Role` y `X-Plan-Tier` para que los Server Components los lean sin nueva query.

### Acceso / Seguridad
Las rutas bajo `/founder` verifican un metadata field `is_founder: true` en `auth.users.raw_user_meta_data` — este campo solo puede ser asignado via service_role durante el onboarding del founder. Si el claim no existe, redirect a `/dashboard`. El middleware nunca expone el JWT o las keys en headers de respuesta — solo datos derivados y sanitizados.

### UI / Contrato de componentes
La página `/login` es funcional mínima — solo el formulario email+password con estados de Loading y Error. El diseño completo con branding viene en E-02. Debe funcionar correctamente para el test de integración del M1-03.

## Fuera de scope
- Magic link / OAuth providers (v2)
- MFA (v2)
- Rate limiting en middleware (v2)
- Página de registro completa (E-02)

## Estados UI requeridos
- Login page Loading: botón deshabilitado con spinner mientras se envía
- Login page Error: mensaje de error bajo el formulario (credenciales inválidas)
- Login page Success: redirect automático a /dashboard

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `__tests__/middleware.test.ts` | Integration | Request sin JWT → redirect 302 a /login; Request con JWT válido → headers X-Organization-Id y X-User-Role presentes; Request a /founder sin is_founder claim → redirect a /dashboard; Token expirado → refresh automático y continúa |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| GET /dashboard sin sesión | Redirect 302 a /login |
| GET /dashboard con sesión válida | Request pasa con headers inyectados |
| GET /founder con usuario normal | Redirect a /dashboard |
| GET /founder con usuario founder | Request pasa correctamente |
| Token expirado (menos de 60s de vida) | Refresh automático, usuario no interrumpido |
| Login con credenciales incorrectas | Error visible en formulario, sin redirect |
| Login exitoso | Redirect a /dashboard con sesión activa |

---

# E01-T16 — Configurar GitHub Actions: pipeline CI
> Milestone: M1-04 — Pipeline CI/CD operativo · Risk: Bajo

## Objetivo
Crear el pipeline de Integración Continua que corre automáticamente en cada push y pull request. Ejecuta en paralelo tres jobs independientes: calidad de código (lint + typecheck), tests unitarios e integración con Supabase local, y build de producción. Un fallo en cualquier job bloquea el merge. Este pipeline es la red de seguridad que protege el codebase de regresiones que los agentes de IA pudieran introducir al generar código en paralelo.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T01 | Scripts npm: `lint`, `type-check`, `build` en package.json |
| E01-T02 | Supabase CLI disponible para instancia local en CI |
| E01-T03 | ESLint y TypeScript configurados como base del job de calidad |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `.github/workflows/ci.yml` | CREATE | Pipeline CI con 3 jobs paralelos: quality, test, build |
| `.github/workflows/pr-checks.yml` | CREATE | Checks específicos de PR: tamaño máximo de diff, convención de commits |
| `vitest.config.ts` | CREATE | Configuración de Vitest: paths, coverage, setup files |
| `__tests__/setup.ts` | CREATE | Setup global: mocks de Supabase client, variables de entorno de test |
| `__tests__/ci/pipeline.test.ts` | CREATE | Test de validación de estructura de jobs en workflows de GitHub |

## Tipos esperados
```yaml
# .github/workflows/ci.yml — estructura completa
name: CI
on:
  push:
    branches: ['**']
  pull_request:
    branches: [main, develop]

jobs:
  quality:
    name: Lint & TypeCheck
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: actions/setup-node@v4
        with: { node-version: '20', cache: 'npm' }
      - run: npm ci
      - run: npm run lint
      - run: npm run type-check

  test:
    name: Tests
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v4
      - uses: supabase/setup-cli@v1
      - run: supabase start
      - run: npm ci
      - run: npm run test
      - run: supabase test db  # Tests pgTAP de migraciones y RLS

  build:
    name: Build
    runs-on: ubuntu-latest
    env:
      NEXT_PUBLIC_SUPABASE_URL: ${{ secrets.STAGING_SUPABASE_URL }}
      NEXT_PUBLIC_SUPABASE_ANON_KEY: ${{ secrets.STAGING_SUPABASE_ANON_KEY }}
    steps:
      - uses: actions/checkout@v4
      - run: npm ci
      - run: npm run build
```

```typescript
// vitest.config.ts
import { defineConfig } from 'vitest/config'
import { resolve } from 'path'

export default defineConfig({
  test: {
    environment: 'node',
    setupFiles: ['__tests__/setup.ts'],
    globals: true,
  },
  resolve: {
    alias: { '@': resolve(__dirname, '.') }
  }
})
```

## Decisiones técnicas

### Datos
Los tres jobs corren en paralelo — un fallo en cualquiera bloquea el merge pero no espera a los otros. La instancia de Supabase en CI usa `supabase/setup-cli@v1` que levanta un contenedor Docker con el schema completo del proyecto. Las variables de entorno de CI son instancias de staging — nunca producción.

### Acceso / Seguridad
Las PRs de forks externos no tienen acceso a GitHub Secrets por defecto (comportamiento estándar de GitHub Actions). El job de build usa las keys de staging explícitamente — no las de producción. Los secrets nunca se imprimen en logs (GitHub Actions enmascara automáticamente los valores de secrets).

### UI / Contrato de componentes
No hay componentes visuales. El pipeline incluye implícitamente la validación Anti-UI-Orphaning: el job de build fallará si hay componentes importados en páginas que no existen, o componentes creados sin ser importados en ningún layout.

## Fuera de scope
- Tests end-to-end con Playwright (v2)
- Análisis de cobertura de código con reporte en PR
- Lighthouse CI para métricas de performance
- Tests de carga o stress

## Estados UI requeridos
No aplica — configuración de pipeline sin componentes visuales.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `__tests__/ci/pipeline.test.ts` | Meta-test | El pipeline en sí es el test de validación — se verifica que los tres jobs existen y tienen los pasos correctos |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| Push con error de TypeScript | Job `quality` falla, merge bloqueado |
| Push con test unitario fallido | Job `test` falla, merge bloqueado |
| Push con error de build de Next.js | Job `build` falla, merge bloqueado |
| Push limpio en los tres jobs | Todos los checks en verde, merge permitido |
| `npm run test` en local | Vitest corre y reporta resultados con path aliases resueltos |

---

# E01-T17 — Configurar GitHub Actions: pipeline CD con Supabase migrations
> Milestone: M1-04 — Pipeline CI/CD operativo · Risk: Medio

## Objetivo
Crear el pipeline de Despliegue Continuo que se activa en merge a `main`. Despliega a Vercel y aplica las migraciones de Supabase en staging de forma transaccional — cada migración corre en `BEGIN/COMMIT` y un fallo activa `ROLLBACK` total del archivo, deteniendo el deploy. El pipeline de producción es manual (`workflow_dispatch`) para prevenir deploys accidentales. Implementa el Migration-First Protocol y el DLP Policy del playbook.

## Dependencias consumidas
| Tarea | Qué aporta |
|:---|:---|
| E01-T16 | Pipeline CI que debe pasar antes de activar CD |
| E01-T04 al E01-T13 | Todas las migraciones en `/supabase/migrations/` listas para aplicar |

## Archivos
| Archivo | Acción | Responsabilidad |
|:---|:---|:---|
| `.github/workflows/cd-staging.yml` | CREATE | CD automático a staging en merge a main: migraciones + deploy Vercel |
| `.github/workflows/cd-production.yml` | CREATE | CD manual (`workflow_dispatch`) para producción con confirmación requerida |
| `scripts/run-migrations.sh` | CREATE | Script transaccional: valida orden, detecta DROP sin flag, ejecuta BEGIN/COMMIT por archivo |
| `__tests__/scripts/run-migrations.test.sh` | CREATE | Test del motor de migraciones: transaccionalidad y DLP protection |

## Tipos esperados
```yaml
# .github/workflows/cd-staging.yml
name: CD Staging
on:
  push:
    branches: [main]

jobs:
  deploy-staging:
    runs-on: ubuntu-latest
    environment: staging
    steps:
      - uses: actions/checkout@v4
      - name: Apply Supabase Migrations
        env:
          SUPABASE_DB_URL: ${{ secrets.STAGING_DB_URL }}
          FORCE_DESTRUCTIVE_MIGRATIONS: ${{ vars.FORCE_DESTRUCTIVE_MIGRATIONS }}
        run: bash scripts/run-migrations.sh
      - name: Deploy to Vercel
        uses: amondnet/vercel-action@v25
        with:
          vercel-token: ${{ secrets.VERCEL_TOKEN }}
          vercel-org-id: ${{ secrets.VERCEL_ORG_ID }}
          vercel-project-id: ${{ secrets.VERCEL_PROJECT_ID }}
          vercel-args: '--prod'
```

```bash
#!/bin/bash
# scripts/run-migrations.sh — Migration-First Protocol
set -e

MIGRATIONS_DIR="supabase/migrations"

# Ordenar migraciones por nombre (timestamp prefix garantiza orden)
for migration_file in $(ls "$MIGRATIONS_DIR"/*.sql | sort); do
  filename=$(basename "$migration_file")

  # DLP Policy: bloquear DROP sin flag explícito
  if grep -qi "DROP\s\+TABLE\|DROP\s\+COLUMN\|DROP\s\+SCHEMA" "$migration_file"; then
    if [ "$FORCE_DESTRUCTIVE_MIGRATIONS" != "true" ]; then
      echo "❌ BLOCKED: $filename contains destructive DDL."
      echo "Set FORCE_DESTRUCTIVE_MIGRATIONS=true to proceed."
      exit 1
    fi
    echo "⚠️  WARNING: Applying destructive migration with override flag: $filename"
  fi

  echo "→ Applying: $filename"

  # Ejecutar en bloque transaccional
  psql "$SUPABASE_DB_URL" << SQL
    BEGIN;
    \i $migration_file
    COMMIT;
SQL

  if [ $? -ne 0 ]; then
    echo "❌ FAILED: $filename — Rolling back."
    psql "$SUPABASE_DB_URL" -c "ROLLBACK;" 2>/dev/null || true
    exit 1
  fi

  echo "✅ Applied: $filename"
done

echo "✅ All migrations applied successfully."
```

## Decisiones técnicas

### Datos
Las migraciones se aplican en orden lexicográfico por nombre de archivo — el prefijo de timestamp (`20240001000000_`) garantiza la secuencia correcta. La detección de `DROP` es preventiva — el regex busca `DROP TABLE`, `DROP COLUMN` y `DROP SCHEMA`. `DROP INDEX` y `DROP FUNCTION` no son bloqueados ya que son operaciones de menor riesgo. El pipeline de producción requiere aprobación manual en el environment de GitHub (`environment: production`) antes de ejecutar.

### Acceso / Seguridad
Los secrets de staging y producción son completamente separados — `STAGING_DB_URL` nunca tiene acceso a la DB de producción. El `VERCEL_TOKEN` tiene scope limitado al proyecto específico. El flag `FORCE_DESTRUCTIVE_MIGRATIONS` es una variable de entorno del runner, no un secret, para que sea visible en los logs de auditoría del pipeline.

### UI / Contrato de componentes
No hay componentes visuales. El resultado observable del CD es la URL de staging con la versión actualizada y las migraciones aplicadas.

## Fuera de scope
- Preview deployments por PR (se habilita en Vercel sin cambios de código)
- Notificaciones de deploy a Slack o Discord (v2)
- Rollback automático de deploy Vercel si las migraciones fallan (v2 — requiere Vercel API)
- Múltiples entornos (dev, qa, staging, prod) con pipelines independientes

## Estados UI requeridos
No aplica — configuración de pipeline.

## Tests
| Archivo | Tipo | Casos clave |
|:---|:---|:---|
| `__tests__/scripts/run-migrations.test.sh` | Integration (bats) | Migración válida aplica y hace COMMIT; migración con SQL inválido hace ROLLBACK y falla el script; archivo con DROP sin flag FORCE bloquea; archivo con DROP y flag FORCE aplica con warning |

## Criterio de salida
| Escenario | Resultado esperado |
|:---|:---|
| Merge a main con migración nueva | Migración aplicada en staging antes del deploy de Vercel |
| Migración con error SQL en CD | ROLLBACK, deploy no ocurre, pipeline falla con mensaje descriptivo |
| Migración con `DROP TABLE` sin flag | Script rechaza con mensaje de bloqueo DLP |
| Migración con `DROP TABLE` con `FORCE_DESTRUCTIVE_MIGRATIONS=true` | Aplica con warning visible en logs |
| Deploy exitoso | URL de staging accesible con nueva versión en menos de 5 minutos |
| Trigger manual de `cd-production.yml` | Requiere aprobación en GitHub Environments antes de ejecutar |

---

## Resumen de tasks por milestone

| Milestone | Tasks | Riesgo máximo |
|---|---|---|
| M1-01 Entorno base | T01, T02, T03 | Medio |
| M1-02 Base de datos + RLS | T04, T05, T06, T07, T08, T09, T10, T11, T12, T13 | Alto |
| M1-03 Capa de acceso tipada | T14, T15 | Alto |
| M1-04 CI/CD | T16, T17 | Medio |

## Firma de aprobación (Nexus Forge)

```
Épica   : E-01 — Fundación e Infraestructura
Estado  : DRAFT — Pendiente de firma humana
Versión : 1.0
Fecha   : 2024

[ ] Aprobado por: _______________
[ ] Fecha de aprobación: _______________
[ ] Pasa a status: TODO
```
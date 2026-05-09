# Fase 4 Frontend UX/UI

## Implementado

- Base Next.js + React + TypeScript en `apps/web`.
- Layout maestro con sidebar colapsable preparado, topbar, busqueda, notificaciones, avatar y cambio de tema.
- Sistema visual inspirado en los mockups: azul, blanco, gris, tarjetas redondeadas, sombras suaves, verdes para ingresos, rojos para egresos, azul para ahorro/metas y alertas por severidad.
- Pantallas base: login, registro, recuperar/restablecer contrasena, onboarding, dashboard, movimientos, drawer registrar movimiento, metas, crear meta, detalle de meta, simuladores de ahorro/vivir solo/carro/viaje, reglas, reportes, configuracion, notificaciones, 404 y sesion expirada.
- Componentes reutilizables: `AppShell`, `PageHeader`, `EmptyState`, `MoneyInput`, `MetricCard`, graficos base, `GoalCard`, `MovementTable`, `SimulatorTabs`.
- Cliente API preparado para Fase 3 con `X-Request-ID`, `X-Client-Version`, `X-Timezone`, `Idempotency-Key` en creacion de movimientos y `credentials: include`.
- Preferencias visuales de MVP en localStorage: modo claro/oscuro, acento de color y modo compacto.

## Variables De Entorno

Crear `apps/web/.env.local` desde `apps/web/.env.example`:

```powershell
NEXT_PUBLIC_API_BASE_URL=http://localhost:8000/api/v1
NEXT_PUBLIC_CLIENT_VERSION=0.1.0
```

No se guardan secretos en el frontend. Solo se usan variables publicas `NEXT_PUBLIC_*`.

## Ejecutar

```powershell
cd apps/web
npm install
npm run dev
```

Abrir `http://localhost:3000`.

## Pruebas

```powershell
cd apps/web
npm run test
npm run e2e
npm run lint
```

En este entorno de Codex no hay `npm` disponible, por eso no se instalaron dependencias ni se levanto el dev server.

## Seguridad Frontend

- No hay API keys, tokens privados ni credenciales quemadas.
- El cliente API usa cookies/sesion segura mediante `credentials: include`; no persiste tokens en localStorage.
- `localStorage` se limita a preferencias visuales no sensibles.
- Inputs monetarios trabajan con string decimal normalizado; el backend sigue siendo la fuente de verdad para calculos criticos.
- Errores de API deben mostrarse como mensajes entendibles con trace/request id; no se exponen stack traces.
- El frontend envia `Idempotency-Key` en creacion de movimientos para evitar duplicados.
- Se respetan dominios autorizados configurando `NEXT_PUBLIC_API_BASE_URL` por entorno.

## Decisiones

- El nombre visible nuevo es NexoVia; MetaFinanzas queda tratado como nombre historico de documentos/mockups.
- Los datos visibles son mock data de UI mientras se conectan TanStack Query y endpoints reales.
- Reportes se implementan como pantalla visual preparada; el backend de Fase 3 aun documenta reportes exportables como pendiente.
- El cambio de color/tema no depende del backend en esta fase, tal como indica el documento.

## Pendientes

- Conectar cada pantalla con TanStack Query y servicios API reales.
- Completar Storybook y pruebas de accesibilidad con axe-core.
- Agregar drag and drop real para widgets con `dnd-kit` o `react-grid-layout`.
- Implementar proteccion real de rutas cuando el backend defina estrategia final de cookie/JWT.
- Ajustar textos acentuados cuando el repositorio adopte UTF-8 de forma consistente.

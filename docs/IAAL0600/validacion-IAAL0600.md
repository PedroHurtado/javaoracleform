# Informe de validación — IAAL0600

> Validación realizada por el agente `oracle-forms-output-validator` contra la
> fuente de verdad determinista (`extract_logic.py` y `oracle_wireframe.py` con
> sus plantillas/checklists). El agente **solo verifica corrección**; no reescribe
> archivos ni sugiere refactors.
>
> **Fecha:** 2026-07-01

## Veredicto global: ❌ RECHAZADO

6 de 10 artefactos presentan hallazgos.

## Resumen

| Artefacto | Veredicto | Hallazgos |
|-----------|-----------|-----------|
| `logica-negocio/IA_RECEP_DISPO.md` | ❌ RECHAZADO | 1 (cabeceras PL/SQL abreviadas en 2 disparadores) |
| `logica-negocio/IA_RECEP_DISPO_INDIV.md` | ❌ RECHAZADO | 1 (cabeceras PL/SQL abreviadas en 2 disparadores) |
| `logica-negocio/IA_DIST_DISPO.md` | ❌ RECHAZADO | 2 (comentario corregido silenciosamente + cabeceras abreviadas) |
| `logica-negocio/IA_DES_RECEP.md` | ✅ APROBADO | 0 |
| `logica-negocio/IA_DES_DIST.md` | ✅ APROBADO | 0 |
| `logica-negocio/IA_ANU_DIST.md` | ❌ RECHAZADO | 1 (cabeceras PL/SQL abreviadas) |
| `logica-negocio/IA_ANU_DISPO.md` | ❌ RECHAZADO | 1 (cabeceras reformateadas a línea única) |
| `logica-negocio/IA_DES_ANUL_RECI.md` | ✅ APROBADO | 0 |
| `logica-negocio/IA_DES_ANUL_DIST.md` | ✅ APROBADO | 0 |
| `IAAL0600/wireframe.html` | ❌ RECHAZADO | 1 (2 referencias externas a Google Fonts) |

---

## Lógica de negocio (`docs/logica-negocio/`)

### ❌ IA_RECEP_DISPO.md — RECHAZADO

- **PL/SQL no verbatim:** los cuerpos de los disparadores `WHEN-NEW-BLOCK-INSTANCE`
  y `WHEN-NEW-ITEM-INSTANCE` tienen las cabeceras de comentario abreviadas
  respecto al `body` del JSON. El fuente (líneas 3595 y 3621) incluye las
  secciones completas `* Modificaciones`, `* -------------- `, `*` (línea vacía),
  tabla `* Proyecto...Autor...Fecha...Comentarios`, separador `* --...`, datos
  `* RIIA  MEGG  09/03/2006...`, y línea vacía `*` final antes del cierre
  `***...*/`. El `.md` suprime todas esas líneas y muestra solo la fila de datos
  directamente tras la primera línea de funcionalidad (líneas 74-76 del `.md`
  vs. cuerpo completo en el JSON).

### ❌ IA_RECEP_DISPO_INDIV.md — RECHAZADO

- **PL/SQL no verbatim:** los disparadores `WHEN-NEW-BLOCK-INSTANCE` y
  `WHEN-NEW-ITEM-INSTANCE` presentan la misma abreviación de cabecera que el caso
  anterior (líneas 52-55 y 63-68 del `.md` omiten las secciones `* Modificaciones`
  y sus separadores presentes en el JSON para las líneas 5367 y 5394 del fuente).

### ❌ IA_DIST_DISPO.md — RECHAZADO

- **PL/SQL no verbatim (`WHEN-NEW-ITEM-INSTANCE`, línea 56 del `.md`):** el
  comentario dice `-- Establecer el estado de los botones de la botonera.` pero el
  fuente devuelve `-- Esablecer el estado de los botones de la bonotnera.` (dos
  erratas tipográficas en el original: "Esablecer" y "bonotnera"). El `.md`
  corrige silenciosamente el texto en lugar de reproducirlo verbatim.
- **PL/SQL no verbatim (`KEY-LISTVAL`, líneas 65-71 del `.md`):** la cabecera del
  bloque de código omite las líneas `* Modificaciones`, `* -------------- `, `*`
  (vacío), separadores y fila de datos de la tabla de modificaciones. El JSON
  tiene 14 líneas de cabecera; el `.md` tiene 5.
- **Misma abreviación** en los `WHEN-VALIDATE-ITEM` de `TXT_DIS_DESDE` (líneas
  115-120) y `TXT_DIS_HASTA` (líneas 130-135): el `.md` omite `* Modificaciones`
  y sus separadores presentes en el fuente (líneas 7281 y 7582).

### ✅ IA_DES_RECEP.md — APROBADO

- Recuento: 6 disparadores en `--list`, 6 subapartados en el `.md`. Cuadra.
- PL/SQL verbatim: cabeceras completas (incluyendo `* Modificaciones`,
  separadores y `*` en blanco).
- Paquetes reflejados: `IA_DES_RECEP_PKG.P_DES_IDEN_DESDE`, `P_DES_IDEN_HASTA` en
  la tabla. Advertencia de paquete externo presente.
- Estructura obligatoria completa. Sin fuga de UI.

### ✅ IA_DES_DIST.md — APROBADO

- Recuento: 6 disparadores, 6 subapartados. Cuadra.
- PL/SQL verbatim: cabeceras completas.
- Paquetes reflejados. Advertencia de paquete externo presente.
- Estructura obligatoria completa. Sin fuga de UI.

### ❌ IA_ANU_DIST.md — RECHAZADO

- **PL/SQL no verbatim (`KEY-LISTVAL`, líneas 38-44 del `.md`):** la cabecera tiene
  `* Proyecto`, `* RIIA   MEGG   14/03/2006   Desarrollo inicial` pero omite las
  líneas `* Modificaciones`, `* -------------- `, `*` (vacía antes y después del
  bloque de modificaciones) que sí están en el JSON (línea 10325 del fuente). Se
  suprimen 4 líneas interiores del bloque de cabecera.
- La misma omisión se repite en los `WHEN-VALIDATE-ITEM` de `TXT_DIS_DESDE`
  (líneas 85-91) y `TXT_DIS_HASTA` (líneas 99-105): faltan las líneas
  `* Modificaciones`, `* -------------- `, `*` en blanco presentes en el JSON.

### ❌ IA_ANU_DISPO.md — RECHAZADO

- **PL/SQL no verbatim (`KEY-LISTVAL`, líneas 61-65 del `.md`):** la cabecera
  completa del fuente (14 líneas) queda reducida a una sola línea
  `* Proyecto RIIA - MEGG - 14/03/2006 - Desarrollo inicial` que fusiona y
  reformatea los campos. El JSON tiene la tabla en formato columnar
  (`Proyecto Autor Fecha Comentarios` con separadores de guiones).
- La misma fusión de líneas se repite en `WHEN-VALIDATE-ITEM` de `TXT_DIS_DESDE`
  (líneas 109-111) y `TXT_DIS_HASTA` (líneas 121-123).

### ✅ IA_DES_ANUL_RECI.md — APROBADO

- Recuento: 6 disparadores, 6 subapartados. Cuadra.
- PL/SQL verbatim: cabeceras completas con `* Modificaciones` y separadores.
- Paquetes reflejados. Advertencia de paquete externo presente.
- Estructura obligatoria completa. Sin fuga de UI.

### ✅ IA_DES_ANUL_DIST.md — APROBADO

- Recuento: 6 disparadores, 6 subapartados. Cuadra.
- PL/SQL verbatim: cabeceras completas.
- Paquetes reflejados. Advertencia de paquete externo presente.
- Estructura obligatoria completa. Sin fuga de UI.

---

## Wireframe (`docs/IAAL0600/wireframe.html`)

### ❌ RECHAZADO

- **No autocontenido:** el archivo incluye dos recursos externos de Google Fonts
  en las líneas 7-8:
  - `<link rel="preconnect" href="https://fonts.googleapis.com">`
  - `<link href="https://fonts.googleapis.com/css2?family=Kalam:wght@300;400;700&display=swap" rel="stylesheet">`

  El requisito exige CSS/JS completamente embebidos sin dependencias externas.

- **Cobertura de pantallas — completa (correcto):** el `inspect --json` reporta 10
  lienzos de Contenido con items (BOTONERA + `CV_RECEPCION`, `CV_RECEPCION_INDIV`,
  `CV_DIST_DISPO`, `CV_DES_RECEP`, `CV_DES_DIST`, `CV_ANULAR_DIST`,
  `CV_ANULAR_RECEP`, `CV_DES_ANUL_REC`, `CV_DES_ANUL_DIST`, `C_CONSULTA_ESTADOS`) y
  1 lienzo de Pestaña (`C_INF_CROTAL` con 4 páginas). El wireframe presenta
  exactamente 10 entradas de navegación correspondientes a todos los lienzos de
  contenido, más la pestaña `C_INF_CROTAL` renderizada con sus 4 páginas clicables
  (Identificación, Animal, Localizaciones, Reidentificaciones).
- **BOTONERA:** se renderiza como barra superior fija (`position:sticky; top:0`)
  con los campos de sesión y botones. Correcto.

---

## Causas raíz

1. **Lógica de negocio:** el extractor está recortando/normalizando las cabeceras
   de comentario (bloques `* Modificaciones`, tablas `Proyecto/Autor/Fecha`) en
   lugar de copiarlas byte a byte. En `IA_DIST_DISPO.md` además **corrige erratas
   del original** — un extractor verbatim debe reproducirlas tal cual.
2. **Wireframe:** la fuente *Kalam* se carga por CDN (`fonts.googleapis.com`) en
   vez de embeberse; rompe el requisito de HTML autocontenido.

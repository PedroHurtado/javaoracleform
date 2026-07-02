---
name: oracle-forms-to-business-logic
description: Extract the business logic of exported Oracle Forms (.fmb dumped to text) into one Markdown file per user-input form (data block), capturing every trigger's PL/SQL, the business rules, and the database packages each screen invokes. Use this skill whenever the user wants to extract, document, or "sacar/volcar la lógica de negocio" of an Oracle Form, get the triggers/validations of a form as markdown, understand what a Forms screen does before migrating it, or produce a per-form business-logic report from a .fmb export. Trigger on: "extrae la lógica de negocio", "documenta los disparadores", "qué hace cada formulario", "un markdown por formulario", analysis of Forms triggers/validations/package calls. NOT for building the Java domain model (that is oracle-forms-to-ddd) nor for reconstructing the UI (that is oracle-forms-to-wireframe).
---

# Oracle Forms → Lógica de negocio (extracción por formulario)

Antes de escribir una sola línea de Java conviene **entender y documentar qué
hace cada pantalla** de un Oracle Form: sus disparadores, sus validaciones y las
llamadas que hace a la base de datos. Este skill produce, a partir de un `.fmb`
exportado a texto, **un archivo Markdown por formulario de entrada de usuario**
(bloque de datos) con toda su lógica de negocio, de forma trazable y homogénea.

Es una fase de **análisis** (no genera código Java). Su salida alimenta después a
`oracle-forms-to-ddd` (dominio) y a las fases Service/Repository/Controller: el
Markdown es la especificación legible de lo que esas capas deben reproducir.

## Cuándo usar este skill

- "Extrae / documenta la lógica de negocio de este Form."
- "Saca los disparadores y validaciones de cada formulario a markdown."
- "¿Qué hace cada pantalla de este `.fmb`?" antes de migrar.
- "Un `.md` por formulario con su PL/SQL y sus llamadas a paquetes."
- Cualquier análisis de comportamiento (triggers, reglas, paquetes) de un Form,
  como paso previo a la migración por capas.

Si el usuario pide el **modelo de dominio / entidades** usa `oracle-forms-to-ddd`;
si pide **ver la UI / un wireframe** usa `oracle-forms-to-wireframe`. Este skill
es el del **comportamiento**.

## Entrada esperada

La exportación en texto de un `.fmb` (volcado de propiedades, normalmente en
español y codificación ISO-8859-1/Latin-1), con secciones `Bloques de Datos`,
`Disparadores`, `Unidades de Programa`, etc. Un mismo módulo Form contiene varios
bloques; cada bloque de entrada de usuario es un "formulario" a documentar.

## Workflow

### Paso 1 — Inventariar bloques y disparadores (determinista)

No intentes leer 30.000 líneas a ojo. Ejecuta el extractor, que maneja la
codificación Latin-1 y captura cada disparador con su cuerpo PL/SQL:

```bash
python3 scripts/extract_logic.py <form.txt> --list        # resumen: 1 línea por bloque
python3 scripts/extract_logic.py <form.txt> --block NAME   # informe de un bloque
python3 scripts/extract_logic.py <form.txt> --json         # JSON completo (todos)
python3 scripts/extract_logic.py <form.txt> --block NAME --json
```

El modo `--list` da, por bloque: si es de BD (`Sí`/`No`), el **nº de disparadores**,
el **rango de líneas** y los **paquetes** que invoca. Úsalo como radiografía y
como control de completitud (el nº de disparadores documentados debe cuadrar con
la columna `DISP`).

### Paso 2 — Clasificar y proponer el alcance (validación humana)

De todos los bloques, distingue los **formularios de entrada de usuario** (los
que tienen lógica de negocio real) de los auxiliares:

- **Formularios de entrada** — bloques con disparadores de interacción
  (WHEN-BUTTON-PRESSED, WHEN-VALIDATE-ITEM, WHEN-LIST-CHANGED…) y/o llamadas a
  paquetes `IA_*_PKG`. Suelen ser bloques **de control** (`BD=No`) que orquestan
  una operación (recibir, distribuir, anular, deshacer). Estos SÍ se documentan.
- **Auxiliares / de consulta / control técnico** — bloques sin disparadores, de
  navegación (p. ej. `ENTRAR`), o de pura consulta/soporte. Normalmente NO son
  "formularios de entrada"; se listan pero no se documentan salvo que el usuario
  lo pida.

Presenta al usuario la **lista de formularios candidatos** (nombre, propósito
inferido, nº de disparadores, paquetes) y **pídele que confirme el alcance**
antes de generar nada. Esta validación es deliberada: el usuario decide si quiere
solo los funcionales o también los auxiliares. No la omitas.

### Paso 3 — Generar un Markdown por formulario

Lee `references/markdown-template.md` y genera, para **cada** bloque aprobado, un
archivo `docs/logica-negocio/<NOMBRE_BLOQUE>.md` siguiendo esa plantilla exacta:
propósito, items de entrada, disparadores con su **PL/SQL íntegro**, validaciones
de negocio en prosa, tabla de llamadas a paquetes/procedimientos, y notas de
migración a capas Java.

Reglas clave (ver checklist en la referencia):
- Copia el PL/SQL **verbatim** desde la salida del script; no lo reescribas ni lo
  traduzcas. Corrige acentos solo en la prosa que redactas tú.
- Documenta **todos** los disparadores (nivel bloque + nivel item); cuadra el
  recuento con `--list`.
- Recoge cada `PKG.PROC` y cada `:OTRO_BLOQUE.ITEM` (el JSON los agrega en
  `packages`/`fields`). Una referencia a un item de **otro** bloque es una
  dependencia entre pantallas o un posible bug: anótala.
- Cuando el bloque delegue en un `IA_*_PKG`, **advierte** de que el cuerpo del
  paquete no está en el `.fmb` y hay que recuperarlo de la BD para migrarlo con
  fidelidad.

**Procesamiento por lotes:** cuando haya varios formularios, la extracción de
cada uno es independiente. Puedes lanzar **un subagente por formulario en
paralelo** (Agent tool, `general-purpose`), pasándole el nombre del bloque, su
rango de líneas (de `--list`) y la plantilla, para que cada agente escriba su
`.md`. Instruye a cada agente a devolver solo un resumen corto, no el markdown.

### Paso 4 — Verificar y entregar

Comprueba que existen todos los `.md` esperados y que su nº de disparadores
cuadra con el inventario. Entrega al usuario una tabla resumen (formulario →
archivo, nº de disparadores, paquete) y resalta los **hallazgos transversales**:
lógica que vive en paquetes fuera del `.fmb`, referencias cruzadas entre bloques,
y posibles bugs heredados. Estos son el mayor valor del análisis para las fases
siguientes.

## Qué NO hace este skill

- No genera Java (ni modelo, ni Service, ni Repository, ni Bean). Es análisis.
- No documenta la UI/estética (colores, coordenadas, fuentes) → eso es
  `oracle-forms-to-wireframe`.
- No recupera el cuerpo de los paquetes de BD: solo detecta y señala las
  llamadas. Recuperar esos cuerpos es un paso aparte, contra la base de datos.

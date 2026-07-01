---
name: oracle-forms-to-wireframe
description: Reconstruye la interfaz de un Oracle Form exportado a texto (.fmb volcado) como un wireframe HTML interactivo autocontenido, para VER las pantallas y valorar la viabilidad del traspaso. Usa este skill cuando el usuario quiera generar un wireframe, previsualizar/visualizar/maquetar la UI de un formulario, reconstruir sus pantallas, ver "cómo se ve" un .fmb, obtener un mockup navegable, o probar cómo quedaría la pantalla antes de migrar. Trigger en: "genera un wireframe", "reconstruye el formulario", "visualiza la pantalla del form", "quiero ver la UI del .fmb", "maqueta interactiva del formulario". NO es para extraer el modelo de dominio ni generar capas Java (eso es otro skill).
---

# Oracle Forms → Wireframe HTML interactivo

Reconstruye la **pantalla** de un Oracle Form exportado a texto como un único
fichero HTML interactivo, sin dependencias, que se abre en el navegador. Sirve
para **ver** el formulario (ventanas, campos, marcos, pestañas, botonera) y así
juzgar si el traspaso a la nueva pila es viable y por dónde conviene atacarlo.

El proceso es determinista: un script parsea la geometría real de la UI (posición
X/Y, tamaño, tipo de elemento, prompt, lienzo, pestaña) y emite el HTML. No
inventa la disposición: la deriva de las coordenadas del propio Form.

## Cuándo usar este skill

- "Genera el wireframe de este formulario", "reconstruye la UI del `.fmb`".
- "Quiero ver cómo se ve la pantalla", "haz una maqueta interactiva del form".
- "Previsualiza/visualiza el formulario antes de migrar."
- Análisis de viabilidad: comparar aproximaciones de migración viendo la pantalla
  original reconstruida.

Este skill produce **solo la vista** (HTML). No decide capas Java ni modelo de
dominio; para eso está `oracle-forms-to-ddd`.

## Entrada esperada

Un fichero de texto que es la **exportación de un `.fmb`** (volcado de
propiedades, normalmente en español y codificación ISO-8859-1/Latin-1). El script
maneja la codificación y la indentación irregular del export.

## Workflow

### Paso 1 — Inventariar la UI (determinista)

Comprueba qué contiene el formulario antes de generar nada:

```bash
python3 scripts/oracle_wireframe.py inspect <ruta_al_form.txt>
python3 scripts/oracle_wireframe.py inspect <ruta_al_form.txt> --json   # para procesar
```

El informe lista, por lienzo: su **tipo** (Contenido / Barra de Herramientas /
Pestaña), la **ventana** a la que pertenece, cuántos **items** tiene, y sus
**pestañas** y **marcos**. Con esto confirmas que el parseo ha capturado todas
las pantallas y detectas casos especiales (lienzos apilados, lienzos sin items,
pestañas anidadas).

### Paso 2 — Generar el wireframe

```bash
python3 scripts/oracle_wireframe.py build <ruta_al_form.txt> -o <NOMBRE>/wireframe.html
```

Convención de salida: una **subcarpeta con el nombre del formulario** y dentro un
`wireframe.html`. Si se omite `-o`, el script escribe
`<dir_del_form>/<NOMBRE>_wireframe.html`.

El HTML generado incluye:
- **Barra de herramientas común** (el lienzo tipo *Barra de Herramientas*):
  campos de sesión + botones; al pulsarlos muestra su acción.
- **Navegación lateral** con una pantalla por lienzo de contenido, agrupada por
  ventana.
- Cada pantalla con sus campos reales, agrupados en los **marcos** del Form
  (posición → contención geométrica), y con el **widget** correcto por tipo de
  item (lista, texto, fecha, casilla, radio, solo lectura, imagen, botón).
- **Pestañas clicables** para los lienzos de tipo *Pestaña*.
- **Rejillas** para los bloques multi-registro (`Número de Elementos
  Visualizados > 1`).

### Paso 3 — Revisar en el navegador

Abre el `.html` y navega. Comprueba que:
- Aparecen todas las ventanas/pantallas que esperabas (contrasta con el `inspect`).
- Los campos caen en el marco correcto y las pestañas cambian.
- Los multi-registro se ven como tabla.

El mapeo de tipos de item a widgets y la lógica de agrupación por marcos están en
`references/layout-and-widgets.md`. Consúltala si necesitas **afinar** un caso
(p. ej. un tipo de elemento poco común, un lienzo apilado que solapa a otro, o un
campo que debería ser fecha y sale como texto). Ajusta el heurístico en el script
y regenera; no edites el HTML a mano.

## Procesamiento por lotes (N formularios)

Ejecuta el `build` sobre cada `.txt`. Cada formulario genera su propia subcarpeta
`<NOMBRE>/wireframe.html`, independiente y autocontenida. Usa `inspect` primero
sobre cada uno para detectar formularios con estructuras que el heurístico no
cubra todavía y decidir si vale la pena ajustar el script antes de la tanda.

## Límites conocidos

- Reconstruye **disposición**, no píxel exacto: las coordenadas del Form se
  traducen a filas/columnas relativas, no a un lienzo absoluto.
- Los **datos** mostrados son de ejemplo (placeholders); el objetivo es la
  estructura y el comportamiento de la pantalla, no datos reales.
- No ejecuta triggers ni lógica: los botones solo muestran su nombre/acción.
- Lienzos **apilados** que se solapan en el Form se presentan como pantallas
  independientes en la navegación.

# Referencia: estructura del export, widgets y agrupación

Guía para entender y **afinar** `scripts/oracle_wireframe.py`. El script es la
fuente de verdad; ajústalo aquí y regenera, no edites el HTML.

## Estructura del export que se aprovecha

El `.fmb` volcado es un árbol de propiedades indentado. Cada propiedad es
`<sangría><marca> <Etiqueta><espacios><Valor>` (marca ∈ `* - ^ o`). Las etiquetas
están en español y con acentos (Latin-1). Piezas relevantes para la UI:

| Objeto            | Dónde / cómo se detecta |
|-------------------|-------------------------|
| Item de pantalla  | Registro con `Tipo de Elemento`. Indent 5 bajo un bloque. |
| Geometría de item | `Posición X`, `Posición Y`, `Ancho`, `Altura`. |
| Etiqueta de item  | `Prompt` (si vacío, se usa el `Nombre`). |
| Lienzo del item   | `Lienzo`. |
| Pestaña del item  | `Página con Pestaña` (nombre de la página). |
| Multi-registro    | `Número de Elementos Visualizados` > 1. |
| Visibilidad       | `Visible` (los `No` se descartan). |
| Lienzo            | Sección `Lienzos`; registro indent 3 con `Tipo de Lienzo`, `Ventana`. |
| Marco (frame)     | `Tipo de Gráficos = Marco` + `Título del Marco` + geometría, dentro del lienzo. |
| Pestañas          | `Páginas con Pestaña` → registros con `Etiqueta` (rótulo visible). |
| Ventana           | Sección `Ventanas`; registro indent 3 con `Título`. |

Notas de parseo:
- Los **triggers dentro de un item** también empiezan por `* Nombre` en indent 5,
  pero no tienen `Tipo de Elemento`; por eso se descartan (se toma solo el primer
  valor de cada propiedad geométrica del item, antes de sus disparadores).
- Los **objetos gráficos** de un lienzo (Marco, Rectángulo, Texto) usan `Tipo de
  Gráficos`, no `Tipo de Elemento`: nunca se confunden con items.
- La lectura es UTF-8 con *fallback* Latin-1; la salida HTML es UTF-8.

## Tipo de elemento → widget

En `widget_family()`:

| `Tipo de Elemento` (Form)        | Familia   | Render HTML |
|----------------------------------|-----------|-------------|
| Botón                            | `button`  | `<button>` (toolbar o en pantalla) |
| Casilla de Control               | `check`   | `<input type=checkbox>` + etiqueta |
| Grupo de Botones de Radio        | `radio`   | etiqueta + marcador `○ ○` |
| Elemento de Lista / Lista        | `list`    | `<select>` |
| Visualizar Elemento              | `display` | caja de solo lectura |
| Imagen                           | `image`   | placeholder `IMG` |
| Elemento de Texto (y por defecto)| `text`    | `<input type=text>` |

Un `text` se muestra como **fecha** (`dd/mm/aaaa`) si el prompt o el nombre
sugieren fecha (`fecha`, empieza por `f.`, contiene `f_`). Para afinar por
`Tipo de Dato = Date`, captura ese campo en `parse_items` y úsalo en
`render_field`.

## Agrupación por marcos y filas

- **Marco de un item** (`frame_of`): el marco de menor área cuyo rectángulo
  contiene la posición del item (con pequeña tolerancia). Los items fuera de todo
  marco van a un grupo por defecto.
- **Filas** (`rows_of`): dentro de un grupo, los items se ordenan por `(Y, X)` y
  se parten en filas cuando el salto vertical supera `ROW_TOL` (6). Sube/baja
  `ROW_TOL` si las filas salen demasiado juntas o demasiado separadas.
- **Pestañas**: en lienzos de tipo *Pestaña*, los items se reparten por su
  `Página con Pestaña`; cada página se agrupa con los marcos asignados a ella.
- **Multi-registro**: los items con `disp > 1` de un mismo grupo se pintan como
  una tabla (columnas = esos items ordenados por X, cabecera = su prompt), con
  varias filas de celdas vacías.

## Pantallas y navegación

- El lienzo tipo *Barra de Herramientas* se renderiza como barra superior común
  (campos de sesión + botones).
- Cada lienzo de contenido/pestaña **con al menos un item** es una pantalla; la
  navegación lateral las agrupa por **ventana** (`Título` de la ventana).
- El rótulo de cada entrada de navegación usa el título del primer marco del
  lienzo si existe; si no, el nombre del lienzo.

## Casos a vigilar al afinar

- **Lienzos apilados** (`Tipo de Lienzo = Apilado`) que solapan a un lienzo de
  contenido: aquí aparecen como pantallas separadas. Si conviene mostrarlos
  superpuestos, hay que fusionarlos por ventana.
- **Tipos de elemento nuevos** no contemplados en `widget_family`: caen a `text`
  por defecto; añade la rama correspondiente.
- **Marcos anidados**: `frame_of` elige el de menor área, lo que resuelve el
  anidamiento habitual; si un marco decorativo captura items que no le
  corresponden, revísalo por geometría.

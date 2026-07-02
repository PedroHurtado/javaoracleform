# Plantilla y checklist del Markdown de lógica de negocio

Cada formulario de entrada de usuario se documenta en **un archivo Markdown
propio** (`docs/logica-negocio/<NOMBRE_BLOQUE>.md`). Todos los archivos siguen la
misma estructura para que un lote de N formularios quede homogéneo.

## Estructura obligatoria

```markdown
# Formulario: <NOMBRE_BLOQUE>

## Propósito
Una o dos frases: qué acción de negocio representa la pantalla (recibir,
distribuir, anular, deshacer…) y sobre qué entidad opera. Deriva el propósito
del título del Form, del nombre del bloque y de la funcionalidad declarada en las
cabeceras `/* Funcionalidad: ... */` de los disparadores.

## Items / campos de entrada relevantes
Tabla de los campos con los que interactúa el usuario y que participan en la
lógica (no listes campos puramente decorativos):

| Item | Tipo | Descripción / papel en la lógica |
|------|------|----------------------------------|
| LST_ESPECIES | Lista | Especie; condiciona los tipos de dispositivo y la comunidad |
| TXT_DIS_DESDE | Texto | Nº de dispositivo inicial del rango |
| ... | | |

## Disparadores (lógica de negocio)
Un subapartado por disparador, en el orden en que los emite el extractor. Indica
nombre del disparador, item/nivel al que pertenece, una frase de qué hace, y el
**PL/SQL íntegro** en un bloque de código:

### WHEN-VALIDATE-ITEM — TXT_DIS_DESDE
Valida el nº inicial del rango y compone el identificador electrónico.

​```sql
-- (pegar aquí el cuerpo tal cual lo devuelve extract_logic.py, sin reescribirlo)
​```

## Validaciones de negocio
Lista en prosa de las REGLAS extraídas de los disparadores (no el código):
- Exclusión mutua fabricante/proveedor (solo uno de los dos).
- Fecha de recepción no puede ser futura.
- Identificador = comunidad || LPAD(nº_dispositivo, 10, '0').
- ...

## Llamadas a paquetes / procedimientos de BD
Tabla de las llamadas que salen del Form hacia la base de datos (materia prima de
la futura capa Service):

| Llamada | Parámetros | Propósito inferido |
|---------|-----------|--------------------|
| IA_RECEPCION_ID_PKG.P_VALIDAR_IDENT_RECEP | (desde, hasta, especie) | Valida el rango |
| ... | | |

> Nota: el **cuerpo** de estos paquetes normalmente NO está en el `.fmb`
> exportado (solo la llamada). Para migrar la lógica con fidelidad habrá que
> recuperar el código del paquete desde la base de datos. Señálalo explícitamente.

## Notas para la migración a Java
Mapea la lógica a las capas del proyecto (ver CLAUDE.md):
- **Controller/Bean** (`bean`): disparadores de UI, navegación, habilitar/deshabilitar
  botones, mostrar alertas.
- **Service** (`service`): validaciones de negocio y lo que hoy hacen los paquetes
  `IA_*_PKG`.
- **Repository** (`repository`): consultas embebidas / acceso a datos.
- **Model** (`model`): entidades implicadas (enlaza con el modelo de `oracle-forms-to-ddd`).
Anota aquí también cualquier **anomalía** detectada (referencias a items de otro
bloque, posibles bugs de nombre, código muerto comentado).
```

## Checklist de extracción (qué NO dejarse)

- [ ] **Todos** los disparadores del bloque (nivel bloque + nivel item). Usa el
      recuento de `extract_logic.py --list` como control: el nº de subapartados
      debe cuadrar con la columna `DISP`.
- [ ] El PL/SQL se copia **verbatim** (con sus comentarios de cabecera); no se
      traduce ni se "arregla". Los acentos rotos del volcado se corrigen solo en
      la prosa que escribes tú, nunca dentro del bloque de código fuente.
- [ ] Cada llamada `PKG.PROC` y `:OTRO_BLOQUE.ITEM` que aparezca en los cuerpos
      (el script las agrega en `packages`/`fields`). Una referencia a un item de
      **otro** bloque suele ser una dependencia entre pantallas o un bug: anótala.
- [ ] Las reglas de negocio en prosa, separadas del código, para que la fase
      Service tenga una especificación legible.
- [ ] La advertencia de "cuerpo del paquete fuera del `.fmb`" cuando el bloque
      delega en un `IA_*_PKG`.

## Reglas de estilo

- Idioma: español (es la lengua del dominio y del Form).
- Nombre de archivo = nombre del bloque en mayúsculas, tal cual en el Form.
- No incluyas propiedades visuales (colores, fuentes, coordenadas): esas son del
  skill `oracle-forms-to-wireframe`, no de este.
- Un archivo por formulario; no mezcles dos bloques en el mismo `.md`.

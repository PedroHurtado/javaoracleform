---
name: oracle-forms-to-ddd
description: Transpose exported Oracle Forms (.fmb dumped to text) into a pure Java domain model using Domain-Driven Design. Use this skill whenever the user wants to migrate, modernize, convert, or "pasar/transponer" Oracle Forms to Java, extract entities from a .fmb file, or build a DDD domain model (aggregates, entities, value objects) from a legacy Forms application — even if they only say "extract the entities", "model the domain", or mention a form file like IAALxxxx. Trigger on Oracle Forms migration, .fmb analysis, legacy-to-Java modernization, DDD layering of a form, or batch conversion of many forms.
---

# Oracle Forms → Java DDD (Fase de extracción de dominio)

Migrar una aplicación Oracle Forms a Java por capas (Controller/Bean, Service,
Entity, Repository) empieza por **extraer el modelo de dominio**. Este skill
automatiza la Fase 1: leer un formulario exportado y producir un modelo DDD
puro (agregados, entidades, value objects) en Java, validado por compilación.

El proceso replica un análisis manual fiable: parsear la estructura del Form con
un script determinista, clasificar cada bloque/columna según heurísticas DDD, y
emitir código Java limpio con trazabilidad al formulario original.

## Cuándo usar este skill

- "Pasa este Oracle Form a Java", "migra el formulario a DDD".
- "Extrae las entidades del .fmb", "modela el dominio de este form".
- "Tengo N formularios que convertir a Java" (procesamiento por lotes).
- Cualquier mención de modernizar Forms, analizar un `.fmb`, o separar un
  formulario en capas Controller/Service/Entity/Repository.

## Entrada esperada

Un fichero de texto que es la **exportación de un `.fmb`** (un volcado de
propiedades, normalmente en español y codificación ISO-8859-1/Latin-1). Contiene
secciones como `Bloques de Datos`, `Disparadores`, `Unidades de Programa`,
`Listas de Valores`, etc. Si el usuario tiene el `.fmb` binario, necesita
exportarlo a texto primero (Forms `convert` o la utilidad equivalente).

## Workflow

### Paso 1 — Inventariar la estructura (determinista)

Ejecuta el extractor sobre el formulario. Produce el inventario fiable de
bloques, columnas, orígenes de datos y unidades de programa. No improvises este
parseo a mano: el script maneja la codificación Latin-1 y las indentaciones
irregulares del export.

```bash
python3 scripts/extract_form.py <ruta_al_form.txt>          # informe legible
python3 scripts/extract_form.py <ruta_al_form.txt> --json   # JSON para procesar
```

Lee el informe e identifica:
- **Bloques de datos de BD** (`is_db_block = Sí`) → candidatos a Entidad/Agregado.
- Su **origen de consulta** (tabla o SELECT) y **destino DML** (tabla).
- Las **tablas de los SELECT embebidos** → revelan relaciones (claves foráneas).
- **Bloques de control** (`is_db_block = No`) → NO son dominio (van a Controller/Vista).
- **Unidades de Programa / Paquetes** (`IA_*_PKG`, procedimientos) → lógica que
  en la migración irá al Service; aquí solo sirven para inferir el
  **comportamiento de dominio** (recibir, distribuir, anular…).

### Paso 2 — Clasificar en DDD

Lee `references/ddd-classification.md` y aplica las heurísticas para decidir,
bloque a bloque y columna a columna:

- **Aggregate Root**: bloque con identidad propia, `dml_target`, referenciado
  desde otros bloques, con ciclo de vida.
- **Entity** (no raíz): bloque/detalle con identidad pero dependiente de su raíz.
- **Value Object**: grupos de columnas sin identidad (códigos compuestos, rangos,
  importes), estados/tipos cerrados (`enum`), y claves foráneas a tablas que el
  Form no edita (`XxxRef`, value object de referencia).
- Descarta del dominio los bloques de control y los items `db_item = No` de pura
  pantalla.

Mantén los agregados pequeños; ante la duda, haz una entidad raíz propia y
referénciala por id en vez de anidarla.

Presenta al usuario un resumen de la clasificación propuesta y señala las
**decisiones de frontera de agregado** dudosas (p. ej. una entidad de consulta
que podría ser raíz propia o mera referencia) para que las confirme. No las
ocultes: son el punto donde el juicio humano aporta más.

### Paso 3 — Generar el modelo Java

Lee `references/java-conventions.md` y escribe el modelo siguiendo esas reglas.
Por defecto: **un único archivo** `.java`, clases con visibilidad de paquete
(sin `public`), **sin `main` ni runtime**, secciones ordenadas (Aggregate Roots
→ Entities → Value Objects → Identificadores), comportamiento de dominio con
nombres del negocio, y un comentario de **trazabilidad** en cada clase indicando
el bloque/tabla de origen.

Recuerda: los identificadores Java deben ser ASCII (usa `anadir`, no `añadir`);
los comentarios pueden llevar acentos.

### Paso 4 — Validar por compilación

El modelo se valida compilando (no ejecutando). Sigue la sección de validación
de `references/java-conventions.md`:

```bash
JDK=$(ls -d /usr/lib/jvm/java-*-openjdk-* 2>/dev/null | head -1)
"$JDK/bin/java" -m jdk.compiler/com.sun.tools.javac.Main -Xlint:all <archivo>.java
rm -f *.class
```

Compilación **sin errores ni warnings** = modelo válido. Si falla, corrige y
recompila antes de entregar. No dejes ficheros `.class` en la salida.

### Paso 5 — Entregar

Entrega el `.java` al usuario. Acompáñalo de un resumen breve: qué agregados,
entidades y value objects se han extraído, y las decisiones de frontera abiertas
que conviene revisar.

## Procesamiento por lotes (N formularios)

Cuando haya varios formularios, procesa cada uno con el mismo workflow. Para
mantener consistencia entre formularios del mismo sistema:

- Reutiliza los **mismos value objects y `...Ref`** cuando una tabla aparece en
  varios formularios (p. ej. `ExplotacionRef`, `Crotal`): no dupliques el
  concepto con nombres distintos.
- Mantén un **glosario** de tablas → clases ya modeladas, para que la segunda y
  sucesivas conversiones referencien lo ya creado en lugar de recrearlo.
- Si los formularios comparten dominio, considera un único archivo de modelo
  compartido más los específicos de cada formulario; confírmalo con el usuario.

## Qué NO hace este skill (todavía)

Esta es solo la **Fase 1 (dominio)**. No genera repositorios, servicios,
controllers, mapeo JPA ni la UI. Esas capas son fases posteriores que parten de
este modelo de dominio ya validado. El `dml_target`/`query_source` y los
paquetes `IA_*_PKG` que el extractor ya identifica serán la materia prima de las
fases Repository y Service.

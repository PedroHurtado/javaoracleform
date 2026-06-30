# Heurísticas de clasificación DDD para bloques de Oracle Forms

Este documento guía cómo convertir el inventario que produce
`scripts/extract_form.py` en un modelo de dominio DDD. La clasificación es un
**juicio de modelado**, no una regla mecánica: usa estas heurísticas como punto
de partida y ajústalas al dominio concreto.

## Tabla de decisión rápida

| Señal en el bloque / item                                              | Clasificación probable                |
|------------------------------------------------------------------------|---------------------------------------|
| `is_db_block = Sí` + `dml_target` con tabla (insert/update/delete)      | **Aggregate Root** o **Entity**       |
| `is_db_block = Sí` + solo `query_source` (SELECT, sin DML)              | Entidad de **consulta** (a menudo Aggregate Root de solo lectura, o `...Ref`) |
| `is_db_block = No`                                                      | **NO es dominio** → capa Controller/Vista (bloque de control, botonera, filtros de pantalla) |
| Bloque maestro del que cuelgan bloques detalle (relación master-detail) | **Aggregate Root**; los detalle son **Entities** dentro de él |
| Bloque detalle que no existe sin su maestro                            | **Entity** (hija del agregado)        |
| Conjunto de columnas que forman un concepto sin identidad propia (un código compuesto, un importe+moneda, un rango de fechas) | **Value Object** embebido |
| Columna que es clave foránea a otra tabla que este Form NO edita        | **Value Object de referencia** (`XxxRef`) — no arrastres la entidad entera |
| Columna de estado/tipo con dominio cerrado de valores                   | **Value Object enum**                 |

## Cómo decidir Aggregate Root vs Entity

Una **raíz de agregado** es la frontera de consistencia: tiene identidad de
negocio propia, se referencia desde otros agregados, y controla las invariantes
de todo lo que contiene. Pistas:

- El bloque tiene `dml_target` propio (se inserta/actualiza/borra de forma independiente).
- Su identidad aparece como clave foránea en otros bloques (`*_SEQUEN`, `*_NUMREG`, `*_CODIGO`).
- Tiene un ciclo de vida y comportamiento (los packages `IA_*_PKG` actúan sobre él: recibir, distribuir, anular...).

Una **entidad no raíz** tiene identidad pero su existencia depende de la raíz:
no se consulta ni persiste aisladamente, solo a través de su agregado (una línea
de detalle, una situación, un duplicado).

**Regla práctica de fronteras:** mantén los agregados pequeños. Si dudas entre
meter una entidad dentro de un agregado o hacerla raíz propia, hazla raíz propia
y referénciala por id (`XxxRef`) salvo que necesites garantizar una invariante
transaccional entre ambas.

## Cómo detectar Value Objects

Mira los grupos de columnas dentro de un bloque:

- **Código compuesto**: varias columnas que juntas forman un identificador
  visual (p. ej. `CRO_PAIS + CRO_CCAA + CRO_SERIE + CRO_NUM`) → un VO inmutable
  con `equals`/`hashCode` por valor.
- **Estado / tipo**: columnas como `STC_CODIGO`, `RES_SEXO` con un conjunto
  finito de valores → `enum`.
- **Identificación**: un código con reglas de validación (no nulo, formato) →
  VO con validación en el constructor.
- **Referencias**: una FK + su descripción denormalizada traída por el SELECT
  (`RAZ_DESC`, `EMP_DESC`, `TPS_DESC`) → VO de referencia ligero (`id` + texto),
  no la entidad completa.

Los VO **no tienen identidad** y son **inmutables**: su igualdad es por el valor
de todos sus campos.

## Columnas que NO van al dominio

- Items con `db_item = No` que son meros campos de pantalla (filtros, totales
  calculados, descripciones traídas para mostrar) → pertenecen a la vista, no a
  la entidad. Solo modela como VO de referencia las descripciones que aporten
  significado de dominio.
- Bloques de control (`is_db_block = No`): botoneras, bloques de navegación,
  cabeceras de filtro → capa de presentación.

## Identificadores tipados

En lugar de exponer `Long`/`String` crudos como id, crea un VO de identidad por
cada raíz/entidad (`DispositivoId`, `ExplotacionId`...). Esto evita mezclar ids
de distintos conceptos y documenta el modelo.

## Trazabilidad obligatoria

Cada clase generada debe llevar un comentario que indique su **origen en el
Form**: nombre del bloque y tabla (`// Origen: bloque CROTALES_ESTADOS / tabla
IB_CROTAL`). Esto permite validar la transposición contra el formulario original
y facilita futuras revisiones.

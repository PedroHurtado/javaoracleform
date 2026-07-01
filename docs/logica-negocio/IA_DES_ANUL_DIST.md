# Formulario: IA_DES_ANUL_DIST

Bloque **Deshacer anulación de distribución** del formulario Oracle Forms `IAAL0600`.

## Propósito

Bloque de pantalla (no ligado a base de datos: *Bloque de Datos de Base de Datos = No*)
que permite **deshacer la anulación de una distribución** de dispositivos (identificadores
electrónicos). El usuario selecciona una **especie**, indica un **rango de identificadores**
(desde/hasta) y el bloque calcula/muestra el **total de dispositivos** afectados para revertir
la anulación previa.

El identificador electrónico se compone de:

- Un **componente de comunidad** (`DSP_COM_DESDE` / `DSP_COM_HASTA`, 2 caracteres) que actúa como prefijo.
- Un **número de dispositivo** (`TXT_DIS_DESDE` / `TXT_DIS_HASTA`, hasta 10 dígitos) rellenado a la
  izquierda con ceros: `LPAD(numero, 10, '0')`.

El identificador electrónico completo (`TXT_ID_ELECT_D` / `TXT_ID_ELECT_H`, 15 caracteres) se forma
por concatenación: `componente || LPAD(numero, 10, '0')`.

## Items / campos de entrada relevantes

| Item | Tipo | Datos | Descripción / Lógica |
|------|------|-------|----------------------|
| `LST_ESPECIES` | Lista desplegable | Char(50) | Selección de especie. Se carga con `CARGAR_LISTA_ESPECIE`. Al cambiar limpia el rango. |
| `DSP_COM_DESDE` | Display Item | Char(2) | Componente/prefijo de comunidad del identificador inicial. |
| `TXT_DIS_DESDE` | Texto | Char(10) | Número de dispositivo inicial. LOV `LV_DES_ANUL_DIST_D`, valida desde lista. |
| `TXT_ID_ELECT_D` | Texto | Char(15) | Identificador electrónico inicial completo (calculado por concatenación). |
| `DSP_COM_HASTA` | Display Item | Char(2) | Componente/prefijo de comunidad del identificador final. |
| `TXT_DIS_HASTA` | Texto | Char(10) | Número de dispositivo final. LOV `LV_DES_ANUL_DIST_H`, valida desde lista. |
| `TXT_ID_ELECT_H` | Texto | Char(15) | Identificador electrónico final completo (calculado por concatenación). |
| `DSP_N_DISP` | Display Item | Number(40) | Total de dispositivos (resultado, valor inicial 0, solo visualización). |

Listas de valores asociadas: `LV_DES_ANUL_DIST_D` (desde) y `LV_DES_ANUL_DIST_H` (hasta),
ambas con validación desde lista activada.

## Disparadores (lógica de negocio)

### Bloque: `WHEN-NEW-BLOCK-INSTANCE`
Carga la lista de especies al entrar en el bloque.

```sql
--Carga la lista de especies.
CARGAR_LISTA_ESPECIE('IA_DES_ANUL_DIST.LST_ESPECIES');
```

### Bloque: `WHEN-NEW-ITEM-INSTANCE`
Comportamiento estándar de navegación entre items + configuración de la botonera.

```sql
WHEN_NEW_ITEM_INSTANCE;

P_ESTABLECER_BOTONERA;
```

### Bloque: `KEY-LISTVAL`
Antes de mostrar la lista de valores, construye los identificadores electrónicos
(desde/hasta) concatenando el componente de comunidad con el número de dispositivo
rellenado a 10 dígitos, y luego invoca la LOV.

```sql
/************************************************************************************
* Funcionalidad: Validar campos que crean el identificadores y mostrar la lista de
*                valores de identicadores iniciales y finales.
*
* Modificaciones
* --------------
*
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              14/03/2006          Desarrollo inicial
*
************************************************************************************/

IF :IA_DES_ANUL_DIST.TXT_DIS_DESDE IS NULL THEN
    :IA_DES_ANUL_DIST.TXT_ID_ELECT_D := NULL;
ELSE
    :IA_DES_ANUL_DIST.TXT_ID_ELECT_D := :IA_DES_ANUL_DIST.DSP_COM_DESDE || LPAD(:IA_DES_ANUL_DIST.TXT_DIS_DESDE,10,'0');
END IF;

IF :IA_DES_ANUL_DIST.TXT_DIS_HASTA IS NULL THEN
      :IA_DES_ANUL_DIST.TXT_ID_ELECT_H := NULL;
ELSE
      :IA_DES_ANUL_DIST.TXT_ID_ELECT_H := :IA_DES_ANUL_DIST.DSP_COM_HASTA || LPAD(:IA_DES_ANUL_DIST.TXT_DIS_HASTA,10,'0');
END IF;

LIST_VALUES;
```

### Item `LST_ESPECIES`: `WHEN-LIST-CHANGED`
Al cambiar la especie seleccionada, limpia el rango de identificadores y resetea el
contador de dispositivos (fuerza a rehacer la selección para la nueva especie).

```sql
:IA_DES_ANUL_DIST.TXT_DIS_DESDE:=NULL;
:IA_DES_ANUL_DIST.DSP_COM_DESDE:=NULL;
:IA_DES_ANUL_DIST.TXT_DIS_HASTA:=NULL;
:IA_DES_ANUL_DIST.DSP_COM_HASTA:=NULL;
:IA_DES_ANUL_DIST.DSP_N_DISP:=0;
```

### Item `TXT_DIS_DESDE`: `WHEN-VALIDATE-ITEM`
Valida el identificador inicial del rango delegando en el paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
*
*
* Modificaciones
* --------------
*
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              22/03/2006          Desarrollo inicial
*
************************************************************************************/
IA_DES_ANUL_DIST_PKG.P_DES_IDEN_DESDE;
```

### Item `TXT_DIS_HASTA`: `WHEN-VALIDATE-ITEM`
Valida el identificador final del rango delegando en el paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
*
*
*
* Modificaciones
* --------------
*
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              22/03/2006          Desarrollo inicial
*
************************************************************************************/
IA_DES_ANUL_DIST_PKG.P_DES_IDEN_HASTA;
```

## Validaciones de negocio

- **Especie obligatoria de facto**: al cambiar la especie (`WHEN-LIST-CHANGED`) se limpia
  todo el rango; el flujo obliga a seleccionar especie antes de operar sobre el rango.
- **Validación del identificador inicial** (`TXT_DIS_DESDE`): se delega en
  `IA_DES_ANUL_DIST_PKG.P_DES_IDEN_DESDE`. El campo valida además contra su LOV
  `LV_DES_ANUL_DIST_D` (*Validar desde Lista = Sí*).
- **Validación del identificador final** (`TXT_DIS_HASTA`): se delega en
  `IA_DES_ANUL_DIST_PKG.P_DES_IDEN_HASTA`. Valida contra la LOV `LV_DES_ANUL_DIST_H`
  (*Validar desde Lista = Sí*).
- **Composición del identificador electrónico** (regla de formato en `KEY-LISTVAL`):
  - Si el número de dispositivo es NULL → el identificador electrónico es NULL.
  - En caso contrario → `identificador = componente_comunidad || LPAD(numero, 10, '0')`
    (número rellenado con ceros a la izquierda hasta 10 dígitos, prefijado por el componente
    de 2 caracteres; longitud total 15).
- **Coherencia del rango**: la lógica de rango desde/hasta (que el inicial no sea mayor
  que el final, existencia de dispositivos, cálculo de `DSP_N_DISP`) reside en el paquete
  `IA_DES_ANUL_DIST_PKG` (no expuesta en el .fmb).

## Llamadas a paquetes / procedimientos de BD

| Procedimiento / rutina | Parámetros | Disparador | Cometido |
|------------------------|-----------|------------|----------|
| `IA_DES_ANUL_DIST_PKG.P_DES_IDEN_DESDE` | (ninguno; usa items `:IA_DES_ANUL_DIST.*`) | `TXT_DIS_DESDE` WHEN-VALIDATE-ITEM | Valida el identificador electrónico inicial del rango. |
| `IA_DES_ANUL_DIST_PKG.P_DES_IDEN_HASTA` | (ninguno; usa items `:IA_DES_ANUL_DIST.*`) | `TXT_DIS_HASTA` WHEN-VALIDATE-ITEM | Valida el identificador electrónico final del rango. |
| `CARGAR_LISTA_ESPECIE` | `'IA_DES_ANUL_DIST.LST_ESPECIES'` (nombre del item lista a poblar) | WHEN-NEW-BLOCK-INSTANCE | Rutina común: carga los valores de la lista de especies. |
| `WHEN_NEW_ITEM_INSTANCE` | (ninguno) | WHEN-NEW-ITEM-INSTANCE | Rutina común de navegación/estado del item. |
| `P_ESTABLECER_BOTONERA` | (ninguno) | WHEN-NEW-ITEM-INSTANCE | Rutina común: habilita/deshabilita botones según contexto. |
| `LIST_VALUES` (built-in Forms) | — | KEY-LISTVAL | Muestra la lista de valores asociada al item actual. |

> Los procedimientos `P_DES_IDEN_DESDE` / `P_DES_IDEN_HASTA` no reciben parámetros formales:
> operan directamente sobre los items del bloque (`:IA_DES_ANUL_DIST.TXT_ID_ELECT_D/H`,
> `DSP_COM_*`, `LST_ESPECIES`, `DSP_N_DISP`). Su implementación (validación real y actualización
> de `DSP_N_DISP`) debe recuperarse del cuerpo del paquete `IA_DES_ANUL_DIST_PKG` en la BD.

## Notas para la migración a Java

Según las convenciones del proyecto (JSF + PrimeFaces + Spring + Hibernate, Java 11, `javax.*`):

- **Controller (`bean`)**: crear `DesAnulDistBean` (`@Component("desAnulDistBean")`,
  `@Scope("view")` o `session`, `Serializable`). Contiene los campos de entrada
  (`especie`, `disDesde`, `disHasta`, `comDesde`, `comHasta`, `idElectDesde`, `idElectHasta`,
  `nDispositivos`) y las acciones equivalentes a los disparadores:
  - `WHEN-NEW-BLOCK-INSTANCE` → `@PostConstruct` / método `init()` que carga la lista de especies.
  - `WHEN-LIST-CHANGED` → listener del `<p:selectOneMenu>` de especie que limpia el rango
    y pone `nDispositivos = 0`.
  - `KEY-LISTVAL` → la composición del identificador debe ejecutarse antes de abrir/consultar
    la LOV (o al construir el filtro de autocompletado).

- **Service (`service`)**: `DesAnulDistService` (`@Service @Transactional`) que encapsula
  la lógica hoy en `IA_DES_ANUL_DIST_PKG`:
  - `validarIdentificadorDesde(...)` ← `P_DES_IDEN_DESDE`.
  - `validarIdentificadorHasta(...)` ← `P_DES_IDEN_HASTA`.
  - Un método de negocio que calcule el total de dispositivos del rango y ejecute el
    **deshacer anulación** (la operación transaccional central, aún por localizar en el paquete).

- **Repository (`repository`)**: `@Repository` con `EntityManager` (JPQL) para consultar los
  dispositivos por especie y rango de identificador, contarlos y actualizar su estado
  (revertir la anulación).

- **Regla de formato del identificador electrónico** (portar tal cual):
  `idElect = comunidad + String.format("%010d", numeroDispositivo)` cuando el número no es nulo;
  nulo → identificador nulo. Longitud total 15 (2 + 10, holgura hasta 15).

- **LOVs** `LV_DES_ANUL_DIST_D` / `LV_DES_ANUL_DIST_H` → convertir en autocompletados
  (`<p:autoComplete>`) o diálogos de selección respaldados por consultas del repositorio;
  conservar la validación "el valor debe existir en la lista".

- **Pendiente de la BD**: obtener el cuerpo del paquete `IA_DES_ANUL_DIST_PKG` para conocer
  las reglas exactas de validación de rango, cómo se calcula `DSP_N_DISP` y la sentencia que
  efectivamente deshace la anulación (probablemente un `UPDATE` sobre la tabla de dispositivos/
  distribución filtrado por especie e intervalo de identificador).

# Formulario: IA_DES_ANUL_RECI

## Propósito

Bloque **Deshacer anulación de recepción**. Permite revertir la anulación de una
recepción previamente anulada, seleccionando un rango de dispositivos electrónicos
(identificadores inicial y final) filtrados por especie. El bloque calcula el total
de dispositivos afectados dentro del rango indicado.

- No es un bloque de base de datos (`Bloque de Datos de Base de Datos = No`); actúa
  como formulario de captura de parámetros para una operación de negocio.
- El identificador electrónico se compone de un prefijo de comunidad
  (`DSP_COM_*`) concatenado con el número de dispositivo (`TXT_DIS_*`) rellenado a
  10 dígitos con ceros a la izquierda.

## Items / campos de entrada relevantes

| Item             | Tipo            | Tipo dato | Long. | LOV                  | Notas |
|------------------|-----------------|-----------|-------|----------------------|-------|
| `LST_ESPECIES`   | Lista desplegable | Char    | 50    | —                    | Filtro por especie; se carga con `CARGAR_LISTA_ESPECIE`. Al cambiar limpia el rango. |
| `DSP_COM_DESDE`  | Visualizar Elem. | Char     | 2     | —                    | Prefijo de comunidad del identificador inicial (calculado). |
| `TXT_DIS_DESDE`  | Texto (entrada) | Char      | 10    | `LV_DES_ANUL_RECI_D` | Nº de dispositivo inicial. Validar desde lista = Sí. |
| `TXT_ID_ELECT_D` | Texto           | Char      | 15    | —                    | Identificador electrónico inicial (calculado): `DSP_COM_DESDE || LPAD(TXT_DIS_DESDE,10,'0')`. |
| `DSP_COM_HASTA`  | Visualizar Elem. | Char     | 2     | —                    | Prefijo de comunidad del identificador final (calculado). |
| `TXT_DIS_HASTA`  | Texto (entrada) | Char      | 10    | `LV_DES_ANUL_RECI_H` | Nº de dispositivo final. Validar desde lista = Sí. |
| `TXT_ID_ELECT_H` | Texto           | Char      | 15    | —                    | Identificador electrónico final (calculado): `DSP_COM_HASTA || LPAD(TXT_DIS_HASTA,10,'0')`. |
| `DSP_N_DISP`     | Visualizar Elem. | Number   | 40    | —                    | Total de dispositivos en el rango. Valor inicial 0. |

## Disparadores (lógica de negocio)

### Bloque `IA_DES_ANUL_RECI`

**WHEN-NEW-BLOCK-INSTANCE** — Carga la lista desplegable de especies al entrar al bloque.

```sql
--Carga la lista de especies.
CARGAR_LISTA_ESPECIE('IA_DES_ANUL_RECI.LST_ESPECIES');
```

**WHEN-NEW-ITEM-INSTANCE** — Refresca estado general y la botonera al cambiar de item.

```sql
WHEN_NEW_ITEM_INSTANCE;

P_ESTABLECER_BOTONERA;
```

**KEY-LISTVAL** — Antes de mostrar la lista de valores, recalcula los identificadores
electrónicos inicial y final a partir del prefijo de comunidad y el número de
dispositivo, y luego invoca la LOV.

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

IF :IA_DES_ANUL_RECI.TXT_DIS_DESDE IS NULL THEN
    :IA_DES_ANUL_RECI.TXT_ID_ELECT_D := NULL;
ELSE
    :IA_DES_ANUL_RECI.TXT_ID_ELECT_D := :IA_DES_ANUL_RECI.DSP_COM_DESDE || LPAD(:IA_DES_ANUL_RECI.TXT_DIS_DESDE,10,'0');
END IF;

IF :IA_DES_ANUL_RECI.TXT_DIS_HASTA IS NULL THEN
    :IA_DES_ANUL_RECI.TXT_ID_ELECT_H := NULL;
ELSE
    :IA_DES_ANUL_RECI.TXT_ID_ELECT_H := :IA_DES_ANUL_RECI.DSP_COM_HASTA || LPAD(:IA_DES_ANUL_RECI.TXT_DIS_HASTA,10,'0');
END IF;

LIST_VALUES;
```

### Item `LST_ESPECIES`

**WHEN-LIST-CHANGED** — Al cambiar la especie seleccionada, limpia todo el rango de
identificadores y reinicia el contador de dispositivos.

```sql
:IA_DES_ANUL_RECI.TXT_DIS_DESDE:=NULL;
:IA_DES_ANUL_RECI.DSP_COM_DESDE:=NULL;
:IA_DES_ANUL_RECI.TXT_DIS_HASTA:=NULL;
:IA_DES_ANUL_RECI.DSP_COM_HASTA:=NULL;
:IA_DES_ANUL_RECI.DSP_N_DISP:=0;
```

### Item `TXT_DIS_DESDE`

**WHEN-VALIDATE-ITEM** — Valida el rango del identificador inicial mediante el paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
*
* Modificaciones
* --------------
*
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              14/03/2006          Desarrollo inicial
*
************************************************************************************/
IA_DES_ANUL_RECI_PKG.P_DES_IDEN_DESDE;
```

### Item `TXT_DIS_HASTA`

**WHEN-VALIDATE-ITEM** — Valida el rango del identificador final mediante el paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
*
* Modificaciones
* --------------
*
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              14/03/2006          Desarrollo inicial
*
************************************************************************************/
IA_DES_ANUL_RECI_PKG.P_DES_IDEN_HASTA;
```

## Validaciones de negocio

- **Especie obligatoria como filtro previo**: al cambiar `LST_ESPECIES` se limpia
  todo el rango (`TXT_DIS_DESDE/HASTA`, `DSP_COM_DESDE/HASTA`) y se reinicia
  `DSP_N_DISP` a 0, forzando a reintroducir el rango coherente con la nueva especie.
- **Composición del identificador electrónico**: el identificador es
  `prefijo_comunidad (DSP_COM_*) + LPAD(nº_dispositivo, 10, '0')`. Se recalcula en
  `KEY-LISTVAL` antes de abrir la LOV. Si el número de dispositivo es NULL, el
  identificador queda NULL.
- **Validación de rango inicial**: `TXT_DIS_DESDE.WHEN-VALIDATE-ITEM` delega en
  `IA_DES_ANUL_RECI_PKG.P_DES_IDEN_DESDE`.
- **Validación de rango final**: `TXT_DIS_HASTA.WHEN-VALIDATE-ITEM` delega en
  `IA_DES_ANUL_RECI_PKG.P_DES_IDEN_HASTA`.
- **Validación contra lista**: `TXT_DIS_DESDE` (LOV `LV_DES_ANUL_RECI_D`) y
  `TXT_DIS_HASTA` (LOV `LV_DES_ANUL_RECI_H`) tienen "Validar desde Lista = Sí",
  por lo que solo se admiten valores presentes en su lista de valores.

## Llamadas a paquetes / procedimientos de BD

| Procedimiento / rutina                    | Parámetros                       | Contexto / disparador                         | Propósito |
|-------------------------------------------|----------------------------------|-----------------------------------------------|-----------|
| `IA_DES_ANUL_RECI_PKG.P_DES_IDEN_DESDE`   | (sin parámetros; usa items `:BLOQUE.*`) | `TXT_DIS_DESDE` · WHEN-VALIDATE-ITEM   | Valida el identificador/rango inicial. |
| `IA_DES_ANUL_RECI_PKG.P_DES_IDEN_HASTA`   | (sin parámetros; usa items `:BLOQUE.*`) | `TXT_DIS_HASTA` · WHEN-VALIDATE-ITEM   | Valida el identificador/rango final. |
| `CARGAR_LISTA_ESPECIE`                     | `('IA_DES_ANUL_RECI.LST_ESPECIES')` | Bloque · WHEN-NEW-BLOCK-INSTANCE           | Rellena la lista desplegable de especies (rutina de utilidad del Form). |
| `WHEN_NEW_ITEM_INSTANCE`                   | (sin parámetros)                 | Bloque · WHEN-NEW-ITEM-INSTANCE               | Rutina común de gestión de estado por item. |
| `P_ESTABLECER_BOTONERA`                    | (sin parámetros)                 | Bloque · WHEN-NEW-ITEM-INSTANCE               | Habilita/deshabilita la botonera según el estado. |
| `LIST_VALUES` (built-in Forms)            | —                                | Bloque · KEY-LISTVAL                           | Abre la LOV asociada al item actual. |

> Nota: los procedimientos `P_DES_IDEN_DESDE` / `P_DES_IDEN_HASTA` no reciben
> parámetros explícitos en la llamada; operan sobre los items del bloque mediante
> referencias globales de Forms (`:IA_DES_ANUL_RECI.*`). Al migrar habrá que pasar
> esos valores explícitamente al servicio.

## Notas para la migración a Java

- **Controller (`bean`)** — `DesAnulReciBean` (`@Component("desAnulReciBean")`,
  `@Scope` de vista/sesión, `Serializable`):
  - Equivalente a `WHEN-NEW-BLOCK-INSTANCE`: método `@PostConstruct` o `init()` que
    cargue la lista de especies (`cargarListaEspecie()`).
  - Equivalente a `WHEN-LIST-CHANGED`: listener del cambio de especie que reinicie
    el rango (`txtDisDesde`, `dspComDesde`, `txtDisHasta`, `dspComHasta`, `dspNDisp=0`).
  - Cálculo del identificador electrónico (lógica de `KEY-LISTVAL`) como método
    utilitario: `idElect = comunidad + String.format("%010d", numeroDispositivo)`
    (equivalente a `LPAD(...,10,'0')`), devolviendo `null` si el número es null.
  - `WHEN-NEW-ITEM-INSTANCE` (`P_ESTABLECER_BOTONERA`) → lógica de habilitación de
    botones en el bean; no requiere BD.
- **Service (`service`)** — `DesAnulReciService` (`@Service @Transactional`):
  - `validarIdenDesde(...)` ↔ `P_DES_IDEN_DESDE`.
  - `validarIdenHasta(...)` ↔ `P_DES_IDEN_HASTA`.
  - Método principal para **deshacer la anulación de recepción** sobre el rango
    validado (la operación de negocio que da nombre al bloque; su implementación
    reside en el paquete `IA_DES_ANUL_RECI_PKG`, revisar el cuerpo del paquete en
    BD para transponer la lógica completa).
  - Pasar explícitamente como parámetros los valores que en Forms se leían de los
    items globales (especie, identificador inicial/final).
- **Repository (`repository`)** — `@Repository` con `EntityManager`:
  - Consultas para poblar las LOV `LV_DES_ANUL_RECI_D` / `LV_DES_ANUL_RECI_H`
    (dispositivos válidos por especie) y para calcular `DSP_N_DISP` (total de
    dispositivos en el rango).
  - Consulta de especies para `LST_ESPECIES`.
- **Model (`model`)** — entidad(es) de dispositivo/recepción electrónica; el
  identificador electrónico es un valor derivado (comunidad + nº dispositivo con
  padding) apto para un *value object*.
- **Pendiente**: el detalle de las validaciones y la operación de deshacer anulación
  vive en el cuerpo del paquete `IA_DES_ANUL_RECI_PKG` (no incluido en este bloque
  del Form); debe localizarse en la BD para completar la capa de servicio.

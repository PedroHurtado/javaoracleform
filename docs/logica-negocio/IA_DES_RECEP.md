# Formulario: IA_DES_RECEP

## Propósito

Bloque de control **"Deshacer recepción"** del formulario `IAAL0600`. Permite al
usuario seleccionar una **especie** y un **rango de identificadores electrónicos**
(dispositivos) —definido por un identificador inicial y uno final— con el fin de
**deshacer/anular la recepción** de esos dispositivos. El bloque no es un bloque
de base de datos (`Bloque de Datos de Base de Datos = No`): actúa como panel de
parámetros que alimenta las validaciones y la operación de negocio delegada al
paquete de BD `IA_DES_RECEP_PKG`.

Los identificadores electrónicos se construyen concatenando un **código de
comunidad** (2 caracteres) con el número de dispositivo rellenado a 10 dígitos
con ceros a la izquierda. El campo `DSP_N_DISP` muestra el **total de
dispositivos a deshacer** en el rango seleccionado.

## Items / campos de entrada relevantes

| Item              | Tipo             | Datos      | Long. | Descripción / rol de negocio                                                                 |
|-------------------|------------------|------------|-------|----------------------------------------------------------------------------------------------|
| `LST_ESPECIES`    | Lista desplegable| Char       | 50    | Selección de especie. Se carga vía `CARGAR_LISTA_ESPECIE`. Al cambiar, resetea todo el rango.|
| `DSP_COM_DESDE`   | Display item     | Char       | 2     | Código de comunidad del identificador inicial (parte del ID electrónico "desde").            |
| `TXT_DIS_DESDE`   | Texto (LOV)      | Char       | 10    | Número de dispositivo inicial. LOV `LV_DES_RECEP_D`, validado desde lista.                    |
| `TXT_ID_ELECT_D`  | Texto            | Char       | 15    | Identificador electrónico inicial calculado = `DSP_COM_DESDE || LPAD(TXT_DIS_DESDE,10,'0')`.  |
| `DSP_COM_HASTA`   | Display item     | Char       | 2     | Código de comunidad del identificador final.                                                 |
| `TXT_DIS_HASTA`   | Texto (LOV)      | Char       | 10    | Número de dispositivo final. LOV `LV_DES_RECEP_H`, validado desde lista.                      |
| `TXT_ID_ELECT_H`  | Texto            | Char       | 15    | Identificador electrónico final calculado = `DSP_COM_HASTA || LPAD(TXT_DIS_HASTA,10,'0')`.    |
| `DSP_N_DISP`      | Display item     | Number     | 40    | Total de dispositivos a deshacer en el rango. Valor inicial `0`.                              |

Notas de negocio sobre los items:

- `TXT_DIS_DESDE` y `TXT_DIS_HASTA` tienen **LOV con "Validar desde Lista = Sí"**,
  por lo que solo admiten valores presentes en su lista de valores respectiva.
- `TXT_ID_ELECT_D`/`TXT_ID_ELECT_H` y `DSP_COM_*`/`DSP_N_DISP` son campos
  **calculados/mostrados**, no editables directamente por el usuario como entrada
  de negocio principal.

## Disparadores (lógica de negocio)

### Bloque `IA_DES_RECEP`

#### `WHEN-NEW-BLOCK-INSTANCE`
Al entrar en el bloque, carga la lista de especies.

```sql
--Carga la lista de especies.
CARGAR_LISTA_ESPECIE('IA_DES_RECEP.LST_ESPECIES');
```

#### `KEY-LISTVAL`
Antes de abrir la lista de valores (LOV), reconstruye los identificadores
electrónicos "desde" y "hasta" a partir del código de comunidad y del número de
dispositivo (rellenado a 10 dígitos), y luego lanza la LOV.

```sql
/************************************************************************************
* Funcionalidad: Validar campos que crean el identificadores y mostrar la lista de
*                valores de identificadores iniciales y finales.
*
* Modificaciones
* --------------
*
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              14/03/2006          Desarrollo inicial
*
************************************************************************************/

IF :IA_DES_RECEP.TXT_DIS_DESDE IS NULL THEN
    :IA_DES_RECEP.TXT_ID_ELECT_D := NULL;
ELSE
    :IA_DES_RECEP.TXT_ID_ELECT_D := :IA_DES_RECEP.DSP_COM_DESDE || LPAD(:IA_DES_RECEP.TXT_DIS_DESDE,10,'0');
END IF;

IF :IA_DES_RECEP.TXT_DIS_HASTA IS NULL THEN
    :IA_DES_RECEP.TXT_ID_ELECT_H := NULL;
ELSE
    :IA_DES_RECEP.TXT_ID_ELECT_H := :IA_DES_RECEP.DSP_COM_HASTA || LPAD(:IA_DES_RECEP.TXT_DIS_HASTA,10,'0');
END IF;

LIST_VALUES;
```

#### `WHEN-NEW-ITEM-INSTANCE`
Al posicionarse en cada item, ejecuta la lógica común de navegación de item y
recalcula el estado de la botonera del formulario.

```sql
WHEN_NEW_ITEM_INSTANCE;

P_ESTABLECER_BOTONERA;
```

### Item `LST_ESPECIES`

#### `WHEN-LIST-CHANGED`
Al cambiar la especie seleccionada, **limpia todo el rango de identificadores** y
pone a cero el contador de dispositivos (fuerza al usuario a re-seleccionar el
rango para la nueva especie).

```sql
:IA_DES_RECEP.TXT_DIS_DESDE:=NULL;
:IA_DES_RECEP.DSP_COM_DESDE:=NULL;
:IA_DES_RECEP.TXT_DIS_HASTA:=NULL;
:IA_DES_RECEP.DSP_COM_HASTA:=NULL;
:IA_DES_RECEP.DSP_N_DISP:=0;
```

### Item `TXT_DIS_DESDE` (dispositivo inicial)

#### `WHEN-VALIDATE-ITEM`
Al validar el dispositivo inicial, delega la validación del rango de
identificadores al paquete de BD.

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
IA_DES_RECEP_PKG.P_DES_IDEN_DESDE;
```

### Item `TXT_DIS_HASTA` (dispositivo final)

#### `WHEN-VALIDATE-ITEM`
Al validar el dispositivo final, delega la validación del rango de
identificadores al paquete de BD.

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
IA_DES_RECEP_PKG.P_DES_IDEN_HASTA;
```

## Validaciones de negocio

1. **Especie obligatoria como punto de partida**: cambiar la especia
   (`WHEN-LIST-CHANGED`) invalida cualquier rango previamente introducido,
   forzando la coherencia especie ↔ rango de dispositivos.
2. **Composición del identificador electrónico**: el ID electrónico se forma
   siempre como `código_comunidad (2) + LPAD(nº_dispositivo, 10, '0')`, con un
   total de 12 caracteres significativos (item declarado con longitud 15). Si el
   número de dispositivo es NULL, el identificador electrónico correspondiente se
   pone a NULL.
3. **Valores de dispositivo acotados por LOV**: `TXT_DIS_DESDE` y `TXT_DIS_HASTA`
   tienen "Validar desde Lista = Sí" (LOVs `LV_DES_RECEP_D` y `LV_DES_RECEP_H`),
   de modo que solo se aceptan dispositivos existentes/válidos.
4. **Validación del rango**: la comprobación de coherencia del rango
   (inicial ≤ final, pertenencia a la especie, cálculo de `DSP_N_DISP`, etc.) se
   realiza en el paquete de BD mediante `P_DES_IDEN_DESDE` y `P_DES_IDEN_HASTA`.
   La lógica concreta reside en el paquete y no está en el formulario.

## Llamadas a paquetes / procedimientos de BD

| Rutina                              | Disparador origen                        | Parámetros                        | Propósito                                                                 |
|-------------------------------------|------------------------------------------|-----------------------------------|--------------------------------------------------------------------------|
| `IA_DES_RECEP_PKG.P_DES_IDEN_DESDE` | `TXT_DIS_DESDE.WHEN-VALIDATE-ITEM`        | (ninguno explícito; usa items `:IA_DES_RECEP.*`) | Validar el identificador/rango inicial de dispositivos a deshacer.        |
| `IA_DES_RECEP_PKG.P_DES_IDEN_HASTA` | `TXT_DIS_HASTA.WHEN-VALIDATE-ITEM`        | (ninguno explícito; usa items `:IA_DES_RECEP.*`) | Validar el identificador/rango final de dispositivos a deshacer.          |
| `CARGAR_LISTA_ESPECIE`              | `WHEN-NEW-BLOCK-INSTANCE`                 | `'IA_DES_RECEP.LST_ESPECIES'` (nombre del item lista) | Poblar la lista desplegable de especies.                                 |
| `WHEN_NEW_ITEM_INSTANCE`            | `WHEN-NEW-ITEM-INSTANCE`                  | (ninguno)                         | Procedimiento común de navegación de item (program unit del formulario). |
| `P_ESTABLECER_BOTONERA`             | `WHEN-NEW-ITEM-INSTANCE`                  | (ninguno)                         | Habilitar/deshabilitar botones según el estado actual.                   |
| `LIST_VALUES` (built-in)            | `KEY-LISTVAL`                             | —                                 | Built-in de Forms que muestra la LOV asociada al item actual.            |

> Los procedimientos `P_DES_IDEN_DESDE` / `P_DES_IDEN_HASTA` no reciben
> parámetros formales en la llamada: operan directamente sobre los items del
> bloque (`:IA_DES_RECEP.TXT_ID_ELECT_D`, `TXT_ID_ELECT_H`, `DSP_N_DISP`, etc.)
> mediante `:SYSTEM`/referencia global de Forms. Para conocer las reglas exactas
> del rango habría que inspeccionar el cuerpo del paquete `IA_DES_RECEP_PKG` en
> la BD.

## Notas para la migración a Java

Mapeo sugerido a la arquitectura del proyecto (`bean` → `service` → `repository`
→ `model`), siguiendo `CLAUDE.md`:

- **Controller (`bean`)** — `DeshacerRecepcionBean` (`@Component("desRecepBean")`,
  `@Scope` de vista/sesión, `Serializable`):
  - Estado: `especie`, `dispositivoDesde`, `comunidadDesde`, `idElectronicoDesde`,
    `dispositivoHasta`, `comunidadHasta`, `idElectronicoHasta`, `totalDispositivos`.
  - `WHEN-NEW-BLOCK-INSTANCE` → método `init()`/`@PostConstruct` que carga la
    lista de especies desde el service.
  - `WHEN-LIST-CHANGED` (LST_ESPECIES) → `onEspecieChange()`: limpiar rango y
    poner `totalDispositivos = 0`.
  - `KEY-LISTVAL` → construcción del identificador electrónico antes de abrir la
    ayuda de búsqueda; en JSF equivale a un método que recalcula
    `idElectronico = comunidad + StringUtils.leftPad(dispositivo, 10, '0')` y
    dispara la ventana/autocomplete de selección (LOV → `p:autoComplete` o diálogo).
  - `WHEN-VALIDATE-ITEM` (desde/hasta) → validadores JSF que invocan al service.

- **Service (`service`)** — `DeshacerRecepcionService` (`@Service @Transactional`):
  - `validarIdentificadorDesde(...)` ↔ `IA_DES_RECEP_PKG.P_DES_IDEN_DESDE`.
  - `validarIdentificadorHasta(...)` ↔ `IA_DES_RECEP_PKG.P_DES_IDEN_HASTA`.
  - Reglas: rango inicial ≤ final, pertenencia a la especie, cálculo del total de
    dispositivos del rango. **La lógica exacta está en `IA_DES_RECEP_PKG`; hay que
    obtener el cuerpo del paquete para portarla fielmente.**
  - `cargarEspecies()` ↔ `CARGAR_LISTA_ESPECIE`.

- **Repository (`repository`)** — `DispositivoRepository`
  (`@Repository` + `EntityManager`, JPQL):
  - Consultar dispositivos por especie y rango de identificador electrónico.
  - Contar dispositivos en el rango (para `DSP_N_DISP`).
  - Proveer los valores de las LOV (`LV_DES_RECEP_D`, `LV_DES_RECEP_H`).

- **Model (`model`)** — entidades JPA:
  - `Especie` (código, descripción) para la lista desplegable.
  - `Dispositivo`/`IdentificadorElectronico` con los campos `comunidad` (2),
    `numeroDispositivo` (10) y el identificador compuesto.
  - Considerar un **Value Object `IdentificadorElectronico`** que encapsule la
    regla de composición `comunidad + LPAD(numero,10,'0')` (candidato claro a VO
    en DDD).

- **Puntos de atención**:
  - El identificador electrónico es un valor **derivado**; no debería persistirse
    de forma redundante sino calcularse en el VO.
  - Las validaciones `P_DES_IDEN_*` deben trasladarse a validadores de
    dominio/servicio y no a la capa de presentación.
  - `P_ESTABLECER_BOTONERA` corresponde a lógica de habilitación de UI
    (`rendered`/`disabled` en JSF); no es lógica de dominio.

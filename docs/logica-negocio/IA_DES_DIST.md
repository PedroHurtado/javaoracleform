# Formulario: IA_DES_DIST

## Propósito

Bloque de datos **IA_DES_DIST** ("Deshacer distribución") del formulario
`IAAL0600`. Permite al usuario seleccionar un **rango de identificadores
electrónicos** (dispositivos) de una **especie** determinada para **deshacer su
distribución**. El usuario indica un identificador inicial y otro final (compuestos
por un código de comunidad/provincia más un número de dispositivo), y el bloque
calcula y muestra el **total de dispositivos a deshacer** dentro de ese rango.

Es un bloque **no basado en base de datos** (`Bloque de Datos de Base de Datos = No`),
puramente de control/parámetros: recoge criterios de entrada y delega la lógica de
validación y cálculo en el paquete de BD `IA_DES_DIST_PKG`.

## Items / campos de entrada relevantes

| Item | Tipo | Datos | Rol funcional |
|------|------|-------|---------------|
| `LST_ESPECIES` | Elemento de Lista (desplegable) | Char(50) | Selección de la **especie**. Se carga en `WHEN-NEW-BLOCK-INSTANCE`. |
| `DSP_COM_DESDE` | Visualizar Elemento | Char(2) | Código de comunidad/provincia del identificador **inicial**. Se rellena vía LOV. |
| `TXT_DIS_DESDE` | Elemento de Texto | Char(10) | Número de dispositivo **inicial**. LOV `LV_DES_DIST_D`, validado desde lista. |
| `TXT_ID_ELECT_D` | Elemento de Texto | Char(15) | Identificador electrónico **inicial** completo (calculado): `DSP_COM_DESDE || LPAD(TXT_DIS_DESDE,10,'0')`. |
| `DSP_COM_HASTA` | Visualizar Elemento | Char(2) | Código de comunidad/provincia del identificador **final**. |
| `TXT_DIS_HASTA` | Elemento de Texto | Char(10) | Número de dispositivo **final**. LOV `LV_DES_DIST_H`, validado desde lista. |
| `TXT_ID_ELECT_H` | Elemento de Texto | Char(15) | Identificador electrónico **final** completo (calculado): `DSP_COM_HASTA || LPAD(TXT_DIS_HASTA,10,'0')`. |
| `DSP_N_DISP` | Visualizar Elemento | Number(40), valor inicial 0 | **Total de dispositivos a deshacer** (solo lectura, resultado del cálculo). |

Listas de valores asociadas: `LV_DES_DIST_D` (rango desde) y `LV_DES_DIST_H` (rango hasta).

## Disparadores (lógica de negocio)

### Bloque `IA_DES_DIST`

#### WHEN-NEW-ITEM-INSTANCE
Establece la botonera al entrar en cualquier item del bloque.

```sql
WHEN_NEW_ITEM_INSTANCE;

P_ESTABLECER_BOTONERA;
```

#### KEY-LISTVAL
Al invocar la lista de valores: construye los identificadores electrónicos inicial y
final a partir del código de comunidad y el número de dispositivo (con relleno a 10
dígitos), y luego lanza la LOV.

```sql
/************************************************************************************
* Funcionalidad: Validar campos que crean el identificadores y mostrar la lista de
*               valores de identicadores iniciales y finales.
*
* Modificaciones
* --------------
*
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              14/03/2006          Desarrollo inicial
*
************************************************************************************/

IF :IA_DES_DIST.TXT_DIS_DESDE IS NULL THEN
    :IA_DES_DIST.TXT_ID_ELECT_D := NULL;
ELSE
    :IA_DES_DIST.TXT_ID_ELECT_D := :IA_DES_DIST.DSP_COM_DESDE || LPAD(:IA_DES_DIST.TXT_DIS_DESDE,10,'0');
END IF;

IF :IA_DES_DIST.TXT_DIS_HASTA IS NULL THEN
      :IA_DES_DIST.TXT_ID_ELECT_H := NULL;
ELSE
      :IA_DES_DIST.TXT_ID_ELECT_H := :IA_DES_DIST.DSP_COM_HASTA || LPAD(:IA_DES_DIST.TXT_DIS_HASTA,10,'0');
END IF;

LIST_VALUES;
```

#### WHEN-NEW-BLOCK-INSTANCE
Al entrar en el bloque, carga la lista de especies.

```sql
--Carga la lista de especies.
CARGAR_LISTA_ESPECIE('IA_DES_DIST.LST_ESPECIES');
```

### Item `LST_ESPECIES`

#### WHEN-LIST-CHANGED
Al cambiar la especie seleccionada, **reinicia** todos los campos del rango de
identificadores y el total, para forzar una nueva selección coherente con la especie.

```sql
:IA_DES_DIST.TXT_DIS_DESDE:=NULL;
:IA_DES_DIST.DSP_COM_DESDE:=NULL;
:IA_DES_DIST.TXT_DIS_HASTA:=NULL;
:IA_DES_DIST.DSP_COM_HASTA:=NULL;
:IA_DES_DIST.DSP_N_DISP:=0;
```

### Item `TXT_DIS_DESDE`

#### WHEN-VALIDATE-ITEM
Valida el identificador **inicial** del rango delegando en el paquete de BD.

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
IA_DES_DIST_PKG.P_DES_IDEN_DESDE;
```

### Item `TXT_DIS_HASTA`

#### WHEN-VALIDATE-ITEM
Valida el identificador **final** del rango delegando en el paquete de BD.

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
IA_DES_DIST_PKG.P_DES_IDEN_HASTA;
```

## Validaciones de negocio

1. **Composición del identificador electrónico** (KEY-LISTVAL): el identificador
   electrónico se forma concatenando el código de comunidad (2 caracteres) con el
   número de dispositivo rellenado a la izquierda con ceros hasta 10 dígitos
   (`LPAD(...,10,'0')`), resultando un código de 12 caracteres (campo de longitud 15).
   Si no hay número de dispositivo, el identificador queda nulo.

2. **Validación del rango inicial** (`TXT_DIS_DESDE` / WHEN-VALIDATE-ITEM): delegada
   en `IA_DES_DIST_PKG.P_DES_IDEN_DESDE`. Comprueba la validez del identificador
   inicial del rango de dispositivos a deshacer.

3. **Validación del rango final** (`TXT_DIS_HASTA` / WHEN-VALIDATE-ITEM): delegada
   en `IA_DES_DIST_PKG.P_DES_IDEN_HASTA`. Comprueba la validez del identificador
   final del rango. Es de suponer que estos procedimientos también recalculan/actualizan
   `DSP_N_DISP` (total de dispositivos a deshacer) y verifican la coherencia
   desde/hasta, aunque el detalle reside en el cuerpo del paquete de BD.

4. **Validación desde lista** (`Validar desde Lista = Sí` en `TXT_DIS_DESDE` y
   `TXT_DIS_HASTA`): los números de dispositivo deben existir en las LOV
   `LV_DES_DIST_D` y `LV_DES_DIST_H` respectivamente.

5. **Reinicio por cambio de especie** (WHEN-LIST-CHANGED): al cambiar la especie se
   invalidan/limpian todos los datos del rango y el total, obligando a reintroducir el
   rango para la nueva especie.

## Llamadas a paquetes / procedimientos de BD

| Paquete.Procedimiento | Parámetros | Disparador origen | Función |
|-----------------------|------------|-------------------|---------|
| `IA_DES_DIST_PKG.P_DES_IDEN_DESDE` | (sin parámetros; opera sobre items del bloque vía referencias `:BLOQUE.ITEM`) | `TXT_DIS_DESDE.WHEN-VALIDATE-ITEM` | Valida el identificador electrónico **inicial** del rango. |
| `IA_DES_DIST_PKG.P_DES_IDEN_HASTA` | (sin parámetros) | `TXT_DIS_HASTA.WHEN-VALIDATE-ITEM` | Valida el identificador electrónico **final** del rango. |

Rutinas de librería/Forms utilizadas (no son paquetes `IA_*_PKG`):

- `WHEN_NEW_ITEM_INSTANCE` y `P_ESTABLECER_BOTONERA` — gestión de estado de la botonera.
- `CARGAR_LISTA_ESPECIE('IA_DES_DIST.LST_ESPECIES')` — carga de la lista de especies.
- `LIST_VALUES` — built-in de Forms para mostrar la LOV del item actual.

## Notas para la migración a Java

- **Bean (Controller)** — El bloque es un formulario de parámetros sin persistencia
  propia. Modelar un `@Component("desDistBean")` con `@Scope` de vista/sesión y
  `Serializable`, con las propiedades: `especie`, `comDesde`, `disDesde`,
  `idElectDesde`, `comHasta`, `disHasta`, `idElectHasta`, `totalDispositivos`.
  - El disparador **KEY-LISTVAL** se traduce en un método que, antes de abrir el
    diálogo de selección, recompone `idElectDesde`/`idElectHasta` con
    `String.format("%s%010d", com, dispositivo)` (equivalente a `LPAD(...,10,'0')`);
    valor `null` cuando el dispositivo es nulo.
  - **WHEN-LIST-CHANGED** de la especie → listener del `p:selectOneMenu` que limpia
    los campos del rango y pone `totalDispositivos = 0`.
  - **WHEN-NEW-BLOCK-INSTANCE** → inicialización (`@PostConstruct` o al abrir la vista)
    que carga la lista de especies desde un `service`.

- **Service (lógica de negocio)** — Encapsular la lógica de `IA_DES_DIST_PKG` en un
  `@Service @Transactional`, con métodos equivalentes a:
  - `validarIdentificadorDesde(...)` ← `P_DES_IDEN_DESDE`
  - `validarIdentificadorHasta(...)` ← `P_DES_IDEN_HASTA`
  - un método de conteo/actualización que devuelva el **total de dispositivos a
    deshacer** (`DSP_N_DISP`) para el rango y especie dados.
  Estos métodos deben trasladar las validaciones internas del cuerpo del paquete PL/SQL
  (coherencia desde ≤ hasta, existencia del rango para la especie, etc.), que no están
  visibles en el `.fmb` y requieren revisar el fuente del paquete de BD.

- **Repository** — El acceso a datos (consulta de dispositivos existentes por especie
  y rango, y las LOV `LV_DES_DIST_D` / `LV_DES_DIST_H`) se implementa con
  `@Repository` + `EntityManager` (JPQL), consultando las entidades de especie y
  dispositivo/identificador electrónico.

- **Validaciones** — Las LOV con "Validar desde Lista = Sí" se convierten en validación
  de que el valor seleccionado pertenece al conjunto permitido (por especie).

- **Pendiente de fuente PL/SQL** — Para una migración fiel se necesita el cuerpo de
  `IA_DES_DIST_PKG` (`P_DES_IDEN_DESDE`, `P_DES_IDEN_HASTA`), no incluido en este
  bloque del `.fmb`. Aquí solo se documentan las llamadas y su rol.

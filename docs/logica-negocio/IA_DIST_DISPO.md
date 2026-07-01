# Formulario: IA_DIST_DISPO

Bloque de datos "Distribución de dispositivos" del formulario Oracle Forms
`IAAL0600` (líneas 6855–8387 del volcado). Es un bloque **no ligado a base de
datos** (`Bloque de Datos de Base de Datos = No`) que sirve como pantalla de
filtros/parámetros para lanzar la distribución de dispositivos (identificadores
electrónicos) entre distintos actores (ADS, veterinarios) para una especie y un
rango de identificadores.

## Propósito

Capturar los criterios de una operación de **distribución de dispositivos**
(identificadores electrónicos de animales) y prepararlos para su procesamiento:

- Seleccionar una **especie** (lista desplegable).
- Definir un **rango de identificadores electrónicos** (desde / hasta),
  compuestos por un código de comunidad de 2 caracteres más un dispositivo de
  10 dígitos con relleno de ceros a la izquierda.
- Asignar la distribución a un **ADS** (Agrupación de Defensa Sanitaria) y/o a
  un **veterinario**, cada uno con su identificador oculto.
- Indicar el **número total de dispositivos** a distribuir y la **fecha de
  distribución**.

Al ser un bloque de un único registro (`Número de Registros Mostrados = 1`,
`Orientación = Vertical`), funciona como cabecera de parámetros más que como
rejilla de datos.

## Items / campos de entrada relevantes

| Item                     | Tipo elemento         | Tipo dato | Long. | Lista de valores (LOV) | Notas |
|--------------------------|-----------------------|-----------|-------|------------------------|-------|
| `LST_ESPECIES`           | Lista desplegable     | Char      | 50    | —                      | Cargada dinámicamente con `CARGAR_LISTA_ESPECIE`. Valor de lista `LIST519`. |
| `DSP_COM_DESDE`          | Visualizar elemento   | Char      | 2     | —                      | Código de comunidad del rango inicial (prefijo del identificador). |
| `TXT_DIS_DESDE`          | Elemento de texto     | Char      | 10    | `LV_DIST_DISPO_D`      | Dispositivo inicial; valida desde lista. |
| `TXT_ID_ELECT_D`         | Elemento de texto     | Char      | 15    | —                      | Identificador electrónico inicial calculado (comunidad + dispositivo). |
| `DSP_COM_HASTA`          | Visualizar elemento   | Char      | 2     | —                      | Código de comunidad del rango final. |
| `TXT_DIS_HASTA`          | Elemento de texto     | Char      | 10    | `LV_DIST_DISPO_H`      | Dispositivo final; valida desde lista. |
| `TXT_ID_ELECT_H`         | Elemento de texto     | Char      | 15    | —                      | Identificador electrónico final calculado. |
| `TXT_DIST_ADS`           | Elemento de texto     | Char      | 40    | `LV_ADS`               | Descripción del ADS; valida desde lista. |
| `TXT_DIST_ADS_ID`        | Elemento de texto     | Number    | 6     | —                      | Id del ADS (oculto, `Lienzo` vacío). Marcado como elemento de BD. |
| `TXT_VETERINARIO`        | Elemento de texto     | Char      | 90    | `LV_VETERI`            | Nombre del veterinario; valida desde lista. |
| `TXT_VETERINARIO_ID`     | Elemento de texto     | Number    | 6     | —                      | Id del veterinario (oculto, `Lienzo` vacío). |
| `DSP_N_DISP`             | Visualizar elemento   | Number    | 40    | —                      | Total de dispositivos a distribuir. Valor inicial `0`. Solo lectura (visualización). |
| `TXT_FECHA_DISTRIBUCION` | Elemento de texto     | Date      | 10    | —                      | Fecha de distribución. Valor inicial `:PARAMETER.P_FECHA`. Máscara `DD/MM/YYYY`. |

## Disparadores (lógica de negocio)

### Bloque `IA_DIST_DISPO`

**WHEN-NEW-ITEM-INSTANCE** — establece el estado de la botonera al entrar en
cada item.

```sql
WHEN_NEW_ITEM_INSTANCE;

-- Establecer el estado de los botones de la botonera.
P_ESTABLECER_BOTONERA;
```

**KEY-LISTVAL** — antes de mostrar la LOV, compone los identificadores
electrónicos inicial y final a partir del código de comunidad y el dispositivo
(relleno a 10 dígitos con ceros), y luego lanza la lista de valores.

```sql
/************************************************************************************
* Funcionalidad: Validar campos que crean los identificadores y mostrar la lista de
*                valores de identificadores iniciales y finales.
*
* Proyecto         Autor             Fecha              Comentarios
* RIIA             MEGG              14/03/2006          Desarrollo inicial
************************************************************************************/

IF :IA_DIST_DISPO.TXT_DIS_DESDE IS NULL THEN
    :IA_DIST_DISPO.TXT_ID_ELECT_D := NULL;
ELSE
    :IA_DIST_DISPO.TXT_ID_ELECT_D := :IA_DIST_DISPO.DSP_COM_DESDE || LPAD(:IA_DIST_DISPO.TXT_DIS_DESDE,10,'0');
END IF;

IF :IA_DIST_DISPO.TXT_DIS_HASTA IS NULL THEN
    :IA_DIST_DISPO.TXT_ID_ELECT_H := NULL;
ELSE
    :IA_DIST_DISPO.TXT_ID_ELECT_H := :IA_DIST_DISPO.DSP_COM_HASTA || LPAD(:IA_DIST_DISPO.TXT_DIS_HASTA,10,'0');
END IF;

-- Mostrar lista de valores.
LIST_VALUES;
```

**WHEN-NEW-BLOCK-INSTANCE** — al entrar en el bloque, carga la lista de especies.

```sql
--Carga la lista de especies.
CARGAR_LISTA_ESPECIE('IA_DIST_DISPO.LST_ESPECIES');
```

### Item `LST_ESPECIES`

**WHEN-LIST-CHANGED** — al cambiar la especie seleccionada, limpia el rango de
identificadores y reinicia el contador de dispositivos.

```sql
:IA_DIST_DISPO.TXT_DIS_DESDE:=NULL;
:IA_DIST_DISPO.DSP_COM_DESDE:=NULL;
:IA_DIST_DISPO.TXT_DIS_HASTA:=NULL;
:IA_DIST_DISPO.DSP_COM_HASTA:=NULL;
:IA_DIST_DISPO.DSP_N_DISP:=0;
```

### Item `TXT_DIS_DESDE`

**WHEN-VALIDATE-ITEM** — valida el rango de identificadores desde, delegando en
el paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
*
* Proyecto         Autor             Fecha              Comentarios
* RIIA             MEGG              14/03/2006          Desarrollo inicial
************************************************************************************/
IA_DIST_DISPO_PKG.P_DIST_IDEN_DESDE;
```

### Item `TXT_DIS_HASTA`

**WHEN-VALIDATE-ITEM** — valida el rango de identificadores hasta, delegando en
el paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
*
* Proyecto         Autor             Fecha              Comentarios
* RIIA             MEGG              14/03/2006          Desarrollo inicial
************************************************************************************/
IA_DIST_DISPO_PKG.P_DIST_IDEN_HASTA;
```

### Item `TXT_DIST_ADS`

**WHEN-VALIDATE-ITEM** — si el ADS queda sin valor, se anula también su id.

```sql
/************************************************************************************
* Funcionalidad: En el caso de que el ADS no tenga valor el id tampoco tendrá valor
*
* Proyecto         Autor             Fecha              Comentarios
* RIIA             MEGG              31/03/2006          Desarrollo inicial
************************************************************************************/
IF :IA_DIST_DISPO.TXT_DIST_ADS IS NULL THEN
    :IA_DIST_DISPO.TXT_DIST_ADS_ID := NULL;
END IF;
```

### Item `TXT_VETERINARIO`

**WHEN-VALIDATE-ITEM** — si el veterinario queda sin valor, se anula también su id.

```sql
/***********************************************************************************
* Funcionalidad: En el caso de que el veterinario no tenga valor el id tampoco
*                tendrá valor
*
* Proyecto         Autor             Fecha              Comentarios
* RIIA             MEGG              31/03/2006          Desarrollo inicial
************************************************************************************/
IF :IA_DIST_DISPO.TXT_VETERINARIO IS NULL THEN
    :IA_DIST_DISPO.TXT_VETERINARIO_ID := NULL;
END IF;
```

### Item `TXT_FECHA_DISTRIBUCION`

**WHEN-VALIDATE-ITEM** — la fecha de distribución no puede ser posterior a la
fecha del sistema; si lo es, muestra alerta de error y aborta la operación.

```sql
/***********************************************************************************
* Funcionalidad: Validar la fecha de distribución.
*
* Proyecto         Autor             Fecha              Comentarios
* RIIA             MEGG              31/03/2006          Desarrollo inicial
************************************************************************************/
DECLARE
  V_BOTON NUMBER;
  ID_ALERT ALERT;
BEGIN
  ID_ALERT := FIND_ALERT('ALERT_ERROR');

  IF :IA_DIST_DISPO.TXT_FECHA_DISTRIBUCION > TRUNC(SYSDATE) THEN
     SET_ALERT_PROPERTY(ID_ALERT, ALERT_MESSAGE_TEXT, 'Esta fecha no puede ser mayor que la fecha del sistema');
     V_BOTON := SHOW_ALERT(ID_ALERT);
     RAISE FORM_TRIGGER_FAILURE;
  End if;
END;
```

## Validaciones de negocio

1. **Composición del identificador electrónico**: el identificador se forma como
   `código_comunidad (2) || LPAD(dispositivo, 10, '0')`, generando un código de
   15 caracteres. Si el dispositivo (desde/hasta) es NULL, el identificador
   correspondiente se anula. (KEY-LISTVAL)
2. **Rango de identificadores desde/hasta**: la validez de los dispositivos
   inicial y final se delega a `IA_DIST_DISPO_PKG.P_DIST_IDEN_DESDE` y
   `P_DIST_IDEN_HASTA` (lógica en BD).
3. **Validación contra LOV**: `TXT_DIS_DESDE`, `TXT_DIS_HASTA`, `TXT_DIST_ADS` y
   `TXT_VETERINARIO` tienen `Validar desde Lista = Sí`; solo se aceptan valores
   presentes en sus listas de valores respectivas.
4. **Consistencia descripción/id**: si `TXT_DIST_ADS` o `TXT_VETERINARIO` quedan
   vacíos, sus ids (`TXT_DIST_ADS_ID`, `TXT_VETERINARIO_ID`) se ponen a NULL,
   evitando ids huérfanos.
5. **Fecha de distribución no futura**: `TXT_FECHA_DISTRIBUCION` no puede ser
   mayor que `TRUNC(SYSDATE)`; en caso contrario, error y aborto
   (`FORM_TRIGGER_FAILURE`).
6. **Reinicio al cambiar especie**: al cambiar `LST_ESPECIES` se limpian rango de
   dispositivos, códigos de comunidad y el total de dispositivos (`DSP_N_DISP=0`).

## Llamadas a paquetes / procedimientos de BD

| Origen (item / disparador)            | Llamada                                   | Parámetros | Propósito |
|---------------------------------------|-------------------------------------------|------------|-----------|
| `TXT_DIS_DESDE` / WHEN-VALIDATE-ITEM  | `IA_DIST_DISPO_PKG.P_DIST_IDEN_DESDE`     | ninguno (opera sobre items `:IA_DIST_DISPO.*`) | Validar el identificador inicial del rango. |
| `TXT_DIS_HASTA` / WHEN-VALIDATE-ITEM  | `IA_DIST_DISPO_PKG.P_DIST_IDEN_HASTA`     | ninguno (opera sobre items `:IA_DIST_DISPO.*`) | Validar el identificador final del rango. |

Procedimientos/funciones locales de Forms invocados (no son paquetes `IA_*_PKG`,
pero forman parte de la lógica del bloque):

| Rutina                     | Parámetros                        | Uso |
|----------------------------|-----------------------------------|-----|
| `P_ESTABLECER_BOTONERA`    | ninguno                           | Habilita/deshabilita los botones de la botonera según el estado. |
| `CARGAR_LISTA_ESPECIE`     | `'IA_DIST_DISPO.LST_ESPECIES'`    | Rellena la lista desplegable de especies. |
| `WHEN_NEW_ITEM_INSTANCE`   | ninguno                           | Rutina común invocada al entrar en un item. |
| `LIST_VALUES` / `LIST_VALUES` (built-in) | ninguno            | Muestra la LOV asociada al item actual. |

> Nota: `P_DIST_IDEN_DESDE` y `P_DIST_IDEN_HASTA` se invocan sin argumentos
> explícitos; leen y modifican directamente los items del bloque
> (`TXT_DIS_DESDE`, `DSP_COM_DESDE`, `DSP_N_DISP`, etc.), patrón típico de Forms.
> Su lógica interna no está en este rango y deberá localizarse en el paquete de
> BD `IA_DIST_DISPO_PKG`.

## Notas para la migración a Java

- **Capa Controller (`bean`)**: `IA_DIST_DISPO` es una pantalla de parámetros de
  filtro. Modelar como un `@Component("distDispoBean")` con `@Scope("view"/"request")`,
  `Serializable`, con propiedades para cada item de entrada
  (especie, comunidadDesde, dispositivoDesde, idElectDesde, comunidadHasta,
  dispositivoHasta, idElectHasta, ads/adsId, veterinario/veterinarioId,
  numDispositivos, fechaDistribucion).
- **Cálculo de identificador**: el `KEY-LISTVAL` (composición
  `comunidad || LPAD(dispositivo,10,'0')`) es lógica de presentación/derivación;
  llevarla a un método helper del bean o del service
  (`String.format("%s%010d", comunidad, dispositivo)` o `StringUtils.leftPad`).
- **Validaciones de fecha** (`no futura`) → validación en el service o bean
  antes de ejecutar; en JSF puede ser un `Validator` o comprobación con
  `FacesMessage` (equivalente a la alerta `ALERT_ERROR`).
- **`P_DIST_IDEN_DESDE` / `P_DIST_IDEN_HASTA`**: son la lógica de negocio
  central (validación de rangos y probable cálculo del total de dispositivos).
  Migrar a métodos del **service** (`@Service @Transactional`), y el acceso a
  datos subyacente a un `@Repository` con JPQL. Es imprescindible obtener el
  código fuente de `IA_DIST_DISPO_PKG` para reproducir esta lógica.
- **LOVs** (`LV_DIST_DISPO_D`, `LV_DIST_DISPO_H`, `LV_ADS`, `LV_VETERI`, lista de
  especies) → convertir en consultas del repository que alimenten componentes
  PrimeFaces (`p:autoComplete` / `p:selectOneMenu`), manteniendo el vínculo
  descripción→id (patrón `TXT_*` visible + `TXT_*_ID` oculto).
- **Consistencia descripción/id** (anular id cuando la descripción es NULL) →
  encapsular en setters del bean o en la lógica de selección del autocompletar.
- **`DSP_N_DISP`** es un campo de solo lectura calculado (total de dispositivos);
  probablemente lo rellenan los procedimientos de validación de rango. En Java,
  exponer como propiedad derivada de solo lectura.
- **`TXT_FECHA_DISTRIBUCION`** se inicializa con `:PARAMETER.P_FECHA` (parámetro
  de entrada del formulario) → equivalente a un parámetro de request/flujo o
  valor por defecto inyectado al construir el bean.
- Bloque **no ligado a BD**: no genera una entidad JPA directa; es un DTO/objeto
  de comando de la operación de distribución.

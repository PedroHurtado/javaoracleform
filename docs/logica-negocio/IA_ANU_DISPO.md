# Formulario: IA_ANU_DISPO

Bloque de datos **IA_ANU_DISPO** (Anular recepción / dispositivos) del formulario `IAAL0600`.
Proyecto RIIA. Desarrollo inicial: MEGG, marzo 2006.

## Propósito

Permite **anular la recepción de dispositivos electrónicos** (crotales / identificadores
electrónicos) dentro de un rango. El usuario selecciona una **especie**, indica un
**identificador electrónico inicial y final** (compuestos por un código de comunidad más un
número de dispositivo con relleno de ceros a la izquierda) y una **fecha de anulación**.
El formulario calcula el total de dispositivos a anular en el rango y valida que los rangos y
la fecha sean coherentes antes de proceder.

No es un bloque de base de datos (`Bloque de Datos de Base de Datos = No`); todos sus items
son de control/pantalla y la lógica real de negocio se delega en el paquete de BD
`IA_ANULAR_RECEP_PKG`.

## Items / campos de entrada relevantes

| Item                | Tipo             | Datos / Long. | LOV / Validación         | Rol funcional |
|---------------------|------------------|---------------|--------------------------|---------------|
| `LST_ESPECIES`      | Lista desplegable| Char(50)      | Cargada dinámicamente    | Especie del dispositivo. Al cambiar, resetea el rango. |
| `DSP_COM_DESDE`     | Display item     | Char(2)       | —                        | Código de comunidad del identificador inicial. |
| `TXT_DIS_DESDE`     | Texto            | Char(10)      | LOV `LV_ANUL_RECEP_D`, valida desde lista | Número de dispositivo inicial del rango. |
| `TXT_ID_ELECT_D`    | Texto            | Char(15)      | —                        | Identificador electrónico inicial completo (calculado). |
| `DSP_COM_HASTA`     | Display item     | Char(2)       | —                        | Código de comunidad del identificador final. |
| `TXT_DIS_HASTA`     | Texto            | Char(10)      | LOV `LV_ANUL_RECEP_H`, valida desde lista | Número de dispositivo final del rango. |
| `TXT_ID_ELECT_H`    | Texto            | Char(15)      | —                        | Identificador electrónico final completo (calculado). |
| `DSP_N_DISP`        | Display item     | Number        | Valor inicial 0          | Total de dispositivos a anular en el rango (resaltado en verde). |
| `TXT_FECHA_ANULACION`| Texto (Date)    | Date          | `DD/MM/YYYY`, valor inicial `:PARAMETER.P_FECHA` | Fecha de anulación; no puede ser futura. |

**Composición del identificador electrónico** (regla de negocio clave):

```sql
TXT_ID_ELECT_D := DSP_COM_DESDE || LPAD(TXT_DIS_DESDE, 10, '0');
TXT_ID_ELECT_H := DSP_COM_HASTA || LPAD(TXT_DIS_HASTA, 10, '0');
```

Es decir: código de comunidad (2 caracteres) concatenado con el número de dispositivo
rellenado a 10 dígitos con ceros a la izquierda.

## Disparadores (lógica de negocio)

### Bloque `IA_ANU_DISPO`

**WHEN-NEW-ITEM-INSTANCE** — establece la barra de botones al entrar en cada item.

```sql
WHEN_NEW_ITEM_INSTANCE;

P_ESTABLECER_BOTONERA;
```

**KEY-LISTVAL** — al invocar la lista de valores, construye los identificadores electrónicos
inicial y final a partir del código de comunidad y el número de dispositivo (con `LPAD` a 10
dígitos) y luego lanza la LOV.

```sql
/************************************************************************************
* Funcionalidad: Validar campos que crean el identificadores y mostrar la lista de
*               valores de identicadores iniciales y finales.
*
* Proyecto RIIA - MEGG - 14/03/2006 - Desarrollo inicial
************************************************************************************/

IF :IA_ANU_DISPO.TXT_DIS_DESDE IS NULL THEN
    :IA_ANU_DISPO.TXT_ID_ELECT_D := NULL;
ELSE
    :IA_ANU_DISPO.TXT_ID_ELECT_D := :IA_ANU_DISPO.DSP_COM_DESDE || LPAD(:IA_ANU_DISPO.TXT_DIS_DESDE,10,'0');
END IF;

IF :IA_ANU_DISPO.TXT_DIS_HASTA IS NULL THEN
    :IA_ANU_DISPO.TXT_ID_ELECT_H := NULL;
ELSE
    :IA_ANU_DISPO.TXT_ID_ELECT_H := :IA_ANU_DISPO.DSP_COM_HASTA || LPAD(:IA_ANU_DISPO.TXT_DIS_HASTA,10,'0');
END IF;

LIST_VALUES;
```

**WHEN-NEW-BLOCK-INSTANCE** — carga la lista de especies al entrar en el bloque.

```sql
--Carga la lista de especies.
CARGAR_LISTA_ESPECIE('IA_ANU_DISPO.LST_ESPECIES');
```

### Item `LST_ESPECIES`

**WHEN-LIST-CHANGED** — al cambiar la especie, limpia todo el rango de dispositivos y el
contador (evita mezclar dispositivos de especies distintas).

```sql
:IA_ANU_DISPO.TXT_DIS_DESDE:=NULL;
:IA_ANU_DISPO.DSP_COM_DESDE:=NULL;
:IA_ANU_DISPO.TXT_DIS_HASTA:=NULL;
:IA_ANU_DISPO.DSP_COM_HASTA:=NULL;
:IA_ANU_DISPO.DSP_N_DISP:=0;
```

### Item `TXT_DIS_DESDE`

**WHEN-VALIDATE-ITEM** — valida el rango a partir del identificador inicial delegando en el
paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
* Proyecto RIIA - MEGG - 14/03/2006 - Desarrollo inicial
************************************************************************************/
IA_ANULAR_RECEP_PKG.P_ANULAR_IDEN_DESDE;
```

### Item `TXT_DIS_HASTA`

**WHEN-VALIDATE-ITEM** — valida el rango a partir del identificador final delegando en el
paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
* Proyecto RIIA - MEGG - 14/03/2006 - Desarrollo inicial
************************************************************************************/
IA_ANULAR_RECEP_PKG.P_ANULAR_IDEN_HASTA;
```

### Item `TXT_FECHA_ANULACION`

**WHEN-VALIDATE-ITEM** — valida que la fecha de anulación no sea posterior a la fecha del
sistema; si lo es, muestra alerta de error y aborta la operación.

```sql
/***********************************************************************************
* Funcionalidad: Validar la fecha de distribución.
* Proyecto RIIA - MEGG - 31/03/2006 - Desarrollo inicial
************************************************************************************/
DECLARE
  V_BOTON NUMBER;
  ID_ALERT ALERT;
BEGIN
  ID_ALERT := FIND_ALERT('ALERT_ERROR');

  if :IA_ANU_DISPO.TXT_FECHA_ANULACION > TRUNC(SYSDATE) THEN
     SET_ALERT_PROPERTY(ID_ALERT, ALERT_MESSAGE_TEXT, 'Esta fecha no puede ser mayor que la fecha del sitema');
     V_BOTON := SHOW_ALERT(ID_ALERT);
     RAISE FORM_TRIGGER_FAILURE;
  End if;
END;
```

## Validaciones de negocio

1. **Composición del identificador electrónico**: `código_comunidad (2) || LPAD(número_dispositivo, 10, '0')`.
   Se recalcula en `KEY-LISTVAL` antes de abrir la LOV.
2. **Coherencia de rango (identificador inicial)**: delegada a `IA_ANULAR_RECEP_PKG.P_ANULAR_IDEN_DESDE`
   en la validación de `TXT_DIS_DESDE`.
3. **Coherencia de rango (identificador final)**: delegada a `IA_ANULAR_RECEP_PKG.P_ANULAR_IDEN_HASTA`
   en la validación de `TXT_DIS_HASTA`.
4. **Consistencia por especie**: al cambiar `LST_ESPECIES` se borra el rango y el contador
   (`DSP_N_DISP = 0`), impidiendo anular dispositivos de una especie con datos de otra.
5. **Fecha de anulación no futura**: `TXT_FECHA_ANULACION` no puede ser mayor que
   `TRUNC(SYSDATE)`; en caso contrario se muestra la alerta `ALERT_ERROR` y se lanza
   `FORM_TRIGGER_FAILURE`.
6. **Validación contra lista**: `TXT_DIS_DESDE` y `TXT_DIS_HASTA` tienen "Validar desde Lista = Sí"
   contra las LOV `LV_ANUL_RECEP_D` y `LV_ANUL_RECEP_H` respectivamente.

## Llamadas a paquetes / procedimientos de BD

| Procedimiento / rutina                       | Parámetros                         | Origen (disparador)                    | Función |
|----------------------------------------------|------------------------------------|----------------------------------------|---------|
| `IA_ANULAR_RECEP_PKG.P_ANULAR_IDEN_DESDE`    | ninguno (usa items `:IA_ANU_DISPO.*`) | `TXT_DIS_DESDE` WHEN-VALIDATE-ITEM   | Valida el identificador inicial del rango. |
| `IA_ANULAR_RECEP_PKG.P_ANULAR_IDEN_HASTA`    | ninguno (usa items `:IA_ANU_DISPO.*`) | `TXT_DIS_HASTA` WHEN-VALIDATE-ITEM   | Valida el identificador final del rango. |
| `CARGAR_LISTA_ESPECIE`                        | `'IA_ANU_DISPO.LST_ESPECIES'`      | bloque WHEN-NEW-BLOCK-INSTANCE         | Rellena la lista desplegable de especies. |
| `P_ESTABLECER_BOTONERA`                       | ninguno                            | bloque WHEN-NEW-ITEM-INSTANCE          | Ajusta el estado de la barra de botones (rutina UI del form). |
| `WHEN_NEW_ITEM_INSTANCE`                      | ninguno                            | bloque WHEN-NEW-ITEM-INSTANCE          | Rutina genérica del form al entrar en un item. |

> Los procedimientos `P_ANULAR_IDEN_DESDE` / `P_ANULAR_IDEN_HASTA` no reciben argumentos
> explícitos: operan sobre los items del bloque (efecto lateral típico de Oracle Forms). Su
> definición reside en el paquete `IA_ANULAR_RECEP_PKG` (fuera de este rango; requiere el
> cuerpo del paquete para conocer las validaciones internas y el cálculo de `DSP_N_DISP`).

## Notas para la migración a Java

- **Model**: no hay entidad de BD directa en este bloque. El concepto de dominio es un
  **rango de dispositivos a anular** por especie: value objects `IdentificadorElectronico`
  (comunidad + número, con la regla `LPAD(numero,10,'0')`) y una operación de anulación con
  fecha. La entidad persistida real (recepción de dispositivos) vive tras `IA_ANULAR_RECEP_PKG`.
- **Repository**: encapsular las consultas de las LOV `LV_ANUL_RECEP_D` / `LV_ANUL_RECEP_H`
  (dispositivos disponibles para anular) y la carga de especies (`CARGAR_LISTA_ESPECIE`).
- **Service** (`@Service @Transactional`): trasladar aquí la lógica de
  `IA_ANULAR_RECEP_PKG.P_ANULAR_IDEN_DESDE` / `P_ANULAR_IDEN_HASTA` (validación de rango y
  cálculo del total `DSP_N_DISP`) y la operación de anulación. Requiere disponer del cuerpo
  del paquete para reproducirla con fidelidad.
- **Controller/Bean** (`@Component("anularDispoBean")`, `Serializable`):
  - Construcción del identificador electrónico completo (equivale a `KEY-LISTVAL`).
  - Al cambiar la especie, resetear rango y contador (equivale a `WHEN-LIST-CHANGED`).
  - Validación de fecha: la fecha de anulación no puede ser futura; sustituir la alerta
    `ALERT_ERROR` + `FORM_TRIGGER_FAILURE` por un `FacesMessage` de severidad ERROR y
    detención del flujo (`FacesContext.validationFailed()` o excepción de validación).
  - Valor inicial de la fecha proveniente de un parámetro (`:PARAMETER.P_FECHA`) → parámetro
    de entrada / atributo del bean.
- Corregir la errata del mensaje original ("sitema" → "sistema") al reescribir en Java.
- Las LOV con "Validar desde Lista" se mapean a validación server-side contra el repositorio
  correspondiente, además del autocompletado/selector en la vista PrimeFaces.

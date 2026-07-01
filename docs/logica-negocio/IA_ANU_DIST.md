# Formulario: IA_ANU_DIST

## Propósito

Bloque de datos **no basado en base de datos** (Bloque de Datos de Base de Datos = No) del formulario `IAAL0600`, denominado **Anular distribución**. Su función es capturar los criterios que permiten **anular una distribución** de dispositivos electrónicos (identificadores electrónicos) para una **especie** determinada, dentro de un **rango de identificadores** (desde/hasta) y con una **fecha de anulación**.

El bloque construye los identificadores electrónicos completos concatenando un componente de comunidad (`DSP_COM_*`) con el número de dispositivo (`TXT_DIS_*`) rellenado a 10 posiciones, delega la validación de rangos en el paquete de base de datos `IA_ANU_DIST_PKG`, calcula el total de dispositivos a anular (`DSP_N_DISP`) y valida que la fecha de anulación no sea futura.

## Items / campos de entrada relevantes

| Item | Tipo | Dato | Long. | Notas de lógica |
|------|------|------|-------|-----------------|
| `LST_ESPECIES` | Lista desplegable | Char | 50 | Especie objeto de la anulación. Se carga vía `CARGAR_LISTA_ESPECIE`. Al cambiar, resetea todos los campos del rango. |
| `DSP_COM_DESDE` | Display item | Char | 2 | Componente/comunidad del identificador inicial (se antepone al número). |
| `TXT_DIS_DESDE` | Texto | Char | 10 | Número de dispositivo inicial. LOV `LV_ANUL_DIST_D`, validado desde lista. |
| `TXT_ID_ELECT_D` | Texto | Char | 15 | Identificador electrónico inicial completo (calculado: `DSP_COM_DESDE || LPAD(TXT_DIS_DESDE,10,'0')`). |
| `DSP_COM_HASTA` | Display item | Char | 2 | Componente/comunidad del identificador final. |
| `TXT_DIS_HASTA` | Texto | Char | 10 | Número de dispositivo final. LOV `LV_ANUL_DIST_H`, validado desde lista. |
| `TXT_ID_ELECT_H` | Texto | Char | 15 | Identificador electrónico final completo (calculado: `DSP_COM_HASTA || LPAD(TXT_DIS_HASTA,10,'0')`). |
| `DSP_N_DISP` | Display item | Number | 40 | Total de dispositivos a anular. Valor inicial 0. Calculado por lógica del paquete. |
| `TXT_FECHA_ANULACION` | Texto | Date | 10 | Fecha de anulación. Valor inicial `:PARAMETER.P_FECHA`, máscara `DD/MM/YYYY`. Validada contra `SYSDATE`. |

## Disparadores (lógica de negocio)

### Bloque `IA_ANU_DIST`

**WHEN-NEW-ITEM-INSTANCE** — Al entrar en cada item del bloque. Reconfigura la botonera.

```sql
WHEN_NEW_ITEM_INSTANCE;

P_ESTABLECER_BOTONERA;
```

**KEY-LISTVAL** — Al invocar la lista de valores (LOV). Antes de mostrar la LOV, recalcula los identificadores electrónicos completos (desde/hasta) concatenando comunidad + número rellenado a 10 con ceros.

```sql
/************************************************************************************
* Funcionalidad: Validar campos que crean el identificadores y mostrar la lista de
*               valores de identicadores iniciales y finales.
*
* Proyecto         Autor             Fecha              Comentarios
* RIIA             MEGG              14/03/2006          Desarrollo inicial
************************************************************************************/

IF :IA_ANU_DIST.TXT_DIS_DESDE IS NULL THEN
    :IA_ANU_DIST.TXT_ID_ELECT_D := NULL;
ELSE
    :IA_ANU_DIST.TXT_ID_ELECT_D := :IA_ANU_DIST.DSP_COM_DESDE || LPAD(:IA_ANU_DIST.TXT_DIS_DESDE,10,'0');
END IF;

IF :IA_ANU_DIST.TXT_DIS_HASTA IS NULL THEN
      :IA_ANU_DIST.TXT_ID_ELECT_H := NULL;
ELSE
      :IA_ANU_DIST.TXT_ID_ELECT_H := :IA_ANU_DIST.DSP_COM_HASTA || LPAD(:IA_ANU_DIST.TXT_DIS_HASTA,10,'0');
END IF;

LIST_VALUES;
```

**WHEN-NEW-BLOCK-INSTANCE** — Al entrar en el bloque. Carga la lista de especies.

```sql
--Carga la lista de especies.
CARGAR_LISTA_ESPECIE('IA_ANU_DIST.LST_ESPECIES');
```

### Item `LST_ESPECIES`

**WHEN-LIST-CHANGED** — Al cambiar de especie. Limpia todos los campos del rango y el contador, forzando al usuario a reintroducir el rango para la nueva especie.

```sql
:IA_ANU_DIST.TXT_DIS_DESDE:=NULL;
:IA_ANU_DIST.DSP_COM_DESDE:=NULL;
:IA_ANU_DIST.TXT_DIS_HASTA:=NULL;
:IA_ANU_DIST.DSP_COM_HASTA:=NULL;
:IA_ANU_DIST.DSP_N_DISP:=0;
```

### Item `TXT_DIS_DESDE`

**WHEN-VALIDATE-ITEM** — Valida el rango del identificador inicial delegando en el paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
*
* Proyecto         Autor             Fecha              Comentarios
* RIIA             MEGG              14/03/2006          Desarrollo inicial
************************************************************************************/
IA_ANU_DIST_PKG.P_DIST_IDEN_DESDE;
```

### Item `TXT_DIS_HASTA`

**WHEN-VALIDATE-ITEM** — Valida el rango del identificador final delegando en el paquete de BD.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos.
*
* Proyecto         Autor             Fecha              Comentarios
* RIIA             MEGG              14/03/2006          Desarrollo inicial
************************************************************************************/
IA_ANU_DIST_PKG.P_DIST_IDEN_HASTA;
```

### Item `TXT_FECHA_ANULACION`

**WHEN-VALIDATE-ITEM** — Valida que la fecha de anulación no sea posterior a la fecha del sistema. Si lo es, muestra la alerta `ALERT_ERROR` y aborta con `FORM_TRIGGER_FAILURE`.

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

  if :IA_ANU_DIST.TXT_FECHA_ANULACION > TRUNC(SYSDATE) THEN

     SET_ALERT_PROPERTY(ID_ALERT, ALERT_MESSAGE_TEXT, 'Esta fecha no puede ser mayor que la fecha del sitema');
     V_BOTON := SHOW_ALERT(ID_ALERT);
     RAISE FORM_TRIGGER_FAILURE;

  End if;

END;
```

## Validaciones de negocio

1. **Construcción del identificador electrónico**: el identificador completo se forma como `COMUNIDAD || LPAD(NUM_DISPOSITIVO, 10, '0')` (comunidad de 2 posiciones + número relleno a 10 con ceros a la izquierda ⇒ longitud lógica de hasta 12; el campo destino admite hasta 15). Si el número (`TXT_DIS_*`) es nulo, el identificador (`TXT_ID_ELECT_*`) también queda nulo.
2. **Validación de rango desde/hasta**: los números de dispositivo inicial (`TXT_DIS_DESDE`) y final (`TXT_DIS_HASTA`) se validan mediante LOV (`LV_ANUL_DIST_D` / `LV_ANUL_DIST_H`) con "Validar desde Lista = Sí", y adicionalmente por los procedimientos `IA_ANU_DIST_PKG.P_DIST_IDEN_DESDE` / `P_DIST_IDEN_HASTA` que aplican la lógica de negocio del rango.
3. **Coherencia al cambiar de especie**: cambiar `LST_ESPECIES` invalida (pone a NULL/0) todo el rango y el contador, evitando anular con criterios de una especie distinta a la seleccionada.
4. **Fecha de anulación no futura**: `TXT_FECHA_ANULACION` no puede ser mayor que `TRUNC(SYSDATE)`. Regla obligatoria (bloquea la operación con `FORM_TRIGGER_FAILURE`). Valor por defecto tomado de `:PARAMETER.P_FECHA`.
5. **Total de dispositivos**: `DSP_N_DISP` refleja el número de dispositivos incluidos en el rango a anular (mostrado, no editable; inicial 0).

## Llamadas a paquetes / procedimientos de BD

| Llamada | Origen (disparador) | Parámetros | Función |
|---------|---------------------|------------|---------|
| `IA_ANU_DIST_PKG.P_DIST_IDEN_DESDE` | `TXT_DIS_DESDE` · WHEN-VALIDATE-ITEM | ninguno (usa items del bloque) | Valida el identificador/rango inicial de la distribución. |
| `IA_ANU_DIST_PKG.P_DIST_IDEN_HASTA` | `TXT_DIS_HASTA` · WHEN-VALIDATE-ITEM | ninguno (usa items del bloque) | Valida el identificador/rango final de la distribución. |
| `CARGAR_LISTA_ESPECIE('IA_ANU_DIST.LST_ESPECIES')` | Bloque · WHEN-NEW-BLOCK-INSTANCE | nombre del item lista (`'IA_ANU_DIST.LST_ESPECIES'`) | Rellena la lista desplegable de especies (procedimiento de programa del formulario). |

Rutinas de formulario invocadas (no BD): `WHEN_NEW_ITEM_INSTANCE`, `P_ESTABLECER_BOTONERA` (gestión de botonera), y builtins Forms `LIST_VALUES`, `FIND_ALERT`, `SET_ALERT_PROPERTY`, `SHOW_ALERT`.

## Notas para la migración a Java

- **Capa Model**: el bloque no es de BD, por lo que no genera entidad propia. Modelar un **DTO/comando** `AnularDistribucionCommand` con: `especie`, `comunidadDesde`, `numeroDispositivoDesde`, `idElectronicoDesde`, `comunidadHasta`, `numeroDispositivoHasta`, `idElectronicoHasta`, `totalDispositivos`, `fechaAnulacion`. Los identificadores electrónicos son **derivados** (calculados), no de entrada libre.
- **Capa Service** (`@Service @Transactional`): trasladar la lógica de `IA_ANU_DIST_PKG.P_DIST_IDEN_DESDE` / `P_DIST_IDEN_HASTA` a métodos de validación de rango (p. ej. `validarIdentificadorDesde` / `validarIdentificadorHasta`) y un método `anularDistribucion(command)`. El cálculo del identificador electrónico (`comunidad + String.format("%010d", numero)`, equivalente a `LPAD(...,10,'0')`) es lógica de dominio, ubicarlo en el Value Object del identificador o en el service.
- **Capa Repository** (`@Repository` + `EntityManager`): las LOV `LV_ANUL_DIST_D` / `LV_ANUL_DIST_H` y `CARGAR_LISTA_ESPECIE` corresponden a consultas de lookup (JPQL/nativas) para poblar selects de identificadores y de especies.
- **Capa Bean/Controller** (`@Component("...Bean")` + `@Scope`): 
  - `WHEN-LIST-CHANGED` de especie ⇒ listener que resetea el rango y el contador al cambiar la especie seleccionada.
  - `WHEN-VALIDATE-ITEM` de fecha ⇒ **validación "fecha no futura"**: en Java lanzar excepción de validación / `FacesMessage` de error en lugar de `RAISE FORM_TRIGGER_FAILURE`. Nota: el texto original tiene una errata ("sitema" en vez de "sistema"); corregir a "Esta fecha no puede ser mayor que la fecha del sistema".
  - `:PARAMETER.P_FECHA` (valor inicial de la fecha) ⇒ parámetro de entrada/estado de la vista.
- **Alertas Forms** (`FIND_ALERT`/`SHOW_ALERT`) ⇒ mensajes JSF/PrimeFaces (`FacesMessage` o `p:messages`/growl).
- **Botonera** (`P_ESTABLECER_BOTONERA`, `WHEN-NEW-ITEM-INSTANCE`) ⇒ lógica de habilitación/deshabilitación de botones en el bean según el estado del formulario.
- **Validaciones de LOV** ("Validar desde Lista = Sí") ⇒ garantizar en el service que los valores seleccionados existan en el catálogo antes de procesar.

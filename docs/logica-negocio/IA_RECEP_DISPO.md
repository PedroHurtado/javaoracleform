# Formulario: IA_RECEP_DISPO

> Bloque de datos del formulario Oracle Forms `IAAL0600` (proyecto RIIA / RIIA_EQUINO).
> Rango en el volcado de texto: líneas 3519–5289.
> Autor original: MEGG (2006).

## Propósito

El bloque **IA_RECEP_DISPO** ("Recepción de dispositivos electrónicos, en lote")
representa la pantalla donde el usuario da de alta la **recepción por lotes de
identificadores electrónicos** (crotales/bolos electrónicos) para animales de
ganadería (ovino, caprino, camélidos, cérvidos, equino…).

El usuario:

1. Selecciona la **especie** (`LST_ESPECIES`), lo que determina qué **tipos de
   dispositivo** son válidos (la lista `LST_TIPO_DISPOSITIVOS` se recarga en
   función de la especie) y de qué comunidad autónoma proviene.
2. Indica **fabricante** (`TXT_ICAR`) **o** **proveedor** (`TXT_PROVEEDOR`), que
   son mutuamente excluyentes (no pueden coexistir).
3. Indica la **norma de fabricación** (`LST_NORMAS`), el **país** de origen
   (`TXT_NOMBRE_PAIS` / `DSP_COD_PAIS`, por defecto España / 0724 / ES).
4. Introduce el **rango de identificadores a recibir** (el último identificador
   del lote, `TXT_DIS_HASTA`), que se normaliza al formato `04NNNNNNNN` y se
   valida.
5. Indica la **fecha de recepción** (`TXT_FECHA_RECEPCION`), que no puede ser
   futura.

El bloque muestra además datos calculados/informativos: el **último dispositivo
recibido** (`DSP_ULTIMO_DISP`) y el **total de dispositivos** del lote
(`DSP_N_DISP`).

La lógica de negocio pesada (carga de valores, cálculo del máximo identificador,
validación de rangos) reside en el paquete de base de datos
**`IA_RECEPCION_ID_PKG`**, que el bloque invoca en varios disparadores.

## Items / campos de entrada relevantes

| Item | Tipo | Dato | Descripción / papel en la lógica |
|------|------|------|----------------------------------|
| `LST_ESPECIES` | Lista desplegable | Char(50) | Especie animal. Determina el record group de tipos de dispositivo y la comunidad (`DSP_COMUNIDAD`). Valores conocidos: `'01'` (equino → `RG_TIP_DISP_EQ`), `'04'` (ovino/caprino → `RG_TIP_DISP`), otros p.ej. `'06'` (camélidos/cérvidos → `RG_TIP_DISP_CAM_CER`). |
| `LST_TIPO_DISPOSITIVOS` | Lista desplegable | Char(50) | Tipo de dispositivo. Se llena dinámicamente por `POPULATE_LIST` según especie. |
| `LST_NORMAS` | Lista desplegable | Char(50) | Norma de fabricación del dispositivo. |
| `TXT_ICAR` | Texto + LOV `LV_ICAR` | Char(100) | Fabricante (código ICAR). Excluyente con proveedor. Valida desde lista. |
| `TXT_ID_ICAR` | Texto (oculto) | Char(2) | Id interno del fabricante seleccionado. |
| `TXT_PROVEEDOR` | Texto + LOV `LV_PROVEEDORES` | Char(50) | Proveedor. Excluyente con fabricante. Valida desde lista. |
| `TXT_ID_PROVEEDOR` | Texto (oculto) | Number(3) | Id interno del proveedor seleccionado. |
| `DSP_COD_PAIS` | Display | Char(4) | Código de país. Valor inicial `0724` (España). Se anula si el nombre de país es nulo. |
| `TXT_NOMBRE_PAIS` | Display | Char(50) | Nombre del país. Valor inicial `ESPAÑA`. |
| `TXT_L_PAIS` | Texto | Char(2) | Código ISO del país. Valor inicial `ES`. |
| `DSP_COMUNIDAD` | Display | Char(2) | Código de comunidad autónoma, derivado de la especie. |
| `TXT_DIS_HASTA` | Texto | Char(10) | Último identificador electrónico del lote a recibir. Se normaliza a `04NNNNNNNN` y se valida numéricamente + contra el paquete. |
| `DSP_ULTIMO_DISP` | Display | Char(15) | Último dispositivo ya recibido (obtenido de `F_MAX_IDEN`). |
| `DSP_N_DISP` | Display | Number(40) | Total de dispositivos del lote. Valor inicial `0`. |
| `TXT_FECHA_RECEPCION` | Texto | Date(DD/MM/YYYY) | Fecha de recepción. Valor inicial `:PARAMETER.P_FECHA`. No puede ser posterior a `SYSDATE`. |

LOVs implicadas: `LV_ICAR` (fabricantes), `LV_PROVEEDORES` (proveedores).
Record groups implicados: `RG_TIP_DISP_EQ`, `RG_TIP_DISP`, `RG_TIP_DISP_CAM_CER`.

## Disparadores (lógica de negocio)

### WHEN-NEW-BLOCK-INSTANCE (bloque IA_RECEP_DISPO)

Al entrar en el bloque, carga los valores iniciales de combos y listas de valores
mediante el paquete de recepción (con parámetro `0`).

```sql
/************************************************************************************
* Funcionalidad: Inserción de valores para los combos y las listas de valores.
*
* Modificaciones
* --------------
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              09/03/2006          Desarrollo inicial
************************************************************************************/

IA_RECEPCION_ID_PKG.P_CARGAR_VALORES_RECEPCION(0);
```

### WHEN-NEW-ITEM-INSTANCE (bloque IA_RECEP_DISPO)

Al posicionarse en cualquier item del bloque: si la variable global
`CAMBIADO_DIS_HASTA` está activa (=1), fuerza volver al item `TXT_DIS_HASTA`
(porque su valor cambió y hay que revalidar). Después reestablece el estado de la
botonera. Invoca primero un `WHEN_NEW_ITEM_INSTANCE;` (procedimiento de programa
común del formulario) y luego `P_ESTABLECER_BOTONERA`.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos a recibir.
*
* Modificaciones
* --------------
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              14/03/2006          Desarrollo inicial
************************************************************************************/
WHEN_NEW_ITEM_INSTANCE;

-- Volver al mismo iten si la variable ha cambiado de valor. Identificador hasta a recibir.
IF :GLOBAL.CAMBIADO_DIS_HASTA = 1  then
     GO_ITEM('IA_RECEP_DISPO.TXT_DIS_HASTA');
     :GLOBAL.CAMBIADO_DIS_HASTA := 0;
END IF;

-- Establecer el estado de los botonos de la botonera.
P_ESTABLECER_BOTONERA;
```

### WHENCREATERECORD (WHEN-CREATE-RECORD, bloque IA_RECEP_DISPO)

Al crear un registro, carga en `DSP_ULTIMO_DISP` el máximo identificador ya
insertado, obtenido de la función `F_MAX_IDEN` del paquete.

```sql
--Carga del máximo identificador insertado.--------------------------
 :IA_RECEP_DISPO.DSP_ULTIMO_DISP := IA_RECEPCION_ID_PKG.F_MAX_IDEN;--
---------------------------------------------------------------------
```

### WHEN-LIST-CHANGED (item LST_ESPECIES)

Núcleo de la carga dinámica dependiente de la especie. Al cambiar la especie:

1. Selecciona el **record group** de tipos de dispositivo según especie
   (`'01'` equino, `'04'` ovino/caprino, resto `'06'` camélidos/cérvidos).
2. Si hay especie seleccionada, obtiene el **código de comunidad**
   (`DSP_COMUNIDAD`) de `IA_ESPECIES_NACIONAL` y refresca el máximo identificador
   (`DSP_ULTIMO_DISP` = `F_MAX_IDEN`); si no, los anula.
3. Recarga la lista `LST_TIPO_DISPOSITIVOS` con `POPULATE_GROUP` +
   `POPULATE_LIST`, mostrando error si la carga del grupo falla.

```sql
DECLARE

	  ID_ALERT   ALERT;  -- Identificador de la alerta.
    V_BOTON    NUMBER; -- Botón pinchado cuando se muestra alerta.
    V_STATUS   NUMBER; -- Estado de la carga del registro

    ID_RGROUP RECORDGROUP; --Identificador del registro.
    ID_LIST   ITEM;  -- Identificador de lista.

BEGIN
		-- 2ª Carga de tipos de dispositivos.

		-- RIIA_EQUINO: No cargamos los tipos de dispositivo en el WHEN NEW BLOCK INSTANCE, porque dependen de la especie.
		-- Los cargamos en la lista de especies. Comentamos por tanto la carga de dispositivos el paquete
		-- IA_RECEPCION_ID_PKG.P_CARGAR_VALORES_RECEPCION;

		IF :IA_RECEP_DISPO.LST_ESPECIES = '01' THEN
			ID_RGROUP := FIND_GROUP('RG_TIP_DISP_EQ');
		ELSIF	:IA_RECEP_DISPO.LST_ESPECIES = '04' THEN--> ovino/caprino
			ID_RGROUP := FIND_GROUP('RG_TIP_DISP');
    ELSE	--(06)--> camélidos y cérvidos
			ID_RGROUP := FIND_GROUP('RG_TIP_DISP_CAM_CER');
		END IF;

    If :IA_RECEP_DISPO.LST_ESPECIES Is Not Null Then
       SELECT EN.SPCN_CODIGO
         INTO :IA_RECEP_DISPO.DSP_COMUNIDAD
         FROM SGISIBEXT.IA_ESPECIES_NACIONAL EN
        WHERE SUBSTR(EN.SPCN_CODIGO,2,1) = SUBSTR(:IA_RECEP_DISPO.LST_ESPECIES,2,1);

	     --Carga del máximo identificador insertado.-------------------------
       :IA_RECEP_DISPO.DSP_ULTIMO_DISP := IA_RECEPCION_ID_PKG.F_MAX_IDEN;
    Else
    	:IA_RECEP_DISPO.DSP_COMUNIDAD := null;
    	:IA_RECEP_DISPO.DSP_ULTIMO_DISP := null;
    End If;


    ID_LIST := FIND_ITEM('IA_RECEP_DISPO.LST_TIPO_DISPOSITIVOS');

    CLEAR_LIST(ID_LIST);

    V_STATUS := POPULATE_GROUP(ID_RGROUP);

    IF V_STATUS = 0 THEN

       CLEAR_LIST(ID_LIST);
       POPULATE_LIST(ID_LIST, ID_RGROUP);

    ELSE

    	 MESSAGE('Error: No se han podido cargar los tipos de dispositivos');

    END IF;

END;
```

### WHEN-VALIDATE-ITEM (item TXT_ICAR — fabricante)

Regla de exclusión fabricante/proveedor. Si `TXT_ICAR` es nulo limpia su id.
Si hay **proveedor** y **fabricante** a la vez, muestra alerta y **anula el
fabricante** (prevalece el proveedor).

```sql
/************************************************************************************
* Funcionalidad: validacion de fabricante y poveedores.
*
* Modificaciones
* --------------
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              09/03/2006          Desarrollo inicial
************************************************************************************/
DECLARE

  ID_ALERT ALERT;
  V_BOTON VARCHAR2(2);

BEGIN

		IF :IA_RECEP_DISPO.TXT_ICAR IS NULL THEN
		    :IA_RECEP_DISPO.TXT_ID_ICAR := NULL;
		END IF;

		IF :IA_RECEP_DISPO.TXT_PROVEEDOR IS NOT NULL
			    AND
			 :IA_RECEP_DISPO.TXT_ICAR IS NOT NULL THEN

			  SET_ALERT_PROPERTY('F__PLA_MENSAJE_1',ALERT_MESSAGE_TEXT,
		                       'Si existe proveedor no puede existir fabricante.');
		    ID_ALERT := FIND_ALERT('F__PLA_MENSAJE_1');
		  	V_BOTON := SHOW_ALERT(ID_ALERT);


			 :IA_RECEP_DISPO.TXT_ICAR := NULL;
			 :IA_RECEP_DISPO.TXT_ID_ICAR := NULL;

		END IF;

END;
```

### WHEN-VALIDATE-ITEM (item TXT_PROVEEDOR — proveedor)

Regla simétrica de exclusión. Si `TXT_PROVEEDOR` es nulo limpia su id.
Si hay **fabricante** y **proveedor** a la vez, muestra alerta y **anula el
proveedor** (prevalece el fabricante). Nota: esta regla es la inversa de la de
`TXT_ICAR`, por lo que el item que se valide en último lugar es el que gana.

```sql
/************************************************************************************
* Funcionalidad: validacion de fabricante y poveedores.
*
* Modificaciones
* --------------
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              09/03/2006          Desarrollo inicial
************************************************************************************/
DECLARE

  ID_ALERT ALERT;
  V_BOTON VARCHAR2(2);

BEGIN

    IF :IA_RECEP_DISPO.TXT_PROVEEDOR IS NULL THEN
    	    :IA_RECEP_DISPO.TXT_ID_PROVEEDOR := NULL;
    END IF;


		IF :IA_RECEP_DISPO.TXT_ICAR IS NOT NULL
			   AND
			 :IA_RECEP_DISPO.TXT_PROVEEDOR IS NOT NULL THEN

			  SET_ALERT_PROPERTY('F__PLA_MENSAJE_1',ALERT_MESSAGE_TEXT,
		                       'Si existe fabricante no puede existir proveedor.');
		    ID_ALERT := FIND_ALERT('F__PLA_MENSAJE_1');
		  	V_BOTON := SHOW_ALERT(ID_ALERT);


			 :IA_RECEP_DISPO.TXT_PROVEEDOR := NULL;
			 :IA_RECEP_DISPO.TXT_ID_PROVEEDOR := NULL;

		END IF;

END;
```

### WHEN-VALIDATE-ITEM (item TXT_NOMBRE_PAIS — país)

Si el nombre de país queda nulo, se anula también su código.

```sql
/************************************************************************************
* Funcionalidad: Si el nombre del pais es nulo no se inserta el código.
*
* Modificaciones
* --------------
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              09/03/2006          Desarrollo inicial
************************************************************************************/
IF :IA_RECEP_DISPO.TXT_NOMBRE_PAIS IS NULL THEN
     :IA_RECEP_DISPO.DSP_COD_PAIS := NULL;
END IF;
```

### WHEN-VALIDATE-ITEM (item TXT_DIS_HASTA — último identificador a recibir)

Disparador clave. Normaliza el identificador introducido al formato canónico de
10 dígitos con prefijo `04`, valida que sea numérico y con el prefijo correcto, y
finalmente delega en el paquete la validación del rango de identificadores a
recibir (`P_VALIDAR_IDENT_RECEP(0)`).

Reglas de normalización según longitud de entrada:
- 10 → tal cual.
- 9 → `LPAD` con ceros a la izquierda hasta 10.
- 8 → prefijo `'04'` + valor.
- otra longitud → `'04'` + `LPAD` a 8.

```sql
/************************************************************************************
* Funcionalidad: Validar los identificadores electrónicos a insertar.
*
* Modificaciones
* --------------
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              09/03/2006          Desarrollo inicial
************************************************************************************/
IF :IA_RECEP_DISPO.TXT_DIS_HASTA IS NOT NULL THEN
	DECLARE
		DISPOSITIVO_NUM NUMBER;
	BEGIN
		Select Decode(Length(:IA_RECEP_DISPO.TXT_DIS_HASTA),10,:IA_RECEP_DISPO.TXT_DIS_HASTA
		                                                   ,9,LPAD(:IA_RECEP_DISPO.TXT_DIS_HASTA,10,'0')
		                                                   ,8,'04'||:IA_RECEP_DISPO.TXT_DIS_HASTA,
		                                                   '04'||LPAD(:IA_RECEP_DISPO.TXT_DIS_HASTA,8,'0'))
		  Into :IA_RECEP_DISPO.TXT_DIS_HASTA
		  From dual;

  	SELECT TO_NUMBER(:IA_RECEP_DISPO.TXT_DIS_HASTA)
  	INTO DISPOSITIVO_NUM
  	FROM DUAL;
 	EXCEPTION
 	  WHEN invalid_number THEN
	     ALERTA('F__PLA_MENSAJE_4', 'El dispositivo introducido no es numérico.', NULL, 1);
 	END;

	IF(:IA_RECEP_DISPO.TXT_DIS_HASTA NOT LIKE '04%') THEN
	   ALERTA('F__PLA_MENSAJE_4', 'El dispositivo introducido no es válido (04NNNNNNNN)', NULL, 1);
	END IF;

 	IA_RECEPCION_ID_PKG.P_VALIDAR_IDENT_RECEP(0);
END IF;
```

### WHEN-VALIDATE-ITEM (item TXT_FECHA_RECEPCION — fecha de recepción)

La fecha de recepción no puede ser posterior a la fecha del sistema. Si lo es,
muestra alerta de error y aborta la validación con `RAISE FORM_TRIGGER_FAILURE`.

```sql
/************************************************************************************
* Funcionalidad: Validación de la fecha de recepción.
*
* Modificaciones
* --------------
* Proyecto         Autor             Fecha              Comentarios
* --------------   ----------------  -----------------  ---------------------------
* RIIA             MEGG              31/03/2006          Desarrollo inicial
************************************************************************************/
DECLARE

  V_BOTON NUMBER;
  ID_ALERT ALERT;

BEGIN

  ID_ALERT := FIND_ALERT('ALERT_ERROR');

  IF :IA_RECEP_DISPO.TXT_FECHA_RECEPCION > TRUNC(SYSDATE) THEN

     SET_ALERT_PROPERTY(ID_ALERT, ALERT_MESSAGE_TEXT, 'Esta fecha no puede ser mayor que la fecha del sistema');
     V_BOTON := SHOW_ALERT(ID_ALERT);
     RAISE FORM_TRIGGER_FAILURE;

  END IF;

END;
```

## Validaciones de negocio

1. **Especie determina tipos de dispositivo válidos**: la lista de tipos de
   dispositivo depende de la especie seleccionada (equino / ovino-caprino /
   camélidos-cérvidos), cargándose desde distintos record groups.
2. **Comunidad derivada de la especie**: `DSP_COMUNIDAD` se obtiene de
   `IA_ESPECIES_NACIONAL` comparando el 2.º carácter del código de especie.
3. **Fabricante y proveedor son mutuamente excluyentes**: no puede haber
   fabricante (`TXT_ICAR`) y proveedor (`TXT_PROVEEDOR`) simultáneamente; al
   detectarse ambos se anula uno de ellos (el último validado prevalece).
4. **Nombre de país nulo ⇒ código de país nulo** (consistencia país/código).
5. **Formato del identificador electrónico**: se normaliza a `04NNNNNNNN`
   (10 dígitos, prefijo `04`); debe ser numérico y empezar por `04`; en caso
   contrario se muestran mensajes de error (`F__PLA_MENSAJE_4`).
6. **Validación de rango de identificadores**: delegada a
   `IA_RECEPCION_ID_PKG.P_VALIDAR_IDENT_RECEP(0)` sobre el identificador
   normalizado.
7. **Fecha de recepción no futura**: `TXT_FECHA_RECEPCION` no puede ser mayor que
   `TRUNC(SYSDATE)`; si lo es se aborta con `FORM_TRIGGER_FAILURE`.
8. **Reentrada forzada al item de identificador**: si la global
   `CAMBIADO_DIS_HASTA` está activa, se obliga a volver a `TXT_DIS_HASTA` para
   revalidar.

## Llamadas a paquetes / procedimientos de BD

| Rutina | Tipo | Parámetros | Uso / disparador |
|--------|------|------------|------------------|
| `IA_RECEPCION_ID_PKG.P_CARGAR_VALORES_RECEPCION` | Procedimiento | `(0)` | Carga inicial de combos y LOVs (WHEN-NEW-BLOCK-INSTANCE). |
| `IA_RECEPCION_ID_PKG.F_MAX_IDEN` | Función | (sin parámetros) | Devuelve el máximo identificador ya insertado; usado en WHENCREATERECORD y WHEN-LIST-CHANGED para `DSP_ULTIMO_DISP`. |
| `IA_RECEPCION_ID_PKG.P_VALIDAR_IDENT_RECEP` | Procedimiento | `(0)` | Valida el rango de identificadores a recibir (WHEN-VALIDATE-ITEM de `TXT_DIS_HASTA`). |
| `P_ESTABLECER_BOTONERA` | Procedimiento de programa (Form) | (sin parámetros) | Establece el estado de los botones de la botonera (WHEN-NEW-ITEM-INSTANCE). |
| `WHEN_NEW_ITEM_INSTANCE` | Procedimiento de programa (Form) | (sin parámetros) | Lógica común compartida al posicionarse en un item. |
| `ALERTA` | Procedimiento auxiliar (Form) | `(nombre_alerta, mensaje, ?, tipo)` | Muestra alertas de error de validación del identificador. |

Consulta directa a tabla (dentro de WHEN-LIST-CHANGED):
`SELECT EN.SPCN_CODIGO FROM SGISIBEXT.IA_ESPECIES_NACIONAL EN WHERE SUBSTR(EN.SPCN_CODIGO,2,1) = SUBSTR(:LST_ESPECIES,2,1)`.

Parámetros/globales del formulario referenciados: `:PARAMETER.P_FECHA` (fecha por
defecto de recepción), `:GLOBAL.CAMBIADO_DIS_HASTA` (flag de cambio del
identificador). Alertas usadas: `F__PLA_MENSAJE_1`, `F__PLA_MENSAJE_4`,
`ALERT_ERROR`.

## Notas para la migración a Java (capa sugerida: Service/Controller/Repository)

**Model / Entity (`model`)**
- Una entidad de **recepción de dispositivos** (agregado raíz del lote de
  recepción) con: especie, tipo de dispositivo, norma, fabricante/proveedor
  (uno u otro), país (código + nombre + ISO), comunidad, identificador hasta,
  total de dispositivos, fecha de recepción.
- Value object `IdentificadorElectronico` que encapsule la normalización a
  `04NNNNNNNN` y su validación (numérico + prefijo). El código de especie y de
  comunidad también son buenos candidatos a value objects.
- Entidad de referencia `EspecieNacional` (tabla `IA_ESPECIES_NACIONAL`,
  columna `SPCN_CODIGO`) para derivar la comunidad.

**Repository (`repository`)**
- `EspecieNacionalRepository`: consulta que deriva el código de comunidad a
  partir del código de especie (`SUBSTR(SPCN_CODIGO,2,1) = SUBSTR(especie,2,1)`).
- Método `findMaxIdentificador()` que sustituya a `F_MAX_IDEN`.
- Repositorios/consultas para los catálogos que hoy alimentan los record groups
  (`RG_TIP_DISP_EQ`, `RG_TIP_DISP`, `RG_TIP_DISP_CAM_CER`) y las LOVs
  (`LV_ICAR` fabricantes, `LV_PROVEEDORES` proveedores).

**Service (`service`, `@Transactional`)**
- Transponer `IA_RECEPCION_ID_PKG`:
  - `cargarValoresRecepcion()` ← `P_CARGAR_VALORES_RECEPCION`.
  - `maxIdentificador()` ← `F_MAX_IDEN`.
  - `validarIdentificadorRecepcion(...)` ← `P_VALIDAR_IDENT_RECEP` (validación de
    rango; probablemente comprueba solapes con lotes previos).
- Reglas de negocio como métodos de validación del servicio:
  exclusión fabricante/proveedor, consistencia país/código, formato del
  identificador, fecha no futura. Estas deben lanzar excepciones de validación
  (equivalentes al `FORM_TRIGGER_FAILURE` / alertas), a mapear a mensajes de UI.
- La selección del catálogo de tipos de dispositivo según especie es lógica de
  servicio (mapear `'01'/'04'/otros` → conjunto de tipos), no de presentación.

**Controller / Bean JSF (`bean`)**
- Bean `#{recepDispositivosBean}` (`@Component` + `@Scope`), `Serializable`.
- Eventos AJAX de PrimeFaces que reemplacen los disparadores de UI:
  - Cambio de especie (WHEN-LIST-CHANGED) → recargar lista de tipos y refrescar
    comunidad + último dispositivo.
  - Validaciones `WHEN-VALIDATE-ITEM` → validadores JSF o llamadas al service en
    los eventos `blur`/`valueChange` de fabricante, proveedor, país, identificador
    y fecha.
  - Inicialización (WHEN-NEW-BLOCK-INSTANCE / WHENCREATERECORD) → `@PostConstruct`
    / método de "nuevo registro" que cargue valores por defecto (país España
    `0724`/`ES`, fecha `P_FECHA`, último dispositivo, total 0).
- El flag `CAMBIADO_DIS_HASTA` y la botonera (`P_ESTABLECER_BOTONERA`) son estado
  de UI que se resuelve con el ciclo de vida del bean y `rendered`/`disabled` de
  los botones; no requieren global de sesión.

# Formulario: IA_RECEP_DISPO_INDIV

> Bloque del formulario Oracle Forms `IAAL0600` (fichero `oracle/IAAL0600.txt`, líneas 5291–6853).
> Proyecto RIIA. Autor original: MEGG (2006).

## Propósito

Bloque de **recepción individual de dispositivos** (identificadores electrónicos de
ganado). Permite dar de alta, uno a uno, los dispositivos que se reciben en el
almacén: se selecciona la especie, el tipo de dispositivo, la norma de fabricación,
el fabricante o el proveedor, y se introduce el identificador electrónico del
dispositivo junto con la fecha de recepción. El bloque valida los rangos de
identificadores electrónicos y controla la exclusión mutua entre fabricante y
proveedor.

Características del bloque (líneas 5291–5361):

- **No es un bloque de base de datos** (`Bloque de Datos de Base de Datos = No`);
  actúa como bloque de control/entrada. La persistencia se delega en el paquete
  PL/SQL `IA_RECEPCION_ID_PKG`.
- Inserción y actualización permitidas; **borrado no permitido**.
- Consulta no permitida. Un solo registro mostrado.
- Lienzo asociado: `CV_RECEPCION_INDIV`.

## Items / campos de entrada relevantes

| Item | Tipo | Datos | Detalle relevante para la lógica |
|------|------|-------|----------------------------------|
| `LST_ESPECIES` | Lista desplegable | Char(50) | Especie. `'01'` = equino (bovino/EQ); otros (`'04'`) = ovino/caprino. Determina el grupo de registros de tipos de dispositivo. Prompt "Especie". |
| `TXT_ICAR` | Texto + LOV `LV_ICAR_INDIV` | Char(100) | Fabricante (ICAR). Validado desde lista. Excluyente con proveedor. Prompt "Fabricante". |
| `TXT_ID_ICAR` | Texto (oculto/soporte) | Char(2) | Identificador del fabricante ICAR. Se pone a NULL cuando `TXT_ICAR` es NULL. |
| `TXT_PROVEEDOR` | Texto + LOV `LV_PROVEEDORES_INDIV` | Char(50) | Proveedor. Validado desde lista. Excluyente con fabricante. Prompt "Prooveedor" (sic). |
| `TXT_ID_PROVEEDOR` | Texto (soporte) | Number(3) | Identificador del proveedor. Se pone a NULL cuando `TXT_PROVEEDOR` es NULL. |
| `LST_TIPO_DISPOSITIVOS` | Lista desplegable | Char(50) | Tipo de dispositivo. Se rellena dinámicamente según la especie (grupos `RG_TIP_DISP_EQ` / `RG_TIP_DISP`). Prompt "Tipo de dispositivo". |
| `LST_NORMAS` | Lista desplegable | Char(50) | Norma de fabricación. Prompt "Norma de fabricación". |
| `DISP_ELECTRONICO` | Texto | Char(23), longitud fija | Identificador electrónico del dispositivo a recibir. Se valida contra el paquete de recepción. Prompt "Dispositivo a Recibir". |
| `TXT_FECHA_RECEPCION` | Texto | Date, máscara `DD/MM/YYYY` | Fecha de recepción. Valor inicial `:PARAMETER.P_FECHA`. No puede ser posterior a la fecha del sistema. Prompt "Fecha de recepción". |
| `DSP_ULTIMO_DISP` | Display item | Number(12), fmt `FM099999999999` | Solo visualización: último dispositivo recibido. |
| `DSP_N_DISP` | Display item | Number, valor inicial 0 | Solo visualización: total de dispositivos recibidos (no visible). |
| `DSP_COD_PAIS` | Texto | Char(4), obligatorio, no visible | Código de país (soporte). Inserción/actualización no permitidas. |
| `TXT_L_PAIS` | Texto | Char(2), no visible | Literal/código de país (soporte). |

## Disparadores (lógica de negocio)

### Bloque `IA_RECEP_DISPO_INDIV`

#### WHEN-NEW-BLOCK-INSTANCE (líneas 5363–5388)
Al entrar en el bloque, carga los valores de combos y listas de valores mediante
el paquete de recepción (parámetro `1`).

```sql
/************************************************************************************
* Funcionalidad: Inserción de valores para los combos y las listas de valores.
************************************************************************************/
IA_RECEPCION_ID_PKG.P_CARGAR_VALORES_RECEPCION(1);
```

#### WHEN-NEW-ITEM-INSTANCE (líneas 5390–5415)
Al cambiar de item, valida rangos y actualiza el estado de los botones de la
botonera.

```sql
/************************************************************************************
* Funcionalidad: Validar rangos de identificadores electrónicos a recibir.
************************************************************************************/
WHEN_NEW_ITEM_INSTANCE;
-- Establecer el estado de los botones de la botonera.
P_ESTABLECER_BOTONERA;
```

### Item `LST_ESPECIES`

#### WHEN-LIST-CHANGED (líneas 5576–5623)
Al cambiar la especie, recarga dinámicamente la lista de tipos de dispositivos
según sea equino (`'01'`, grupo `RG_TIP_DISP_EQ`) u ovino/caprino (grupo
`RG_TIP_DISP`).

```sql
DECLARE
	  
	  ID_ALERT   ALERT;  -- Identificador de la alerta.
    V_BOTON    NUMBER; -- Botón pinchado cuando se muestra alerta.
    V_STATUS   NUMBER; -- Estado de la carga del registro
  
    ID_RGROUP RECORDGROUP; --Identificador del registro.
    ID_LIST   ITEM;  -- Identificador de lista.
    
BEGIN
		-- 2ª Carga de tipos de dispositivos.			
		IF :IA_RECEP_DISPO_INDIV.LST_ESPECIES = '01' THEN		
			ID_RGROUP := FIND_GROUP('RG_TIP_DISP_EQ');
		ELSE	--(04)--> ovino/caprino
			ID_RGROUP := FIND_GROUP('RG_TIP_DISP');
		END IF;	
		
   ID_LIST := FIND_ITEM('IA_RECEP_DISPO_INDIV.LST_TIPO_DISPOSITIVOS');
		
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

### Item `TXT_ICAR` (Fabricante)

#### WHEN-VALIDATE-ITEM (líneas 5726–5776)
Valida fabricante frente a proveedor. Si el fabricante queda NULL, limpia su
identificador. Si hay proveedor **y** fabricante, muestra alerta ("Si existe
proveedor no puede existir fabricante") y **anula el fabricante** (exclusión mutua:
gana el proveedor).

```sql
/************************************************************************************
* Funcionalidad: validacion de fabricante y poveedores.
************************************************************************************/
DECLARE

  ID_ALERT ALERT;
  V_BOTON VARCHAR2(2);

BEGIN
		
		IF :IA_RECEP_DISPO_INDIV.TXT_ICAR IS NULL THEN
		    :IA_RECEP_DISPO_INDIV.TXT_ID_ICAR := NULL;
		END IF;
		
		IF :IA_RECEP_DISPO_INDIV.TXT_PROVEEDOR IS NOT NULL 
			    AND 
			 :IA_RECEP_DISPO_INDIV.TXT_ICAR IS NOT NULL THEN
			
			  SET_ALERT_PROPERTY('F__PLA_MENSAJE_1',ALERT_MESSAGE_TEXT, 
		                       'Si existe proveedor no puede existir fabricante.');		  	
		    ID_ALERT := FIND_ALERT('F__PLA_MENSAJE_1');
		  	V_BOTON := SHOW_ALERT(ID_ALERT);	
				
			
			 :IA_RECEP_DISPO_INDIV.TXT_ICAR := NULL;
			 :IA_RECEP_DISPO_INDIV.TXT_ID_ICAR := NULL; 
			 
		END IF;	 

END;
```

### Item `TXT_PROVEEDOR` (Proveedor)

#### WHEN-VALIDATE-ITEM (líneas 5980–6031)
Simétrico al anterior. Si el proveedor queda NULL, limpia su identificador. Si hay
fabricante **y** proveedor, muestra alerta ("Si existe fabricante no puede existir
proveedor") y **anula el proveedor** (exclusión mutua: gana el fabricante).

```sql
/************************************************************************************
* Funcionalidad: validacion de fabricante y poveedores.
************************************************************************************/
DECLARE

  ID_ALERT ALERT;
  V_BOTON VARCHAR2(2);

BEGIN

    IF :IA_RECEP_DISPO_INDIV.TXT_PROVEEDOR IS NULL THEN
    	    :IA_RECEP_DISPO_INDIV.TXT_ID_PROVEEDOR := NULL; 
    END IF;	

		
		IF :IA_RECEP_DISPO_INDIV.TXT_ICAR IS NOT NULL 
			   AND
			 :IA_RECEP_DISPO_INDIV.TXT_PROVEEDOR IS NOT NULL THEN
			
			  SET_ALERT_PROPERTY('F__PLA_MENSAJE_1',ALERT_MESSAGE_TEXT, 
		                       'Si existe fabricante no puede existir proveedor.');		  	
		    ID_ALERT := FIND_ALERT('F__PLA_MENSAJE_1');
		  	V_BOTON := SHOW_ALERT(ID_ALERT);	
				
			
			 :IA_RECEP_DISPO_INDIV.TXT_PROVEEDOR := NULL;
			 :IA_RECEP_DISPO_INDIV.TXT_ID_PROVEEDOR := NULL; 
			 
		END IF;	 

END;
```

> **Nota:** las dos validaciones anteriores implementan la misma regla de exclusión
> mutua (un dispositivo procede de un fabricante O de un proveedor, nunca de ambos),
> pero cada una anula el item recién editado, de modo que "gana" el otro campo ya
> presente.

### Item `DISP_ELECTRONICO` (Identificador electrónico)

#### WHEN-VALIDATE-ITEM (líneas 6407–6434)
Si se ha introducido un identificador electrónico, invoca la validación de rangos
del paquete de recepción.

```sql
/************************************************************************************
* Funcionalidad: Validar los identificadores electrónicos a insertar.
************************************************************************************/
IF :IA_RECEP_DISPO_INDIV.DISP_ELECTRONICO IS NOT NULL THEN
	IA_RECEPCION_ID_PKG.P_VALIDAR_IDENT_RECEP(1);
END IF;
```

### Item `TXT_FECHA_RECEPCION` (Fecha de recepción)

#### WHEN-VALIDATE-ITEM (líneas 6608–6649)
Valida que la fecha de recepción no sea posterior a la fecha del sistema
(`TRUNC(SYSDATE)`). Si lo es, muestra la alerta `ALERT_ERROR` y aborta con
`RAISE FORM_TRIGGER_FAILURE`.

> **Ojo:** el código referencia `:IA_RECEP_DISPO.TXT_FECHA_RECEPCION` (bloque
> `IA_RECEP_DISPO`, sin sufijo `_INDIV`). Verificar si es una referencia
> intencionada a otro bloque hermano o un error de nombre a corregir en la
> migración.

```sql
/************************************************************************************
* Funcionalidad: Validación de la fecha de recepción.
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

1. **Exclusión mutua fabricante / proveedor.** Un dispositivo no puede tener a la
   vez fabricante (`TXT_ICAR`) y proveedor (`TXT_PROVEEDOR`). Al detectarse ambos,
   se avisa y se anula el campo recién introducido junto con su identificador
   asociado (`TXT_ID_ICAR` / `TXT_ID_PROVEEDOR`).
2. **Coherencia de identificadores de soporte.** Si `TXT_ICAR` es NULL,
   `TXT_ID_ICAR` debe ser NULL. Si `TXT_PROVEEDOR` es NULL, `TXT_ID_PROVEEDOR`
   debe ser NULL.
3. **Fecha de recepción no futura.** `TXT_FECHA_RECEPCION` no puede ser mayor que
   la fecha del sistema (`TRUNC(SYSDATE)`); si lo es, se rechaza la validación.
4. **Validación del identificador electrónico.** Todo `DISP_ELECTRONICO` no nulo
   se valida (rangos) mediante `IA_RECEPCION_ID_PKG.P_VALIDAR_IDENT_RECEP(1)`.
5. **Tipo de dispositivo dependiente de la especie.** La lista de tipos de
   dispositivo (`LST_TIPO_DISPOSITIVOS`) se recarga según la especie seleccionada:
   equino (`'01'`) usa el grupo `RG_TIP_DISP_EQ`; el resto (ovino/caprino, `'04'`)
   usa `RG_TIP_DISP`.
6. **Campos validados desde lista (LOV):** `TXT_ICAR` (`LV_ICAR_INDIV`),
   `TXT_PROVEEDOR` (`LV_PROVEEDORES_INDIV`) — con "Validar desde Lista = Sí".
7. **Campos obligatorios:** `DSP_COD_PAIS` (aunque oculto y de soporte).

## Llamadas a paquetes / procedimientos de BD

| Paquete.Procedimiento | Parámetros | Disparador origen | Propósito |
|-----------------------|-----------|-------------------|-----------|
| `IA_RECEPCION_ID_PKG.P_CARGAR_VALORES_RECEPCION` | `(1)` | WHEN-NEW-BLOCK-INSTANCE del bloque | Carga inicial de valores de combos y listas de valores. |
| `IA_RECEPCION_ID_PKG.P_VALIDAR_IDENT_RECEP` | `(1)` | WHEN-VALIDATE-ITEM de `DISP_ELECTRONICO` | Valida los rangos de los identificadores electrónicos a insertar. |

Rutinas locales del formulario invocadas (no de paquete de BD, presumiblemente
definidas en unidades de programa del propio Form):

- `WHEN_NEW_ITEM_INSTANCE;` — procedimiento del Form, validación de rangos.
- `P_ESTABLECER_BOTONERA;` — actualiza el estado (habilitado/deshabilitado) de la
  botonera.

Grupos de registros (record groups) usados: `RG_TIP_DISP_EQ`, `RG_TIP_DISP`.
Alertas usadas: `F__PLA_MENSAJE_1`, `ALERT_ERROR`.
Listas de valores (LOV): `LV_ICAR_INDIV`, `LV_PROVEEDORES_INDIV`.
El parámetro `1` que reciben los procedimientos parece indicar el modo
"individual" (frente a recepción masiva/por rango en otros bloques del mismo Form).

## Notas para la migración a Java

- **Capa Model (entidad JPA).** El bloque no es de BD directo; la entidad de
  dominio (recepción de dispositivo individual) se persiste vía el paquete
  `IA_RECEPCION_ID_PKG`. Modelar una entidad `RecepcionDispositivoIndividual`
  (o agregado *Recepción*) con: especie, tipo de dispositivo, norma, fabricante
  (id + descripción), proveedor (id + descripción), identificador electrónico,
  fecha de recepción, país. El campo `DISP_ELECTRONICO` es Char(23) de longitud
  fija.
- **Capa Repository.** Traducir `P_CARGAR_VALORES_RECEPCION` y
  `P_VALIDAR_IDENT_RECEP` a métodos de repositorio (JPQL / llamadas). Si la lógica
  de estos paquetes es compleja (rangos), puede requerir consulta de las unidades
  de programa asociadas o mantener la llamada al procedimiento almacenado.
- **Capa Service (`@Service @Transactional`).** Ubicar aquí las reglas de negocio:
  - Exclusión mutua fabricante/proveedor (regla 1) — validar antes de persistir,
    lanzando excepción de validación en lugar de anular silenciosamente el campo
    (comportamiento original a confirmar con negocio).
  - Coherencia de identificadores de soporte (regla 2).
  - Fecha de recepción ≤ hoy (regla 3) — usar `LocalDate.now()` en vez de
    `SYSDATE`.
  - Validación de rangos de identificador electrónico (regla 4 → método de
    servicio equivalente a `P_VALIDAR_IDENT_RECEP`).
  - Carga condicional de tipos de dispositivo por especie (regla 5) — el mapeo
    `'01' → EQ` / `'04' → ovino/caprino` debe modelarse (enum de especie o tabla
    de tipos parametrizada).
- **Capa Bean/Controller (JSF).** Los combos (`LST_ESPECIES`,
  `LST_TIPO_DISPOSITIVOS`, `LST_NORMAS`) se cargan como listas de selección; el
  refresco de tipos al cambiar la especie (WHEN-LIST-CHANGED) se implementa con un
  `valueChangeListener`/AJAX en PrimeFaces que repuebla la lista dependiente.
  Las LOV (`LV_ICAR_INDIV`, `LV_PROVEEDORES_INDIV`) se traducen a autocompletar o
  diálogos de selección.
- **Alertas.** `SHOW_ALERT` / `SET_ALERT_PROPERTY` se sustituyen por
  `FacesMessage` / `p:messages` o diálogos de confirmación.
- **Aviso de nombre de bloque.** El disparador de fecha referencia
  `:IA_RECEP_DISPO.TXT_FECHA_RECEPCION` (sin `_INDIV`). Confirmar el bloque real
  antes de migrar para no arrastrar un bug latente.
- El bloque no permite borrado; la entidad solo soporta alta y modificación.

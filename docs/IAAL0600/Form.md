# IAAL0600 — Recepción de dispositivos electrónicos

Wireframes (mockups ASCII) de las pantallas del formulario Oracle `IAAL0600`,
reconstruidos a partir de las coordenadas (Posición X/Y, Ancho/Alto), tipos de
elemento y prompts del export `oracle/IAAL0600.txt`. Son aproximados: reflejan la
disposición relativa de campos, etiquetas y marcos, no el pixel exacto.

Convenciones del dibujo:

- `[____]` campo de texto / visualización · `[ v ]` lista desplegable ·
  `[ ] etiqueta` casilla · `( ) opción` radio · `[ Botón ]` botón.
- Cada recuadro exterior es una **ventana**; los recuadros interiores con título
  son **marcos** (frames) del lienzo.

## Índice de pantallas

| Ventana | Lienzo | Contenido |
|---------|--------|-----------|
| WINDOWPLA | `BOTONERA` | Barra de herramientas común (sesión + navegación) |
| W_RECEPCION | `CV_RECEPCION` | Recepción de dispositivos |
| W_RECEPCION_INDIV | `CV_RECEPCION_INDIV` | Recepción individual |
| W_DIST_DISPO | `CV_DIST_DISPO` | Distribución de dispositivos |
| W_DES_RECEP | `CV_DES_RECEP` | Deshacer recepción |
| W_DES_DIST | `CV_DES_DIST` | Deshacer distribución |
| W_ANULAR_DIST | `CV_ANULAR_DIST` | Anular distribución |
| W_ANULAR_RECEP | `CV_ANULAR_RECEP` | Anular recepción |
| W_DES_ANUL_RECI | `CV_DES_ANUL_REC` | Deshacer anulación de recepción |
| W_DES_ANUL_DIST | `CV_DES_ANUL_DIST` | Deshacer anulación de distribución |
| W_CONSULTA_ESTADOS | `C_CONSULTA_ESTADOS` + `C_INF_CROTAL` | Consulta de estados del crotal |

---

## Barra de herramientas — BOTONERA (WINDOWPLA)

Barra superior común del formulario: logotipo e info de sesión a la izquierda y la
botonera estándar de navegación/consulta de Oracle Forms a la derecha (iconos en
dos filas).

```
+-------------------------------------------------------------------------------------------------------+
| WINDOWPLA                                                                          [ lienzo BOTONERA ] |
+-------------------------------------------------------------------------------------------------------+
| .-------.  Proceso:[..............]   Usuario:[.....] Fecha:[......]  [Ins][Del][Grb][IQry][EQry][Can][Prt][Clr] |
| | LOGO  |  Subproceso:[...........]   Modo Acceso.:[M]  Campaña.:[....][cmp]   [1º][<-][->][Ult][LoV][Run][Salir] |
| '-------'  Subsubproc.:[.........]   Variable1:[......................]                                          |
+-------------------------------------------------------------------------------------------------------+
```

| Botón | Tooltip | Fila |
|-------|---------|------|
| INSERTAR | Insertar Registro | 1 |
| BORRAR | Eliminar Registro | 1 |
| GRABAR | Grabar | 1 |
| INTRODUCIR_CONSULTA | Introducir Consulta | 1 |
| EJECUTAR_CONSULTA | Ejecutar la Consulta | 1 |
| CANCELAR_CONSULTA | Cancelar la Entrada de Consulta | 1 |
| IMPRIMIR | Imprime Pantalla | 1 |
| CLEAR_RECORD | Limpiar Registro | 1 |
| PRIMERO / ANTERIOR / SIGUIENTE / ULTIMO | Navegación de registros | 2 |
| LISTA | Lista de Valores | 2 |
| LANZA | Ejecuta Proceso | 2 |
| SALIR | Salir | 2 |

Campos de sesión (solo lectura, `Visualizar Elemento`): PROCESO, SUBPROCESO,
SUBSUBPROCESO, USUARIO, FECHA, MODO, CAMPANA/TCAMPANA, VARIABLE1. LOGOTIPO es
`Imagen`.

---

## Recepción de dispositivos — W_RECEPCION (CV_RECEPCION)

Cabecera "Dispositivos" (último recibido por especie) y marco "Recepción" con los
datos del lote a recibir. Los botones de operación viven en la BOTONERA.

```
+------------------------------------------------------------------------------+
| Recepcion de I. Electronicos                                          [_][x] |
+------------------------------------------------------------------------------+
|   +-- Dispositivos ---------------------------------------------------+      |
|   | Especie:                     [ Bovino  v ]                        |      |
|   | Ultimo dispositivo recibido: [_________]                          |      |
|   +------------------------------------------------------------------+       |
|                                                                              |
|   +-- Recepcion ------------------------------------------------------+      |
|   | Fabricante:              [________________]                       |      |
|   | Prooveedor:              [________________]                       |      |
|   | Tipo de dispositivo:     [               v ]                      |      |
|   | Norma de fabricacion:    [               v ]                      |      |
|   | Pais:                    [___] [__________]                       |      |
|   | Ultimo dispositivo a recibir: [__] [_____]                        |      |
|   | Total de dispositivos:   [_______]                                |      |
|   | Fecha de recepcion:      [__/__/____]                             |      |
|   +------------------------------------------------------------------+       |
+------------------------------------------------------------------------------+
```

| Campo | Tipo | BD |
|-------|------|----|
| Especie (LST_ESPECIES) | Lista | No |
| Ultimo dispositivo recibido (DSP_ULTIMO_DISP) | Visualizar | No |
| Fabricante (TXT_ICAR) | Texto (LOV) | No |
| Prooveedor (TXT_PROVEEDOR) | Texto (LOV) | No |
| Tipo de dispositivo (LST_TIPO_DISPOSITIVOS) | Lista | No |
| Norma de fabricacion (LST_NORMAS) | Lista | No |
| Pais (DSP_COD_PAIS / TXT_NOMBRE_PAIS) | Visualizar | No |
| Ultimo dispositivo a recibir (TXT_DIS_HASTA) | Texto | No |
| Total de dispositivos (DSP_N_DISP) | Visualizar | No |
| Fecha de recepcion (TXT_FECHA_RECEPCION) | Texto (Date) | No |

## Recepción individual — W_RECEPCION_INDIV (CV_RECEPCION_INDIV)

Un único marco "Recepción"; recibe un dispositivo concreto en vez de un rango.

```
+------------------------------------------------------------------------------+
| Recepcion de I. Electronico Individual                                [_][x] |
+------------------------------------------------------------------------------+
|   +-- Recepcion ------------------------------------------------------+      |
|   | Especie:                     [ Bovino  v ]                        |      |
|   | Fabricante:              [________________]                       |      |
|   | Prooveedor:              [________________]                       |      |
|   | Tipo de dispositivo:     [               v ]                      |      |
|   | Norma de fabricacion:    [               v ]                      |      |
|   | Ultimo dispositivo recibido: [_________]                          |      |
|   | Dispositivo a Recibir:   [________________]                       |      |
|   | Fecha de recepcion:      [__/__/____]                             |      |
|   +------------------------------------------------------------------+       |
+------------------------------------------------------------------------------+
```

| Campo | Tipo | BD |
|-------|------|----|
| Especie (LST_ESPECIES) | Lista | No |
| Fabricante (TXT_ICAR) | Texto | No |
| Prooveedor (TXT_PROVEEDOR) | Texto | No |
| Tipo de dispositivo (LST_TIPO_DISPOSITIVOS) | Lista | No |
| Norma de fabricacion (LST_NORMAS) | Lista | No |
| Ultimo dispositivo recibido (DSP_ULTIMO_DISP) | Visualizar | No |
| Dispositivo a Recibir (DISP_ELECTRONICO) | Texto | No |
| Fecha de recepcion (TXT_FECHA_RECEPCION) | Texto (Date) | No |

---

## Distribución de dispositivos — W_DIST_DISPO (CV_DIST_DISPO)

Rango de identificadores, ADS, veterinario y fecha con los que se distribuyen los
dispositivos (marco "Distribuir").

```
+------------------------------------------------------------------------------+
| Distribucion de dispositivos                                          [_][x] |
+------------------------------------------------------------------------------+
|   +-- Distribuir -----------------------------------------------------+      |
|   | Especie                 [ v ]                                     |      |
|   | Identificador inicial - [__] [_____________]                      |      |
|   | Identificador final   - [__] [_____________]                      |      |
|   | ADS                     [________________]                        |      |
|   | Veterinarios            [________________]                        |      |
|   | Total disp. a distribuir[________________]  (solo lectura)        |      |
|   | Fecha de distribucion   [__/__/____]                              |      |
|   +------------------------------------------------------------------+       |
+------------------------------------------------------------------------------+
```

| Campo | Tipo | BD |
|-------|------|----|
| Especie (LST_ESPECIES) | Lista | No |
| Identificador inicial (DSP_COM_DESDE / TXT_DIS_DESDE) | Visualizar + Texto(LOV) | No |
| Identificador final (DSP_COM_HASTA / TXT_DIS_HASTA) | Visualizar + Texto(LOV) | No |
| ADS (TXT_DIST_ADS) | Texto (LOV) | No |
| Veterinarios (TXT_VETERINARIO) | Texto (LOV) | No |
| Total de dispositivos (DSP_N_DISP) | Visualizar | No |
| Fecha de distribución (TXT_FECHA_DISTRIBUCION) | Texto (Date) | No |

## Deshacer recepción — W_DES_RECEP (CV_DES_RECEP)

Especie y rango de identificadores cuya recepción se va a deshacer (marco
"Deshacer").

```
+------------------------------------------------------------------------------+
| Deshacer recepcion                                                    [_][x] |
+------------------------------------------------------------------------------+
|   +-- Deshacer -------------------------------------------------------+      |
|   | Especie                 [ v ]                                     |      |
|   | Identificador inicial - [__] [_____________]                      |      |
|   | Identificador final   - [__] [_____________]                      |      |
|   | Total disp. a deshacer  [________________]  (solo lectura)        |      |
|   +------------------------------------------------------------------+       |
+------------------------------------------------------------------------------+
```

## Deshacer distribución — W_DES_DIST (CV_DES_DIST)

Idéntica a "Deshacer recepción" pero sobre distribuciones (marco "Deshacer").

```
+------------------------------------------------------------------------------+
| Deshacer distribucion                                                 [_][x] |
+------------------------------------------------------------------------------+
|   +-- Deshacer -------------------------------------------------------+      |
|   | Especie                 [ v ]                                     |      |
|   | Identificador inicial - [__] [_____________]                      |      |
|   | Identificador final   - [__] [_____________]                      |      |
|   | Total disp. a deshacer  [________________]  (solo lectura)        |      |
|   +------------------------------------------------------------------+       |
+------------------------------------------------------------------------------+
```

Campos comunes de ambas pantallas: Especie (LST_ESPECIES, Lista), rango
DSP_COM_DESDE/HASTA + TXT_DIS_DESDE/HASTA (Visualizar + Texto LOV), DSP_N_DISP
(Total, Visualizar). Todos no-BD.

---

## Anular distribución — W_ANULAR_DIST (CV_ANULAR_DIST)

Anula una distribución por especie y rango de identificadores (marco "Anulación").

```
+------------------------------------------------------------------------------+
| Anular distribucion                                                   [_][x] |
+------------------------------------------------------------------------------+
|   +-- Anulacion ------------------------------------------------------+      |
|   | Especie                 [ v ]                                     |      |
|   | Identificador inicial - [__] [_____________]                      |      |
|   | Identificador final   - [__] [_____________]                      |      |
|   | Total de dispositivos a anular [________________]                 |      |
|   | Fecha de anulacion      [__/__/____]                              |      |
|   +------------------------------------------------------------------+       |
+------------------------------------------------------------------------------+
```

## Anular recepción — W_ANULAR_RECEP (CV_ANULAR_RECEP)

Estructuralmente idéntica a "Anular distribución" pero sobre recepciones.

```
+------------------------------------------------------------------------------+
| Anular recepcion                                                      [_][x] |
+------------------------------------------------------------------------------+
|   +-- Anulacion ------------------------------------------------------+      |
|   | Especie                 [ v ]                                     |      |
|   | Identificador inicial - [__] [_____________]                      |      |
|   | Identificador final   - [__] [_____________]                      |      |
|   | Total de dispositivos a anular [________________]                 |      |
|   | Fecha de anulacion      [__/__/____]                              |      |
|   +------------------------------------------------------------------+       |
+------------------------------------------------------------------------------+
```

Campos comunes: Especie (LST_ESPECIES, Lista), rango DSP_COM_DESDE/HASTA +
TXT_DIS_DESDE/HASTA, DSP_N_DISP (Total), TXT_FECHA_ANULACION (Fecha). Todos no-BD.

---

## Deshacer anulación de recepción — W_DES_ANUL_RECI (CV_DES_ANUL_REC)

Deshace la anulación de recepciones por especie y rango (marco "Deshacer A.
Recibidos").

```
+------------------------------------------------------------------------------+
| Deshacer Anular Recibidos                                             [_][x] |
+------------------------------------------------------------------------------+
|   +-- Deshacer A. Recibidos ------------------------------------------+      |
|   | Especie                 [ v ]                                     |      |
|   | Identificador inicial - [__] [_____________]                      |      |
|   | Identificador final   - [__] [_____________]                      |      |
|   | Total de dispositivos   [________________]                        |      |
|   +------------------------------------------------------------------+       |
+------------------------------------------------------------------------------+
```

## Deshacer anulación de distribución — W_DES_ANUL_DIST (CV_DES_ANUL_DIST)

Misma disposición, sobre distribuciones (marco "Deshacer A. Distribuidos").

```
+------------------------------------------------------------------------------+
| Deshacer Anular Distribuidos                                          [_][x] |
+------------------------------------------------------------------------------+
|   +-- Deshacer A. Distribuidos ---------------------------------------+      |
|   | Especie                 [ v ]                                     |      |
|   | Identificador inicial - [__] [_____________]                      |      |
|   | Identificador final   - [__] [_____________]                      |      |
|   | Total de dispositivos   [________________]                        |      |
|   +------------------------------------------------------------------+       |
+------------------------------------------------------------------------------+
```

Campos comunes: Especie (LST_ESPECIES, Lista), rango DSP_COM_DESDE/HASTA +
TXT_DIS_DESDE/HASTA, DSP_N_DISP (Total). Todos no-BD.

---

## Consulta de estados del crotal — W_CONSULTA_ESTADOS

Ventana de consulta compuesta por dos lienzos: `C_CONSULTA_ESTADOS` (cabecera,
banda "Estados" y lista "Crotales") y un lienzo con pestañas `C_INF_CROTAL` con el
detalle del crotal seleccionado.

```
+==============================================================================+
| Consulta de estados de crotales                                       [_][x] |
+==============================================================================+
|  Crotal:[______________]  Id. Electronico:[____________]  UELN:[__________]  |
|  Especie:[__________]                                                         |
|  +-- Estados ---------------------------------------------------------------+|
|  |  Codigo   Descripcion del estado                                         ||
|  |  [____]   [____________________________________________________]        ||
|  +-------------------------------------------------------------------------+|
|                                                                              |
|  +-- Crotales ------+  +===[ C_INF_CROTAL ]==================================+|
|  | [______________] |  | /Identificacion\ Animal | Localizac. | Reidentif. | |
|  | [______________] |  |----------------------------------------------------| |
|  | [______________] |  |  ...campos de la pestaña activa (abajo)...          | |
|  | [______________] |  |                                                    | |
|  | [______________] |  |                                                    | |
|  +------------------+  +====================================================+|
+==============================================================================+
```

### Pestaña «Identificación» (ciclo de vida del crotal)

```
+-- Identificacion ------------------------------------------------+
|  [x] Recibido      Fecha:[__________]                            |
|  [x] Distribuido   Fecha:[__________]   Oficina:[____________]   |
|                                          ADS:[_____________]     |
|  [x] Repartido     Fecha:[__________]                            |
|      Explotacion:[______________]  Veterinario:[____________]    |
|  [x] Asignado      Fecha:[__________]                            |
|  [x] Sustituido    Fecha:[__________]                            |
|  [x] Anulado       Fecha:[__________]                            |
+-----------------------------------------------------------------+
```

Casillas + fechas: CB_RECIBIDO/F_RECIBIDO, CB_DISTRIBUIDO/F_DISTRIBUIDO,
CB_REPARTIDO/F_REPARTIDO, CB_ASIGNADO/F_ASIGNADO, CB_SUSTITUIDO/F_SUSTITUIDO,
CB_ANULADO/F_ANULADO; más OFICINA, ADS, EXPLOTACION, VETERINARIO.

### Pestaña «Animal» (datos del animal / res)

```
+-- Animal --------------------------------------------------------+
|  Raza:[______________]     Explotacion:[______________]         |
|  +-- Sexo --------+                                              |
|  | ( ) M   ( ) H  |                                              |
|  +----------------+                                              |
|  Fecha:[________]   Fecha Baja:[________]                        |
|  Estado:[__________]   Restriccion:[__________]                  |
|  Crotal Madre:[__________]   Id. Lidia:[__________]              |
+-----------------------------------------------------------------+
```

Campos: RAZ_DESC (Raza), EXP_NUMREG (Explotación), RES_SEXO (marco "Sexo"),
RES_F_NACI (Fecha), RES_F_BAJA (Fecha Baja), STR_DESC (Estado), RST_DESC
(Restricción), MAD_CROTAL (Crotal Madre), IDT_ID (Id. Lidia). Origen: bloque
`DATOS_RES`.

### Pestaña «Localizaciones» (situación de la explotación)

Rejilla multi-registro (marco "Localizaciones del animal").

```
+-- Localizaciones del animal -------------------------------------+
|  Explotacion       F. Inicio    Relacion       F. Fin           |
|  [_____________]   [________]   [__________]   [________]        |
|  [_____________]   [________]   [__________]   [________]        |
|  [_____________]   [________]   [__________]   [________]        |
+-----------------------------------------------------------------+
```

Columnas: EXP_NUMREG (Explotación), SIT_F_INI (F. Inicio), TPS_DESC (Relación),
SIT_F_FIN (F. Fin). Origen: bloque `DATOS_SITUAC` (BD: `IB_SITRES`, `RE_EXPLOT`,
`IB_TPSITU`).

### Pestaña «Reidentificaciones» (sustituciones y duplicados)

```
+-- Reidentificaciones --------------------------------------------+
|  Sustituido Por . . . :[__________]   Motivo:[____________]      |
|  Sustituto De ...     :[__________]   Motivo:[____________]      |
|  Tipo Dispositivo:[__________]   F. Solicitud:[__________]       |
|  Empresa:[______________]   Explotacion:[________]  Numero:[___] |
|  Nº Registro:[__________]   Nombre Explotacion:[______________]  |
+-----------------------------------------------------------------+
```

Campos: SUSTITUIDO_POR / MOTIVO_POR, SUSTITUTO_DE / MOTIVO_DE (bloque
`SUSTITUCION`); TPI_DESC (Tipo Dispositivo), DUP_F_SOLICI (F. Solicitud), EMP_DESC
(Empresa), DUP_EXPLOT (Explotación), DUP_NDUPLIC (Número) del bloque
`IA_DUPLIC_EST` (BD: `IA_DUPLIC`); EXP_NUMREG (Nº Registro), EXP_NOMBRE (Nombre
Explotación) del bloque `RE_EXPLOT`.

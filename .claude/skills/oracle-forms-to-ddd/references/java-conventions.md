# Convenciones del código de dominio Java generado

El objetivo de la Fase 1 es un **modelo de dominio puro y validable**: solo
agregados, entidades y value objects. Sin capa de persistencia, sin framework,
sin `main`, sin lógica de UI.

## Formato de salida

- **Un único archivo** `.java` por formulario, nombrado como el dominio que
  representa (p. ej. `ModeloDominio<NOMBREFORM>.java`).
- Java no permite varias clases `public` en un fichero. Para que todo el modelo
  conviva en un archivo y siga siendo **compilable**, declara las clases con
  visibilidad de paquete (sin `public`). No añadas una clase contenedora ni un
  `main`: el dominio se valida compilando, no ejecutando.
- Si el usuario prefiere **un archivo por clase** (estructura de proyecto real),
  genera un fichero por tipo con su `package` y visibilidad `public`. Pregunta o
  sigue la convención del proyecto destino.

## Estructura interna del archivo

Ordena y separa con comentarios de sección:

1. Imports (`java.time.*`, `java.util.*`, `java.util.Objects`).
2. **Aggregate Roots**.
3. **Entities** (no raíz).
4. **Value Objects** (incluidos enums y los `...Ref`).
5. **Identificadores** tipados.

## Reglas por tipo

**Aggregate Root / Entity**
- `final class`, campos `private`.
- Identidad mediante un VO de id, asignada en el constructor y `final`.
- Constructor que valida invariantes (`Objects.requireNonNull`, comprobaciones).
- Métodos de **comportamiento de dominio** con nombres del negocio (`recibir`,
  `distribuir`, `anular`) en vez de setters anémicos, cuando los packages PL/SQL
  revelen ese comportamiento. Si no hay comportamiento claro, deja getters y los
  mutadores mínimos necesarios.
- Las colecciones de entidades hijas se exponen como copia inmutable
  (`List.copyOf(...)`) y se modifican por métodos (`anadirXxx`).

**Value Object**
- `final class`, todos los campos `final`.
- `equals` y `hashCode` por **valor** (todos los campos).
- Sin identidad ni setters. Validación en el constructor si aplica.
- Para dominios cerrados, usa `enum`.

**Identificadores**
- Un `final class` minimalista por id con un único campo `final` (`v`).

## Trazabilidad

Comentario Javadoc o de línea en cada clase indicando origen:
`// Origen: bloque <BLOQUE> / tabla <TABLA>` y, en cada campo relevante, la
columna de origen (`// CRO_PAIS`).

## Restricciones

- **No** generes `main`, prints, ni código de prueba salvo que el usuario lo pida.
- **No** uses caracteres no ASCII en identificadores Java (métodos/campos). Los
  comentarios sí pueden llevar acentos. (Evita `añadir` como nombre de método →
  usa `anadir`.)
- **No** incluyas anotaciones de framework (JPA, Lombok) en la Fase 1 salvo
  petición explícita: el dominio debe ser independiente de infraestructura.

## Validación de compilación

El entorno puede no traer `javac` como ejecutable pero sí el módulo
`jdk.compiler`. Compila así (ajusta la ruta al JDK disponible):

```bash
JDK=$(ls -d /usr/lib/jvm/java-*-openjdk-* 2>/dev/null | head -1)
"$JDK/bin/java" -m jdk.compiler/com.sun.tools.javac.Main -Xlint:all <archivo>.java
rm -f *.class    # limpiar artefactos de compilación
```

Si no hay ningún JDK con `jdk.compiler`, instala uno empaquetado en un wheel de
PyPI (host permitido) y reutiliza su módulo compiler:

```bash
pip install jdk4py --break-system-packages -q
# jdk4py trae runtime; combínalo con un openjdk del sistema que tenga jdk.compiler,
# o usa cualquier JDK completo disponible.
```

La compilación sin errores ni warnings es la señal de que el modelo es válido.

# CLAUDE.md

Instrucciones para trabajar en este proyecto.

## Propósito

El objetivo del proyecto es **migrar (transponer) aplicaciones Oracle Forms a la
pila tecnológica Java de este proyecto**: JSF (Mojarra) + PrimeFaces + Spring +
Hibernate sobre Java 11.

Cada parte de un Oracle Form (`.fmb` exportado a texto) se traslada a su capa
correspondiente: disparadores/UI → `bean` (Controller), lógica de negocio →
`service`, acceso a datos → `repository`, y bloques de datos → entidades JPA en
`model`. La migración se apoya en un **conjunto de skills** (uno por fase/capa);
ver la sección «Migración Oracle Forms → Java».

## Stack tecnológico

Proyecto web **WAR** sobre **Java 11** con namespace `javax.*`.
Las versiones están fijadas para ser compatibles con Java 11 (no migrar a
`jakarta.*` ni subir a líneas que requieran Java 17+).

| Componente   | Versión       | Nota                                                            |
|--------------|---------------|----------------------------------------------------------------|
| Java         | 11            | `<release>11</release>` en el compiler plugin                  |
| Spring       | 5.3.39        | Última línea 5.x compatible con Java 11 (Spring 6 exige Java 17)|
| Hibernate    | 5.6.15.Final  | `javax.persistence` (Hibernate 6 usa `jakarta`)                |
| JSF Mojarra  | 2.3.9         | Última con namespace `javax` en `org.glassfish:javax.faces`    |
| PrimeFaces   | 11.0.0        | Default `javax` (PrimeFaces 12+ usa `jakarta`)                 |
| Servlet API  | 4.0.1         | `javax.servlet` (scope `provided`)                             |
| H2           | 2.2.224       | Base de datos en memoria para ejecución de ejemplo             |

### Notas de compatibilidad importantes

- `org.glassfish:javax.faces` no publica versiones por encima de **2.3.9**;
  las posteriores se migraron al artefacto `jakarta.faces`. No subir más.
- `javax.annotation` (ej. `@PostConstruct`) se eliminó del JDK en Java 11, por
  eso se incluye explícitamente `javax.annotation:javax.annotation-api:1.3.2`.

## Estructura del proyecto

```
hello/
├── pom.xml
├── .gitignore
├── .claude/
│   ├── CLAUDE.md                        # este archivo
│   └── skills/oracle-forms-to-ddd/      # skill de migración Forms → dominio Java
└── src/main/
    ├── java/com/example/app/
    │   ├── config/AppConfig.java        # Spring: DataSource, JPA/Hibernate, transacciones
    │   ├── model/User.java              # Entidad JPA (@Entity) de ejemplo
    │   ├── repository/UserRepository.java  # @Repository con EntityManager
    │   ├── service/UserService.java     # @Service @Transactional
    │   └── bean/UserBean.java           # Bean JSF gestionado por Spring (#{userBean})
    └── webapp/
        ├── index.xhtml                  # Vista PrimeFaces de ejemplo
        └── WEB-INF/
            ├── web.xml                  # FacesServlet + ContextLoaderListener de Spring
            ├── faces-config.xml         # SpringBeanFacesELResolver (puente JSF↔Spring)
            └── beans.xml
```

## Arquitectura / convenciones

- Paquete base: `com.example.app`.
- Capas: `bean` (presentación JSF) → `service` (lógica + `@Transactional`) →
  `repository` (acceso a datos con `EntityManager`) → `model` (entidades JPA).
- Configuración de Spring **basada en anotaciones** (sin XML de Spring):
  `web.xml` arranca un `AnnotationConfigWebApplicationContext` apuntando al
  paquete `com.example.app.config`.
- Integración **JSF → Spring** mediante `SpringBeanFacesELResolver` declarado en
  `faces-config.xml`; los beans Spring se referencian en las vistas como
  `#{nombreBean}`.
- Los beans JSF se declaran con `@Component("...")` + `@Scope(...)` de Spring
  (no con anotaciones `javax.faces.bean.*`).

## Migración Oracle Forms → Java

Tarea recurrente del proyecto. Cuando el usuario pida migrar, transponer o
"pasar" un Oracle Form a Java —aunque solo diga "extrae las entidades" o "modela
el dominio"— aplica el skill correspondiente sin pedir confirmación de cuál usar.

Mapeo de cada parte del Form a su capa Java:

| Parte del Oracle Form                                    | Capa Java       | Paquete / convención |
|----------------------------------------------------------|-----------------|----------------------|
| Disparadores de UI, items de pantalla, navegación        | **Controller**  | `bean` — `@Component("xxxBean")` + `@Scope`, `Serializable` |
| Lógica de negocio, paquetes `IA_*_PKG`, validación       | **Service**     | `service` — `@Service @Transactional`, inyección por constructor |
| Acceso a datos (bloques BD, `query_source`/`dml_target`) | **Repository**  | `repository` — `@Repository` + `EntityManager` (JPQL) |
| Bloques de datos BD → entidades / agregados DDD          | **Model/Entity**| `model` — `@Entity @Table`, JPA `javax.persistence.*` |

Usa las clases `User*` existentes como plantilla de estilo de cada capa.

### Skills (en `.claude/skills/`)

- **`oracle-forms-to-ddd`** — Fase 1 (dominio): extrae el modelo DDD (agregados,
  entidades, value objects) del Form y genera la capa `model`, validándola por
  compilación. Es el punto de partida de las fases siguientes.
- **`oracle-forms-to-wireframe`** — Análisis de viabilidad (no genera código):
  reconstruye la UI del Form exportado como un wireframe HTML interactivo
  (`<NOMBRE>/wireframe.html`) para *ver* las pantallas antes de migrar.
- **`oracle-forms-to-business-logic`** — Análisis del comportamiento (no genera
  código): extrae la lógica de negocio de cada formulario de entrada de usuario
  (bloque) a un Markdown por formulario en `docs/logica-negocio/<BLOQUE>.md`
  (disparadores con su PL/SQL, validaciones y llamadas a paquetes `IA_*_PKG`).
  Es la especificación legible que alimenta a las fases Service/Repository/Controller.

> Las fases Repository, Service y Controller parten del modelo de dominio ya
> validado por `oracle-forms-to-ddd`. Registra aquí los nuevos skills a medida
> que se añadan.

## Comandos

```powershell
mvn clean package          # compila y genera target/hello.war
mvn tomcat7:run            # arranca en http://localhost:8080/hello
mvn clean                  # limpia target/
```

## Base de datos

- Por defecto **H2 en memoria** (`jdbc:h2:mem:hellodb`), configurada en
  `AppConfig.java` para que el proyecto arranque sin dependencias externas.
- Hibernate con `hbm2ddl.auto = update` (crea/actualiza el esquema al arrancar).
- Para usar una base de datos real, cambiar `DataSource` y `dialect` en
  `AppConfig.java`.

## Reglas al trabajar en este proyecto

- Mantener el namespace `javax.*`; no introducir dependencias `jakarta.*`.
- No subir versiones que rompan la compatibilidad con Java 11.
- Respetar la separación de capas descrita arriba.

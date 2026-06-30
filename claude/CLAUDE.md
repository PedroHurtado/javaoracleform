# CLAUDE.md

Instrucciones para trabajar en este proyecto.

> Nota: el propósito funcional/de negocio del proyecto aún no está definido.
> Este documento describe únicamente el stack técnico y la estructura creada
> hasta ahora. No asumas funcionalidad que no esté reflejada aquí.

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
├── claude/CLAUDE.md                     # este archivo
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

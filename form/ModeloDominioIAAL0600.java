/* =====================================================================================
 *  MODELO DE DOMINIO (DDD) — Derivado del Oracle Form IAAL0600
 *  "Recepción de dispositivos electrónicos" (identificación animal / crotales)
 *
 *  FASE 1: Entidades clasificadas en Aggregate Root, Entity y Value Object.
 *
 *  Trazabilidad al Form:
 *    - Bloques de datos de BD del .fmb   -> Entidades / Agregados
 *    - SELECTs embebidos y package PL/SQL -> relaciones y conceptos de dominio
 * ===================================================================================== */

import java.time.LocalDate;
import java.util.ArrayList;
import java.util.List;
import java.util.Objects;

/* =================================================================================
 * 1) AGGREGATE ROOTS (Raíces de Agregado)
 *    Bloques de BD con identidad propia y ciclo de vida; controlan invariantes.
 * ================================================================================= */

/**
 * AGGREGATE ROOT — DISPOSITIVO ELECTRÓNICO
 * Origen: tabla IA_DISPOSITIVOS (package IA_RECEPCION_ID_PKG / IA_ALMACEN_PKG).
 * Concepto central del formulario: el dispositivo que se recibe, distribuye,
 * reparte, asigna, sustituye o anula. Su estado evoluciona en el tiempo.
 */
final class Dispositivo {
    private final DispositivoId id;
    private final IdentificacionElectronica identificacion; // DIS_IDENTIFICACION
    private final EspecieRef especie;                       // SPC_CODIGO
    private final ProveedorRef proveedor;                   // PSS_CODIGO
    private Crotal crotal;
    private EstadoCrotal estado;                            // ciclo de vida
    private LocalDate fechaRecepcion;
    private LocalDate fechaDistribucion;

    Dispositivo(DispositivoId id, IdentificacionElectronica identificacion,
                EspecieRef especie, ProveedorRef proveedor, Crotal crotal, EstadoCrotal estado) {
        this.id = Objects.requireNonNull(id);
        this.identificacion = Objects.requireNonNull(identificacion);
        this.especie = especie;
        this.proveedor = proveedor;
        this.crotal = crotal;
        this.estado = estado == null ? EstadoCrotal.PENDIENTE : estado;
    }

    void recibir(LocalDate fecha) {
        transicionar(EstadoCrotal.RECIBIDO);
        this.fechaRecepcion = fecha;
    }
    void distribuir(LocalDate fecha) {
        if (estado != EstadoCrotal.RECIBIDO)
            throw new IllegalStateException("Solo se distribuye un dispositivo recibido");
        transicionar(EstadoCrotal.DISTRIBUIDO);
        this.fechaDistribucion = fecha;
    }
    void anular() { transicionar(EstadoCrotal.ANULADO); }

    private void transicionar(EstadoCrotal nuevo) { this.estado = nuevo; }

    DispositivoId getId() { return id; }
    EstadoCrotal getEstado() { return estado; }
}

/**
 * AGGREGATE ROOT — CROTAL ESTADO
 * Origen: bloque CROTALES_ESTADOS (tabla IB_CROTAL) + ESTADOS (IB_STCROT).
 * Crotal físico y su estado/situación, ligado a explotación y res.
 */
final class CrotalEstado {
    private final CrotalEstadoId id;                       // CRO_SEQUEN
    private final Crotal crotal;
    private final IdentificacionElectronica idElectronico; // ID_ELECTRONICO / UELN
    private EstadoCrotal estado;                           // STC_CODIGO -> IB_STCROT
    private ExplotacionRef explotacion;                   // EXP_SEQUEN
    private ResRef res;                                   // RES_SEQUEN
    private OficinaRef oficina;                           // OFI_SEQUEN
    private final List<DuplicadoEstado> duplicados = new ArrayList<>(); // IA_DUPLIC_EST

    CrotalEstado(CrotalEstadoId id, Crotal crotal, IdentificacionElectronica idElectronico) {
        this.id = Objects.requireNonNull(id);
        this.crotal = Objects.requireNonNull(crotal);
        this.idElectronico = idElectronico;
        this.estado = EstadoCrotal.PENDIENTE;
    }

    void asignarEstado(EstadoCrotal e) { this.estado = e; }
    void asignarExplotacion(ExplotacionRef e) { this.explotacion = e; }
    void asignarRes(ResRef r) { this.res = r; }
    void anadirDuplicado(DuplicadoEstado d) { duplicados.add(d); }

    CrotalEstadoId getId() { return id; }
    List<DuplicadoEstado> getDuplicados() { return List.copyOf(duplicados); }
}

/**
 * AGGREGATE ROOT — EXPLOTACIÓN
 * Origen: bloque RE_EXPLOT (tabla RE_EXPLOT).
 * Identidad de negocio propia (número de registro REGA); referenciada desde
 * múltiples agregados, por lo que es raíz propia.
 */
final class Explotacion {
    private final ExplotacionId id;   // EXP_NUMREG
    private String nombre;            // EXP_NOMBRE

    Explotacion(ExplotacionId id, String nombre) {
        this.id = Objects.requireNonNull(id);
        this.nombre = nombre;
    }
    ExplotacionId getId() { return id; }
    String getNombre() { return nombre; }
}

/**
 * AGGREGATE ROOT — RES (ANIMAL)
 * Origen: bloque DATOS_RES (SELECT sobre IB_RESES + razas, sexo, madre, identificación).
 * En este formulario se consulta, pero conceptualmente es raíz: identidad,
 * ciclo de vida (nacimiento/baja) e invariantes propios.
 */
final class Res {
    private final ResId id;             // RES_SEQUEN
    private RazaRef raza;               // RAZ_DESC
    private ExplotacionRef explotacion; // EXP_NUMREG
    private Sexo sexo;                  // RES_SEXO
    private LocalDate fechaNacimiento;  // RES_F_NACI
    private LocalDate fechaBaja;        // RES_F_BAJA
    private Crotal crotalMadre;         // MAD_CROTAL
    private final List<SituacionRes> situaciones = new ArrayList<>(); // DATOS_SITUAC

    Res(ResId id) { this.id = Objects.requireNonNull(id); }

    void anadirSituacion(SituacionRes s) { situaciones.add(s); }

    ResId getId() { return id; }
    List<SituacionRes> getSituaciones() { return List.copyOf(situaciones); }
}

/* =================================================================================
 * 2) ENTITIES (Entidades NO raíz — viven dentro de un agregado)
 * ================================================================================= */

/**
 * ENTITY (hija del agregado Res)
 * Origen: bloque DATOS_SITUAC (SELECT sobre IB_SITRES).
 * Situación/movimiento de una res en una explotación entre dos fechas.
 */
final class SituacionRes {
    private final SituacionResId id;
    private ExplotacionRef explotacion; // EXP_NUMREG
    private String tipoSituacion;       // TPS_DESC
    private LocalDate fechaInicio;      // SIT_F_INI
    private LocalDate fechaFin;         // SIT_F_FIN

    SituacionRes(SituacionResId id) { this.id = Objects.requireNonNull(id); }
    SituacionResId getId() { return id; }
}

/**
 * ENTITY (hija del agregado CrotalEstado)
 * Origen: bloque IA_DUPLIC_EST (tabla IA_DUPLIC).
 * Solicitud de duplicado asociada a un crotal.
 */
final class DuplicadoEstado {
    private final DuplicadoId id;       // DUP_NDUPLIC + CRO_SEQUEN
    private TipoIdentificacionRef tipo; // TPI_CODIGO / TPI_DESC
    private LocalDate fechaSolicitud;   // DUP_F_SOLICI
    private EmpresaRef empresa;         // DUP_EMPRESA / EMP_DESC
    private String explotacion;         // DUP_EXPLOT

    DuplicadoEstado(DuplicadoId id) { this.id = Objects.requireNonNull(id); }
    DuplicadoId getId() { return id; }
}

/* =================================================================================
 * 3) VALUE OBJECTS (inmutables, sin identidad, igualdad por valor)
 * ================================================================================= */

/** VO — Crotal: identificación visual compuesta. */
final class Crotal {
    private final String pais;      // CRO_PAIS
    private final String ccaa;      // CRO_CCAA
    private final String dg;        // CRO_DG / CRO_RECRO
    private final String serie;     // CRO_SERIE
    private final String num;       // CRO_NUM
    private final String codBarras; // CRO_CODBAR

    Crotal(String pais, String ccaa, String dg, String serie, String num, String codBarras) {
        this.pais = pais; this.ccaa = ccaa; this.dg = dg;
        this.serie = serie; this.num = num; this.codBarras = codBarras;
    }
    String valor() { return pais + ccaa + serie + num; }

    @Override public boolean equals(Object o) {
        if (this == o) return true;
        if (!(o instanceof Crotal)) return false;
        Crotal c = (Crotal) o;
        return Objects.equals(pais, c.pais) && Objects.equals(ccaa, c.ccaa)
            && Objects.equals(dg, c.dg) && Objects.equals(serie, c.serie)
            && Objects.equals(num, c.num) && Objects.equals(codBarras, c.codBarras);
    }
    @Override public int hashCode() { return Objects.hash(pais, ccaa, dg, serie, num, codBarras); }
}

/** VO — Identificación electrónica (DIS_IDENTIFICACION / ID_ELECTRONICO / UELN). */
final class IdentificacionElectronica {
    private final String codigo;
    IdentificacionElectronica(String codigo) {
        if (codigo == null || codigo.isBlank())
            throw new IllegalArgumentException("Identificación electrónica obligatoria");
        this.codigo = codigo;
    }
    String getCodigo() { return codigo; }
    @Override public boolean equals(Object o) {
        return o instanceof IdentificacionElectronica
            && codigo.equals(((IdentificacionElectronica) o).codigo);
    }
    @Override public int hashCode() { return codigo.hashCode(); }
}

/** VO enum — Estado del crotal/dispositivo (IB_STCROT / STC_CODIGO). */
enum EstadoCrotal {
    PENDIENTE, RECIBIDO, DISTRIBUIDO, REPARTIDO, ASIGNADO, SUSTITUIDO, ANULADO
}

/** VO enum — Sexo de la res (RES_SEXO). */
enum Sexo { MACHO, HEMBRA, DESCONOCIDO }

/* --- VOs de referencia (claves foráneas que este Form solo consulta, no edita) --- */

/** VO referencia — Especie (IA_ESPECIES / SPC_CODIGO). */
final class EspecieRef {
    final Long id; final String descripcion;
    EspecieRef(Long id, String descripcion) { this.id = id; this.descripcion = descripcion; }
    @Override public boolean equals(Object o){return o instanceof EspecieRef && Objects.equals(id,((EspecieRef)o).id);}
    @Override public int hashCode(){return Objects.hashCode(id);}
}
/** VO referencia — Proveedor (IA_PROVEEDOR / PSS_CODIGO). */
final class ProveedorRef {
    final String codigo; final String descripcion;
    ProveedorRef(String codigo, String descripcion){this.codigo=codigo;this.descripcion=descripcion;}
}
/** VO referencia — Explotación (citada desde otro agregado). */
final class ExplotacionRef {
    final String numReg; final String nombre;
    ExplotacionRef(String numReg, String nombre){this.numReg=numReg;this.nombre=nombre;}
}
/** VO referencia — Res. */
final class ResRef { final Long sequen; ResRef(Long s){this.sequen=s;} }
/** VO referencia — Oficina (OFI_SEQUEN). */
final class OficinaRef { final Long sequen; OficinaRef(Long s){this.sequen=s;} }
/** VO referencia — Raza (RE_RAZAS / RAZ_DESC). */
final class RazaRef { final String descripcion; RazaRef(String d){this.descripcion=d;} }
/** VO referencia — Tipo identificación (IA_TPIDELEC / TPI_CODIGO). */
final class TipoIdentificacionRef { final String codigo,desc; TipoIdentificacionRef(String c,String d){codigo=c;desc=d;} }
/** VO referencia — Empresa (TC_EMPRESA / DUP_EMPRESA). */
final class EmpresaRef { final String codigo,desc; EmpresaRef(String c,String d){codigo=c;desc=d;} }

/* =================================================================================
 * 4) IDENTIFICADORES (Value Objects de identidad — tipados)
 * ================================================================================= */
final class DispositivoId  { final Long v; DispositivoId(Long v){this.v=v;} }
final class CrotalEstadoId { final Long v; CrotalEstadoId(Long v){this.v=v;} }
final class ExplotacionId  { final String v; ExplotacionId(String v){this.v=v;} }
final class ResId          { final Long v; ResId(Long v){this.v=v;} }
final class SituacionResId { final Long v; SituacionResId(Long v){this.v=v;} }
final class DuplicadoId     { final Long v; DuplicadoId(Long v){this.v=v;} }

# taxonomy.py
# Taxonomía municipal de contratación
# Edita estas listas para añadir/quitar categorías

TIPOS_CONTRATO = [
    "Contrato de Servicios",
    "Contrato de Obras",
    "Suministro",
    "Concesión de Servicios",
    "Negociado sin Publicidad",
]

TIPOS_PROCEDIMIENTO = [
    "Procedimiento Abierto",
    "Procedimiento Abierto Simplificado",
    "Procedimiento Negociado",
    "Procedimiento Negociado sin Publicidad",
    "Contrato Menor",
]

TIPOS_ACTO = [
    "Providencia de Inicio",
    "Memoria Justificativa",
    "Aprobación de Pliegos",
    "Propuesta JGL/CJAL",
    "Resolución Alcaldía",
    "Informe Secretaría",
    "Adjudicación",
    "Requerimiento Documentación",
    "Prórroga o Modificado",
    "Otro",
]

# ─────────────────────────────────────────────────────────────────────────────
# REGLAS SIN IA — cuanto más completas, menos llamadas a la API
# Cada regla es (patron_en_nombre, tipo_contrato, tipo_procedimiento, tipo_acto)
# Usa None para "no lo sé" (se enviará a la IA)
# Los patrones son subcadenas en MAYÚSCULAS del nombre del fichero
# ─────────────────────────────────────────────────────────────────────────────

REGLAS = [
    # ── Tipo de contrato ──────────────────────────────────────────────────────
    ("CONCESION SERVICIOS",       "Concesión de Servicios",  None, None),
    ("CONCESIÓN SERVICIOS",       "Concesión de Servicios",  None, None),
    ("SUMINISTRO",                "Suministro",              None, None),
    ("OBRAS",                     "Contrato de Obras",       None, None),
    ("SERVICIOS",                 "Contrato de Servicios",   None, None),

    # ── Tipo de procedimiento ─────────────────────────────────────────────────
    ("NEGOCIADO SIN PUBLICIDAD",  None, "Procedimiento Negociado sin Publicidad", None),
    ("NEGOCIADO",                 None, "Procedimiento Negociado",                None),
    ("ABIERTO SIMPLIFICADO",      None, "Procedimiento Abierto Simplificado",     None),
    ("ABIERTO",                   None, "Procedimiento Abierto",                  None),
    ("CONTRATO MENOR",            None, "Contrato Menor",                         None),
    ("LOTES",                     None, "Procedimiento Abierto",                  None),

    # ── Tipo de acto ──────────────────────────────────────────────────────────
    ("PROVIDENCIA",               None, None, "Providencia de Inicio"),
    ("INICIAR",                   None, None, "Providencia de Inicio"),
    ("INICIO",                    None, None, "Providencia de Inicio"),
    ("INICIAR EXPEDIENTE",        None, None, "Providencia de Inicio"),
    ("MEMORIA JUSTIFICATIVA",     None, None, "Memoria Justificativa"),
    ("MEMORIA",                   None, None, "Memoria Justificativa"),
    ("PLIEGO",                    None, None, "Aprobación de Pliegos"),
    ("PLIEGOS",                   None, None, "Aprobación de Pliegos"),
    ("PROPUESTA JGL",             None, None, "Propuesta JGL/CJAL"),
    ("PROPUESTA CJAL",            None, None, "Propuesta JGL/CJAL"),
    ("INFORME SECRETAR",          None, None, "Informe Secretaría"),
    ("ADJUDICACION",              None, None, "Adjudicación"),
    ("ADJUDICACIÓN",              None, None, "Adjudicación"),
    ("RESOLUCION ALCALD",         None, None, "Resolución Alcaldía"),
    ("RESOLUCIÓN ALCALD",         None, None, "Resolución Alcaldía"),
    ("AVOCACION",                 None, None, "Resolución Alcaldía"),
    ("AVOCACIÓN",                 None, None, "Resolución Alcaldía"),
    ("REQUERIMIENTO",             None, None, "Requerimiento Documentación"),
    ("PRORROGA",                  None, None, "Prórroga o Modificado"),
    ("PRÓRROGA",                  None, None, "Prórroga o Modificado"),
    ("MODIFICADO",                None, None, "Prórroga o Modificado"),
    ("NOMBRAR SUPLENTE",          None, None, "Otro"),
]

# Clasificador de documentos municipales de contratación

## Estructura de carpetas generada

```
output/
└── Contrato de Servicios/
    └── Procedimiento Abierto/
        └── Aprobación de Pliegos/
            └── documento.docx
```

## Uso

### 1. Requisitos
- Docker y Docker Compose instalados
- API Key de Anthropic

### 2. Preparar
```bash
# Copia tus documentos en la carpeta input/
cp /ruta/tus/documentos/* input/

# Crea el fichero .env con tu API key
echo "ANTHROPIC_API_KEY=sk-ant-..." > .env
```

### 3. Ejecutar
```bash
docker compose run --rm classifier
```

### 4. Resultados
- `output/` → documentos organizados en carpetas
- `results/clasificacion.csv` → índice completo con columnas:
  - `nombre_original` — nombre del fichero original
  - `contrato` — tipo de contrato detectado
  - `procedimiento` — tipo de procedimiento detectado
  - `acto` — tipo de acto detectado
  - `fuente` — "reglas" (gratis) o "ia+reglas" (usó API)
  - `ruta_destino` — ruta final del fichero en output/

---

## Personalización

### Añadir tipos nuevos → `app/taxonomy.py`
- `TIPOS_CONTRATO`, `TIPOS_PROCEDIMIENTO`, `TIPOS_ACTO`: listas de valores válidos
- `REGLAS`: patrones de texto en el nombre del fichero → clasificación sin IA

Cuantas más reglas añadas, menos llamadas a la API se harán y más barato saldrá.

### Ejemplo de regla nueva
```python
# En REGLAS, añade una tupla:
# (patrón_en_mayúsculas, contrato_o_None, procedimiento_o_None, acto_o_None)
("EMERGENCIA", "Contrato de Obras", "Procedimiento Negociado sin Publicidad", None),
```

---

## Coste estimado

| Documentos | % resueltos por reglas | Llamadas IA | Coste aprox. |
|------------|------------------------|-------------|--------------|
| 200        | 70%                    | ~60         | < 0,05 €     |
| 200        | 40%                    | ~120        | < 0,10 €     |
| 500        | 70%                    | ~150        | < 0,12 €     |

Modelo usado: **claude-haiku-4-5** (el más barato de Anthropic).
Solo se envían las primeras 600 caracteres de cada documento, no el texto completo.

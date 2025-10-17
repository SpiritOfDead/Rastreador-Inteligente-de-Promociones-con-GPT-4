# Sistema de Rastreo de Promociones Web con LLM
[![Python](https://img.shields.io/badge/Python-3.8+-blue.svg)](https://www.python.org/)
[![OpenAI API](https://img.shields.io/badge/OpenAI-API%20Enabled-brightgreen)](https://platform.openai.com/docs)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)
[![Scraping Async](https://img.shields.io/badge/Scraping-Asíncrono-orange)]()
[![AI Powered](https://img.shields.io/badge/IA-GPT--4%20Integrated-purple)]()

Sistema de scraping inteligente que utiliza inteligencia artificial (GPT-4) para extraer, analizar y estructurar promociones y descuentos de sitios web aprobados.

---

## Características Principales

- Scraping asíncrono con `aiohttp` para máximo rendimiento
- Análisis con LLM (GPT-4) para detección precisa de ofertas
- Almacenamiento en SQLite o JSON
- Reportes visuales en HTML y Markdown
- Ejecución automática programada
- Multi-sitio configurable desde un solo archivo
- Extracción de códigos, fechas y categorías

---

## Instalación

### 1. Requisitos Previos
- Python 3.8 o superior
- Cuenta de OpenAI con API Key

### 2. Clonar el Repositorio
```bash
git clone https://github.com/tuusuario/rastreador-promociones.git
cd rastreador-promociones
```

### 3. Instalar Dependencias
```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install openai beautifulsoup4 aiohttp lxml schedule
```

---

## Configuración

### API Key
**Opción A – Variable de entorno (recomendada):**
```bash
# Linux/Mac
export OPENAI_API_KEY='tu-api-key'

# Windows
set OPENAI_API_KEY=tu-api-key
```

**Opción B – Editar config.py:**
```python
OPENAI_API_KEY = 'tu-api-key'
```

### Sitios a Rastrear
Agrega tus URLs en `config.py`:
```python
SITIOS_APROBADOS = [
    'https://www.tusitio.com/ofertas',
    'https://www.otrositio.com/promociones'
]
```

---

## Uso del Sistema

### Ejemplo Básico
```python
import asyncio
from rastreador import RastreadorPromociones

async def main():
    rastreador = RastreadorPromociones(api_key="tu-api-key")
    sitios = ["https://www.ejemplo.com/ofertas"]
    promociones = await rastreador.rastrear_sitios(sitios)
    rastreador.guardar_resultados(promociones)

asyncio.run(main())
```

### Uso Completo con Análisis
Incluye base de datos, estadísticas y reportes.
```python
from database import DatabaseManager
from analytics import AnalizadorPromociones, GeneradorReportes
```

El sistema genera automáticamente:
- `promociones.json`
- `reporte_promociones.html`
- `reporte_promociones.md`
- `promociones.db`

---

## Estructura de Datos

```json
{
  "titulo": "50% de descuento en laptops",
  "descripcion": "Obtén hasta 50% en laptops seleccionadas",
  "descuento": "50%",
  "codigo_promocional": "LAPTOP50",
  "fecha_inicio": "2025-10-01",
  "fecha_fin": "2025-10-31",
  "terminos": "Aplica en productos seleccionados",
  "url_origen": "https://www.ejemplo.com/ofertas",
  "sitio_web": "www.ejemplo.com",
  "fecha_extraccion": "2025-10-17T10:30:00",
  "categoria": "Electrónica"
}
```

---

## Personalización

### Cambiar Modelo de LLM
```python
rastreador = RastreadorPromociones(
    api_key=api_key,
    modelo='gpt-4o'  # o gpt-4o-mini
)
```

### Usar Claude en lugar de GPT
```python
from anthropic import Anthropic
```

### Filtros Personalizados
```python
MIN_DESCUENTO_PORCENTAJE = 15
CATEGORIAS_EXCLUIDAS = ['adultos']
```

---

## Casos de Uso
- Agregadores de ofertas
- Monitoreo de competencia
- Alertas automáticas de descuentos
- Análisis de tendencias de precios

---

## Consideraciones

- Solo rastrea sitios públicos o con permiso
- Respeta robots.txt
- No sobrecargues servidores
- Controla el costo de tokens GPT

---

## Solución de Problemas

| Error | Solución |
|-------|-----------|
| Rate limit exceeded | Aumenta DELAY_ENTRE_REQUESTS |
| SSL verify failed | Usa ssl=False en la request |
| No detecta ofertas | Revisa selectores CSS o usa un modelo más potente |

---

## Recursos Útiles
- [OpenAI Docs](https://platform.openai.com/docs)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [aiohttp Docs](https://docs.aiohttp.org/)

---

## Contribuciones
Contribuciones, issues o sugerencias son bienvenidas.
Puedes proponer mejoras como:
- Soporte JS con Playwright o Selenium
- Dashboard web interactivo
- Notificaciones por correo o Telegram

---

## Licencia
Este proyecto está bajo la licencia MIT, libre para uso comercial y personal.

---

### Autor
Creado por [SpiritOfDead].

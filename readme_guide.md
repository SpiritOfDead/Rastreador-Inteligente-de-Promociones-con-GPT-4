# 🚀 Sistema de Rastreo de Promociones Web con LLM

Sistema completo de scraping web que utiliza inteligencia artificial para extraer, analizar y estructurar promociones de sitios web aprobados.

## 📋 Características

- ✅ **Scraping asíncrono** para alto rendimiento
- 🤖 **Análisis con LLM** (GPT-4) para extracción inteligente de datos
- 💾 **Persistencia en SQLite** para almacenamiento estructurado
- 📊 **Análisis avanzado** con estadísticas y tendencias
- 📈 **Reportes visuales** en HTML y Markdown
- ⏰ **Programación automática** para rastreo periódico
- 🔍 **Detección inteligente** de descuentos, códigos promocionales y fechas
- 🌐 **Multi-sitio** con configuración centralizada

## 🛠️ Instalación

### 1. Requisitos Previos

- Python 3.8 o superior
- Cuenta de OpenAI con API key

### 2. Clonar o Descargar los Archivos

Asegúrate de tener todos estos archivos:
```
proyecto/
├── rastreador.py           # Scraper principal
├── config.py               # Configuración
├── database.py             # Gestión de base de datos
├── analytics.py            # Sistema de análisis
├── scheduler.py            # Programador de tareas
├── requirements.txt        # Dependencias
└── README.md              # Esta guía
```

### 3. Instalar Dependencias

```bash
pip install -r requirements.txt
```

O manualmente:
```bash
pip install openai beautifulsoup4 aiohttp lxml schedule
```

## ⚙️ Configuración

### 1. Configurar API Key

**Opción A: Variable de entorno (Recomendado)**
```bash
# Linux/Mac
export OPENAI_API_KEY='tu-api-key-aqui'

# Windows
set OPENAI_API_KEY=tu-api-key-aqui
```

**Opción B: Editar config.py**
```python
OPENAI_API_KEY = 'tu-api-key-aqui'
```

### 2. Configurar Sitios a Rastrear

Edita `config.py` y agrega tus URLs:
```python
SITIOS_APROBADOS = [
    'https://www.tusitio.com/ofertas',
    'https://www.otrosito.com/promociones',
    # Agrega más...
]
```

## 🚀 Uso

### Uso Básico - Rastreo Simple

```python
import asyncio
from rastreador import RastreadorPromociones

async def main():
    rastreador = RastreadorPromociones(api_key="tu-api-key")
    
    sitios = [
        "https://www.ejemplo.com/ofertas",
        "https://www.otro.com/promociones"
    ]
    
    promociones = await rastreador.rastrear_sitios(sitios)
    rastreador.guardar_resultados(promociones)

asyncio.run(main())
```

### Uso Completo - Con Base de Datos y Análisis

```python
import asyncio
from rastreador import RastreadorPromociones
from database import DatabaseManager
from analytics import AnalizadorPromociones, GeneradorReportes
from config import Config

async def main():
    # Inicializar
    rastreador = RastreadorPromociones(
        api_key=Config.OPENAI_API_KEY,
        modelo='gpt-4o-mini'  # o 'gpt-4o' para mayor precisión
    )
    db = DatabaseManager()
    
    # Rastrear
    promociones = await rastreador.rastrear_sitios(Config.SITIOS_APROBADOS)
    
    # Guardar
    datos = [vars(p) for p in promociones]
    db.guardar_promociones(datos)
    
    # Analizar
    analizador = AnalizadorPromociones(datos)
    analisis = analizador.generar_reporte_completo()
    
    # Generar reportes
    GeneradorReportes.generar_html(analisis)
    GeneradorReportes.generar_markdown(analisis)

asyncio.run(main())
```

### Rastreo Programado Automático

```python
import asyncio
from rastreador import RastreadorPromociones
from scheduler import SchedulerRastreo
from database import DatabaseManager
from config import Config

async def main():
    rastreador = RastreadorPromociones(api_key=Config.OPENAI_API_KEY)
    db = DatabaseManager()
    
    scheduler = SchedulerRastreo(
        rastreador=rastreador,
        sitios=Config.SITIOS_APROBADOS,
        db_manager=db
    )
    
    # Ejecutar cada 6 horas automáticamente
    scheduler.iniciar()

asyncio.run(main())
```

## 📊 Estructura de Datos

### Objeto Promoción

```python
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
    "categoria": "Electrónica",
    "precio_original": "$1000",
    "precio_descuento": "$500"
}
```

## 📈 Reportes Generados

El sistema genera automáticamente:

1. **promociones.json** - Datos crudos en JSON
2. **reporte_promociones.html** - Reporte visual interactivo
3. **reporte_promociones.md** - Reporte en Markdown
4. **promociones.db** - Base de datos SQLite

### Ejemplo de Análisis Incluido

- Total de promociones por sitio
- Descuentos promedio y máximos
- Mejores ofertas rankeadas
- Distribución por categorías
- Tendencias temporales
- Códigos promocionales activos

## 🔧 Personalización

### Cambiar Modelo de LLM

```python
# Usar modelo más preciso (más costoso)
rastreador = RastreadorPromociones(
    api_key=api_key,
    modelo='gpt-4o'  # En lugar de gpt-4o-mini
)
```

### Usar Claude en lugar de GPT

```python
# En rastreador.py, reemplaza OpenAI por Anthropic
from anthropic import Anthropic

class RastreadorPromociones:
    def __init__(self, api_key: str, modelo: str = "claude-sonnet-4-5-20250929"):
        self.client = Anthropic(api_key=api_key)
        self.modelo = modelo
    
    def analizar_con_llm(self, contenido: Dict[str, any]) -> List[Dict]:
        # Adaptar la llamada para Claude API
        response = self.client.messages.create(
            model=self.modelo,
            max_tokens=2000,
            messages=[{"role": "user", "content": prompt}]
        )
        # ... resto del código
```

### Agregar Filtros Personalizados

```python
# En config.py
MIN_DESCUENTO_PORCENTAJE = 15  # Solo promociones con 15% o más
CATEGORIAS_EXCLUIDAS = ['adultos', 'prohibido']
KEYWORDS_PROMOCION = ['descuento', 'oferta', 'rebaja']  # Personalizar
```

## 🎯 Casos de Uso

### 1. Monitoreo de Competencia
```python
SITIOS_APROBADOS = [
    'https://competidor1.com/ofertas',
    'https://competidor2.com/promociones',
]
```

### 2. Agregador de Ofertas
```python
# Rastrear múltiples categorías de retailers
SITIOS_APROBADOS = [
    'https://electronica.com/deals',
    'https://moda.com/sales',
    'https://alimentos.com/descuentos',
]
```

### 3. Alertas de Precio
```python
# Combinar con sistema de notificaciones
promociones = await rastreador.rastrear_sitios(sitios)
for promo in promociones:
    if promo.descuento and '50%' in promo.descuento:
        enviar_notificacion(promo)  # Tu función de alerta
```

## ⚠️ Consideraciones Importantes

### Legalidad y Ética
- ✅ Solo rastrea sitios con permiso o públicos
- ✅ Respeta robots.txt
- ✅ Implementa delays entre requests
- ❌ No sobrecargues los servidores

### Costos de API
- **gpt-4o-mini**: ~$0.15 por 1M tokens (económico)
- **gpt-4o**: ~$2.50 por 1M tokens (preciso)
- Estima: ~50-100 sitios por $1 con gpt-4o-mini

### Rendimiento
- Scraping asíncrono: 10-20 sitios en paralelo
- Tiempo estimado: 2-5 segundos por sitio
- 100 sitios: ~5-10 minutos total

## 🐛 Troubleshooting

### Error: "Rate limit exceeded"
```python
# Agregar delay entre requests en config.py
DELAY_ENTRE_REQUESTS = 2  # segundos
```

### Error: "SSL Certificate verify failed"
```python
# En rastreador.py, agregar:
async with session.get(url, ssl=False) as response:
```

### No se extraen promociones
1. Verificar que el sitio tiene contenido público
2. Revisar selectores CSS en `extraer_texto_relevante()`
3. Aumentar el límite de caracteres procesados
4. Usar modelo más potente (gpt-4o)

## 📚 Recursos Adicionales

- [Documentación OpenAI](https://platform.openai.com/docs)
- [BeautifulSoup Docs](https://www.crummy.com/software/BeautifulSoup/bs4/doc/)
- [aiohttp Documentation](https://docs.aiohttp.org/)

## 🤝 Contribuciones

Mejoras sugeridas:
- [ ] Soporte para JavaScript rendering (Playwright/Selenium)
- [ ] Integración con más LLMs (Claude, Gemini)
- [ ] Dashboard web interactivo
- [ ] API REST para acceso externo
- [ ] Notificaciones por email/Telegram
- [ ] Detección de cambios en promociones

## 📄 Licencia

MIT License - Libre para uso comercial y personal

## 💡 Soporte

Para preguntas o problemas:
1. Revisa esta documentación
2. Verifica los logs en `rastreador.log`
3. Consulta los ejemplos de código incluidos

---

**¡Feliz rastreo de promociones! 🎉**
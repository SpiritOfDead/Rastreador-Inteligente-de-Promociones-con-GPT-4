"""
Rastreador Web de Promociones con Análisis LLM
Escanea sitios web aprobados, extrae ofertas y utiliza LLM para estructurar datos
"""

import asyncio
import aiohttp
from bs4 import BeautifulSoup
from dataclasses import dataclass, asdict
from typing import List, Dict, Optional
from datetime import datetime
import json
import re
from urllib.parse import urljoin, urlparse
import logging

# Para el LLM - usar OpenAI o alternativas como Anthropic Claude
# pip install openai beautifulsoup4 aiohttp
from openai import OpenAI

# Configuración de logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)


@dataclass
class Promocion:
    """Estructura de datos para una promoción"""
    titulo: str
    descripcion: str
    descuento: Optional[str]
    codigo_promocional: Optional[str]
    fecha_inicio: Optional[str]
    fecha_fin: Optional[str]
    terminos: Optional[str]
    url_origen: str
    sitio_web: str
    fecha_extraccion: str
    categoria: Optional[str]
    precio_original: Optional[str]
    precio_descuento: Optional[str]


class RastreadorPromociones:
    """Rastreador web asíncrono para extraer promociones"""
    
    def __init__(self, api_key: str, modelo: str = "gpt-4o-mini"):
        """
        Inicializa el rastreador
        
        Args:
            api_key: API key para el LLM (OpenAI)
            modelo: Modelo de OpenAI a utilizar
        """
        self.client = OpenAI(api_key=api_key)
        self.modelo = modelo
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36'
        }
        
    async def obtener_contenido_html(self, session: aiohttp.ClientSession, url: str) -> Optional[str]:
        """Obtiene el contenido HTML de una URL"""
        try:
            async with session.get(url, headers=self.headers, timeout=30) as response:
                if response.status == 200:
                    return await response.text()
                else:
                    logger.warning(f"Error al obtener {url}: Status {response.status}")
                    return None
        except Exception as e:
            logger.error(f"Error al obtener {url}: {str(e)}")
            return None
    
    def extraer_texto_relevante(self, html: str, url: str) -> Dict[str, any]:
        """Extrae texto relevante del HTML usando BeautifulSoup"""
        soup = BeautifulSoup(html, 'html.parser')
        
        # Remover scripts y estilos
        for script in soup(["script", "style", "nav", "footer", "header"]):
            script.decompose()
        
        # Buscar secciones comunes de promociones
        selectores_promo = [
            '.promo', '.promocion', '.oferta', '.descuento', '.deal',
            '.special-offer', '.sale', '[class*="promo"]', '[class*="offer"]',
            '[id*="promo"]', '[id*="offer"]'
        ]
        
        secciones_promo = []
        for selector in selectores_promo:
            elementos = soup.select(selector)
            for elem in elementos:
                texto = elem.get_text(strip=True, separator=' ')
                if len(texto) > 20:  # Filtrar textos muy cortos
                    secciones_promo.append(texto)
        
        # Si no se encuentran secciones específicas, obtener todo el texto del body
        if not secciones_promo:
            body = soup.find('body')
            if body:
                texto_completo = body.get_text(strip=True, separator=' ')
                # Limitar el texto para no sobrecargar el LLM
                secciones_promo = [texto_completo[:5000]]
        
        return {
            'url': url,
            'titulo_pagina': soup.title.string if soup.title else '',
            'contenido': secciones_promo[:10],  # Limitar a 10 secciones
            'meta_descripcion': soup.find('meta', attrs={'name': 'description'})
        }
    
    def analizar_con_llm(self, contenido: Dict[str, any]) -> List[Dict]:
        """Utiliza LLM para extraer y estructurar promociones"""
        
        prompt = f"""Analiza el siguiente contenido de una página web y extrae TODAS las promociones, ofertas y descuentos activos.

URL: {contenido['url']}
Título de la página: {contenido['titulo_pagina']}

Contenido:
{' '.join(contenido['contenido'])}

Por favor, extrae CADA promoción que encuentres y estructura la información en formato JSON con los siguientes campos para cada promoción:
- titulo: Título descriptivo de la promoción
- descripcion: Descripción detallada de la oferta
- descuento: Porcentaje o monto del descuento (ej: "20%", "$50 de descuento")
- codigo_promocional: Código de cupón si existe
- fecha_inicio: Fecha de inicio si se menciona
- fecha_fin: Fecha de expiración si se menciona
- terminos: Términos y condiciones relevantes
- categoria: Categoría del producto/servicio
- precio_original: Precio original si se menciona
- precio_descuento: Precio con descuento si se menciona

Si un campo no está disponible, usa null. 
Responde ÚNICAMENTE con un array JSON válido de promociones, sin texto adicional.
Si no encuentras promociones, responde con un array vacío: []

Ejemplo de formato esperado:
[
  {{
    "titulo": "50% de descuento en laptops",
    "descripcion": "Obtén hasta 50% de descuento en laptops seleccionadas",
    "descuento": "50%",
    "codigo_promocional": "LAPTOP50",
    "fecha_inicio": "2025-10-01",
    "fecha_fin": "2025-10-31",
    "terminos": "Aplica en productos seleccionados",
    "categoria": "Electrónica",
    "precio_original": null,
    "precio_descuento": null
  }}
]"""

        try:
            response = self.client.chat.completions.create(
                model=self.modelo,
                messages=[
                    {"role": "system", "content": "Eres un experto en extracción de datos de promociones. Respondes ÚNICAMENTE con JSON válido, sin markdown ni texto adicional."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.1,
                max_tokens=2000
            )
            
            respuesta = response.choices[0].message.content.strip()
            
            # Limpiar la respuesta por si incluye markdown
            respuesta = respuesta.replace('```json', '').replace('```', '').strip()
            
            promociones = json.loads(respuesta)
            
            if not isinstance(promociones, list):
                logger.warning(f"LLM no devolvió una lista: {type(promociones)}")
                return []
            
            logger.info(f"Extraídas {len(promociones)} promociones de {contenido['url']}")
            return promociones
            
        except json.JSONDecodeError as e:
            logger.error(f"Error al parsear JSON del LLM: {str(e)}")
            logger.error(f"Respuesta recibida: {respuesta[:500]}")
            return []
        except Exception as e:
            logger.error(f"Error al analizar con LLM: {str(e)}")
            return []
    
    async def procesar_sitio(self, session: aiohttp.ClientSession, url: str) -> List[Promocion]:
        """Procesa un sitio web completo"""
        logger.info(f"Procesando: {url}")
        
        html = await self.obtener_contenido_html(session, url)
        if not html:
            return []
        
        contenido = self.extraer_texto_relevante(html, url)
        promociones_data = self.analizar_con_llm(contenido)
        
        # Convertir a objetos Promocion
        promociones = []
        dominio = urlparse(url).netloc
        fecha_actual = datetime.now().isoformat()
        
        for promo_data in promociones_data:
            try:
                promocion = Promocion(
                    titulo=promo_data.get('titulo', ''),
                    descripcion=promo_data.get('descripcion', ''),
                    descuento=promo_data.get('descuento'),
                    codigo_promocional=promo_data.get('codigo_promocional'),
                    fecha_inicio=promo_data.get('fecha_inicio'),
                    fecha_fin=promo_data.get('fecha_fin'),
                    terminos=promo_data.get('terminos'),
                    url_origen=url,
                    sitio_web=dominio,
                    fecha_extraccion=fecha_actual,
                    categoria=promo_data.get('categoria'),
                    precio_original=promo_data.get('precio_original'),
                    precio_descuento=promo_data.get('precio_descuento')
                )
                promociones.append(promocion)
            except Exception as e:
                logger.error(f"Error al crear objeto Promocion: {str(e)}")
        
        return promociones
    
    async def rastrear_sitios(self, urls: List[str]) -> List[Promocion]:
        """Rastrea múltiples sitios de forma asíncrona"""
        async with aiohttp.ClientSession() as session:
            tareas = [self.procesar_sitio(session, url) for url in urls]
            resultados = await asyncio.gather(*tareas)
            
            # Aplanar la lista de resultados
            todas_promociones = []
            for promociones in resultados:
                todas_promociones.extend(promociones)
            
            return todas_promociones
    
    def guardar_resultados(self, promociones: List[Promocion], archivo: str = 'promociones.json'):
        """Guarda los resultados en un archivo JSON"""
        datos = [asdict(promo) for promo in promociones]
        
        with open(archivo, 'w', encoding='utf-8') as f:
            json.dump(datos, f, ensure_ascii=False, indent=2)
        
        logger.info(f"Guardadas {len(promociones)} promociones en {archivo}")
        
        # Generar también un resumen
        self.generar_resumen(promociones)
    
    def generar_resumen(self, promociones: List[Promocion]):
        """Genera un resumen de las promociones encontradas"""
        if not promociones:
            logger.info("No se encontraron promociones")
            return
        
        print("\n" + "="*80)
        print(f"RESUMEN: {len(promociones)} promociones encontradas")
        print("="*80)
        
        # Agrupar por sitio web
        por_sitio = {}
        for promo in promociones:
            if promo.sitio_web not in por_sitio:
                por_sitio[promo.sitio_web] = []
            por_sitio[promo.sitio_web].append(promo)
        
        for sitio, promos in por_sitio.items():
            print(f"\n{sitio}: {len(promos)} promociones")
            for i, promo in enumerate(promos[:3], 1):  # Mostrar máximo 3 por sitio
                print(f"  {i}. {promo.titulo}")
                if promo.descuento:
                    print(f"     Descuento: {promo.descuento}")
                if promo.codigo_promocional:
                    print(f"     Código: {promo.codigo_promocional}")


async def main():
    """Función principal de ejemplo"""
    
    # IMPORTANTE: Reemplaza con tu API key real
    API_KEY = "Tu Api-Key-Aqui"
    
    # Lista de sitios web aprobados para rastrear
    sitios_aprobados = [
        "https://www.olimpica.com/?gclsrc=aw.ds&&kb=ga_sb_14495418882_155523087115&gad_source=1&gad_campaignid=14495418882&gclid=CjwKCAjw0sfHBhB6EiwAQtv5qfWoppHwoTcHYQdcIvBDZ1kh175CtS4KzhXEUJGpjLxtppQbehGpFRoCeo8QAvD_BwE ",
        "https://www.promocajita.com/ ",
        # Agrega más URLs según sea necesario
    ]
    
    # Crear el rastreador
    rastreador = RastreadorPromociones(api_key=API_KEY)
    
    # Rastrear sitios
    logger.info(f"Iniciando rastreo de {len(sitios_aprobados)} sitios...")
    promociones = await rastreador.rastrear_sitios(sitios_aprobados)
    
    # Guardar resultados
    rastreador.guardar_resultados(promociones)
    
    print(f"\n✓ Proceso completado. Total de promociones encontradas: {len(promociones)}")


if __name__ == "__main__":
    # Para ejecutar el rastreador
    asyncio.run(main())

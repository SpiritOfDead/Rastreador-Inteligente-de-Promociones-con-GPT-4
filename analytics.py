# Sistema de análisis de promociones
from collections import Counter, defaultdict
from typing import List, Dict
from datetime import datetime, timedelta
import json
import re

class AnalizadorPromociones:
    
    def __init__(self, promociones: List[dict]):
        self.promociones = promociones
    
    def extraer_porcentaje_descuento(self, descuento: str) -> float:
        if not descuento:
            return 0.0
        
        match = re.search(r'(\d+(?:\.\d+)?)\s*%', descuento)
        if match:
            return float(match.group(1))
        
        return 0.0
    
    def analizar_por_sitio(self) -> Dict:
        por_sitio = defaultdict(list)
        
        for promo in self.promociones:
            por_sitio[promo['sitio_web']].append(promo)
        
        analisis = {}
        for sitio, promos in por_sitio.items():
            descuentos = [self.extraer_porcentaje_descuento(p['descuento']) 
                         for p in promos if p.get('descuento')]
            
            analisis[sitio] = {
                'total_promociones': len(promos),
                'con_codigo': sum(1 for p in promos if p.get('codigo_promocional')),
                'descuento_promedio': sum(descuentos) / len(descuentos) if descuentos else 0,
                'descuento_maximo': max(descuentos) if descuentos else 0,
                'categorias': Counter(p['categoria'] for p in promos if p.get('categoria'))
            }
        
        return analisis
    
    def analizar_tendencias_temporales(self) -> Dict:
        por_mes = defaultdict(list)
        
        for promo in self.promociones:
            if promo.get('fecha_fin'):
                try:
                    fecha = datetime.fromisoformat(promo['fecha_fin'].replace('Z', '+00:00'))
                    mes_año = fecha.strftime('%Y-%m')
                    por_mes[mes_año].append(promo)
                except:
                    pass
        
        return {
            mes: {
                'cantidad': len(promos),
                'sitios_activos': len(set(p['sitio_web'] for p in promos))
            }
            for mes, promos in sorted(por_mes.items())
        }
    
    def identificar_mejores_ofertas(self, top_n: int = 10) -> List[Dict]:
        ofertas_con_descuento = []
        
        for promo in self.promociones:
            if promo.get('descuento'):
                porcentaje = self.extraer_porcentaje_descuento(promo['descuento'])
                if porcentaje > 0:
                    ofertas_con_descuento.append({
                        'titulo': promo['titulo'],
                        'sitio': promo['sitio_web'],
                        'descuento': promo['descuento'],
                        'porcentaje': porcentaje,
                        'codigo': promo.get('codigo_promocional'),
                        'url': promo['url_origen']
                    })
        
        ofertas_con_descuento.sort(key=lambda x: x['porcentaje'], reverse=True)
        
        return ofertas_con_descuento[:top_n]
    
    def analizar_categorias(self) -> Dict:
        categorias = Counter()
        descuentos_por_cat = defaultdict(list)
        
        for promo in self.promociones:
            if promo.get('categoria'):
                categorias[promo['categoria']] += 1
                
                if promo.get('descuento'):
                    porcentaje = self.extraer_porcentaje_descuento(promo['descuento'])
                    if porcentaje > 0:
                        descuentos_por_cat[promo['categoria']].append(porcentaje)
        
        return {
            'distribucion': dict(categorias),
            'descuento_promedio_por_categoria': {
                cat: sum(desc) / len(desc) if desc else 0
                for cat, desc in descuentos_por_cat.items()
            }
        }
    
    def generar_reporte_completo(self) -> Dict:
        return {
            'resumen_general': {
                'total_promociones': len(self.promociones),
                'sitios_unicos': len(set(p['sitio_web'] for p in self.promociones)),
                'con_codigo_promocional': sum(1 for p in self.promociones if p.get('codigo_promocional')),
                'fecha_generacion': datetime.now().isoformat()
            },
            'por_sitio': self.analizar_por_sitio(),
            'categorias': self.analizar_categorias(),
            'mejores_ofertas': self.identificar_mejores_ofertas(),
            'tendencias_temporales': self.analizar_tendencias_temporales()
        }


class GeneradorReportes:
    
    @staticmethod
    def generar_html(analisis: Dict, archivo: str = 'reporte.html'):
        html = f"""
<!DOCTYPE html>
<html lang="es">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Reporte de Promociones</title>
    <style>
        body {{
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
            margin: 0;
            padding: 20px;
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
        }}
        .container {{
            max-width: 1200px;
            margin: 0 auto;
            background: white;
            padding: 30px;
            border-radius: 15px;
            box-shadow: 0 20px 60px rgba(0,0,0,0.3);
        }}
        h1 {{
            color: #667eea;
            text-align: center;
            margin-bottom: 30px;
            font-size: 2.5em;
        }}
        .summary-cards {{
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(250px, 1fr));
            gap: 20px;
            margin-bottom: 30px;
        }}
        .card {{
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            color: white;
            padding: 20px;
            border-radius: 10px;
            text-align: center;
        }}
        .card h3 {{
            margin: 0 0 10px 0;
            font-size: 0.9em;
            opacity: 0.9;
        }}
        .card .value {{
            font-size: 2.5em;
            font-weight: bold;
        }}
        .section {{
            margin-bottom: 40px;
        }}
        .section h2 {{
            color: #333;
            border-bottom: 3px solid #667eea;
            padding-bottom: 10px;
            margin-bottom: 20px;
        }}
        table {{
            width: 100%;
            border-collapse: collapse;
            margin-top: 15px;
        }}
        th, td {{
            padding: 12px;
            text-align: left;
            border-bottom: 1px solid #ddd;
        }}
        th {{
            background-color: #667eea;
            color: white;
        }}
        tr:hover {{
            background-color: #f5f5f5;
        }}
        .promo-item {{
            background: #f8f9fa;
            padding: 15px;
            margin-bottom: 15px;
            border-radius: 8px;
            border-left: 4px solid #667eea;
        }}
        .promo-title {{
            font-weight: bold;
            color: #333;
            margin-bottom: 5px;
        }}
        .promo-discount {{
            color: #e74c3c;
            font-size: 1.2em;
            font-weight: bold;
        }}
        .promo-code {{
            background: #fff3cd;
            padding: 5px 10px;
            border-radius: 5px;
            display: inline-block;
            margin-top: 5px;
            font-family: monospace;
        }}
        .footer {{
            text-align: center;
            margin-top: 40px;
            color: #666;
            font-size: 0.9em;
        }}
    </style>
</head>
<body>
    <div class="container">
        <h1>📊 Reporte de Promociones</h1>
        
        <div class="summary-cards">
            <div class="card">
                <h3>Total Promociones</h3>
                <div class="value">{analisis['resumen_general']['total_promociones']}</div>
            </div>
            <div class="card">
                <h3>Sitios Analizados</h3>
                <div class="value">{analisis['resumen_general']['sitios_unicos']}</div>
            </div>
            <div class="card">
                <h3>Con Código</h3>
                <div class="value">{analisis['resumen_general']['con_codigo_promocional']}</div>
            </div>
        </div>
        
        <div class="section">
            <h2>Mejores Ofertas</h2>
            {''.join([f'''
            <div class="promo-item">
                <div class="promo-title">{oferta['titulo']}</div>
                <div class="promo-discount">{oferta['descuento']}</div>
                <div>Sitio: {oferta['sitio']}</div>
                {f'<div class="promo-code">Código: {oferta["codigo"]}</div>' if oferta.get('codigo') else ''}
            </div>
            ''' for oferta in analisis['mejores_ofertas'][:5]])}
        </div>
        
        <div class="section">
            <h2> Análisis por Sitio Web</h2>
            <table>
                <thead>
                    <tr>
                        <th>Sitio Web</th>
                        <th>Promociones</th>
                        <th>Con Código</th>
                        <th>Descuento Promedio</th>
                    </tr>
                </thead>
                <tbody>
                    {''.join([f'''
                    <tr>
                        <td>{sitio}</td>
                        <td>{datos['total_promociones']}</td>
                        <td>{datos['con_codigo']}</td>
                        <td>{datos['descuento_promedio']:.1f}%</td>
                    </tr>
                    ''' for sitio, datos in analisis['por_sitio'].items()])}
                </tbody>
            </table>
        </div>
        
        <div class="footer">
            <p>Reporte generado el {analisis['resumen_general']['fecha_generacion']}</p>
            <p>Sistema de Rastreo de Promociones v1.0</p>
        </div>
    </div>
</body>
</html>
"""
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(html)
        
        print(f"Reporte HTML generado: {archivo}")
    
    @staticmethod
    def generar_markdown(analisis: Dict, archivo: str = 'reporte.md'):
        """Genera un reporte en formato Markdown"""
        md = f"""#  Reporte de Promociones

**Fecha de generación:** {analisis['resumen_general']['fecha_generacion']}

## Resumen General

- **Total de promociones:** {analisis['resumen_general']['total_promociones']}
- **Sitios únicos:** {analisis['resumen_general']['sitios_unicos']}
- **Promociones con código:** {analisis['resumen_general']['con_codigo_promocional']}

##  Mejores Ofertas

"""
        for i, oferta in enumerate(analisis['mejores_ofertas'][:10], 1):
            md += f"""
### {i}. {oferta['titulo']}
- **Descuento:** {oferta['descuento']}
- **Sitio:** {oferta['sitio']}
"""
            if oferta.get('codigo'):
                md += f"- **Código:** `{oferta['codigo']}`\n"
            md += f"- **URL:** {oferta['url']}\n"
        
        md += "\n##  Análisis por Sitio Web\n\n"
        md += "| Sitio | Promociones | Con Código | Descuento Promedio |\n"
        md += "|-------|-------------|------------|--------------------|\n"
        
        for sitio, datos in analisis['por_sitio'].items():
            md += f"| {sitio} | {datos['total_promociones']} | {datos['con_codigo']} | {datos['descuento_promedio']:.1f}% |\n"
        
        if analisis['categorias']['distribucion']:
            md += "\n##  Distribución por Categorías\n\n"
            for cat, count in sorted(analisis['categorias']['distribucion'].items(), 
                                    key=lambda x: x[1], reverse=True):
                descuento = analisis['categorias']['descuento_promedio_por_categoria'].get(cat, 0)
                md += f"- **{cat}:** {count} promociones (Descuento promedio: {descuento:.1f}%)\n"
        
        with open(archivo, 'w', encoding='utf-8') as f:
            f.write(md)
        
        print(f"Reporte Markdown generado: {archivo}")



import asyncio
from datetime import datetime

async def ejemplo_completo():
    """Ejemplo de uso completo del sistema de rastreo"""
    
    # 1. Configurar el rastreador
    from config import Config
    from database import DatabaseManager
    
    print("="*80)
    print("SISTEMA DE RASTREO DE PROMOCIONES")
    print("="*80)
    
    if not Config.OPENAI_API_KEY:
        print("\nATENCIÓN: Debes configurar tu OPENAI_API_KEY")
        print("Opción 1: Variable de entorno")
        print("  export OPENAI_API_KEY='tu-api-key'")
        print("\nOpción 2: Editar config.py directamente")
        return
    
    from rastreador import RastreadorPromociones
    
    rastreador = RastreadorPromociones(
        api_key=Config.OPENAI_API_KEY,
        modelo=Config.LLM_MODEL
    )
    
    db = DatabaseManager()
    
    print(f"\nRastreando {len(Config.SITIOS_APROBADOS)} sitios web...")
    print("Esto puede tomar varios minutos...\n")
    
    promociones = await rastreador.rastrear_sitios(Config.SITIOS_APROBADOS)
    
    print(f"\nRastreo completado: {len(promociones)} promociones encontradas")
    rastreador.guardar_resultados(promociones, Config.ARCHIVO_SALIDA)
    
    if promociones:
        datos_promociones = [vars(p) for p in promociones]
        nuevas = db.guardar_promociones(datos_promociones)
        print(f" Guardadas {nuevas} nuevas promociones en la base de datos")
        
        print("\n Generando análisis...")
        analizador = AnalizadorPromociones(datos_promociones)
        analisis = analizador.generar_reporte_completo()
        
        generador = GeneradorReportes()
        generador.generar_html(analisis, 'reporte_promociones.html')
        generador.generar_markdown(analisis, 'reporte_promociones.md')
        
        print("\n" + "="*80)
        print("ESTADÍSTICAS GENERALES")
        print("="*80)
        
        for sitio, datos in analisis['por_sitio'].items():
            print(f"\n{sitio}")
            print(f"   • Promociones: {datos['total_promociones']}")
            print(f"   • Con código: {datos['con_codigo']}")
            print(f"   • Descuento promedio: {datos['descuento_promedio']:.1f}%")
            print(f"   • Descuento máximo: {datos['descuento_maximo']:.1f}%")
            
            if datos['categorias']:
                print(f"   • Categorías: {', '.join(datos['categorias'].keys())}")
        
        print("\n" + "="*80)
        print("TOP 5 MEJORES OFERTAS")
        print("="*80)
        
        for i, oferta in enumerate(analisis['mejores_ofertas'][:5], 1):
            print(f"\n{i}. {oferta['titulo']}")
            print(f"   Descuento: {oferta['descuento']}")
            print(f"   Sitio: {oferta['sitio']}")
            if oferta.get('codigo'):
                print(f"   Código: {oferta['codigo']}")
        
        print("\n" + "="*80)
        print(f"Proceso completado exitosamente")
        print(f"Archivos generados:")
        print(f"   • {Config.ARCHIVO_SALIDA}")
        print(f"   • reporte_promociones.html")
        print(f"   • reporte_promociones.md")
        print(f"   • promociones.db")
        print("="*80)


if __name__ == "__main__":
    asyncio.run(ejemplo_completo())

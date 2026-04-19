"""
OportunidadPe - Scraper de noticias de oportunidades de negocio
Medios: Gestión, El Comercio, Andina, La República, Peru21, Correo, El Peruano, Ojo, América TV
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import time
import re
import concurrent.futures
from urllib.parse import urljoin

# Importamos la lógica de base de datos que creamos
from database import insert_noticias

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/120.0.0.0 Safari/537.36"
}

KEYWORDS_OPORTUNIDAD = [
    "licitación", "licitacion", "concurso", "adjudicación", "adjudicacion",
    "inversión", "inversion", "proyecto", "contrato", "convocatoria",
    "fondo", "financiamiento", "subsidio", "bono", "capital",
    "startup", "emprendimiento", "exportación", "exportacion",
    "mype", "pyme", "crédito", "credito", "préstamo", "prestamo",
    "oportunidad", "negocio", "obra pública", "obra publica",
    "ProInversión", "proinversion", "concesión", "concesion",
    "ministerio", "gobierno regional", "municipalidad"
]

SECTORES = {
    "construcción": ["construcción", "obra", "infraestructura", "carretera", "puente", "edificio"],
    "agricultura": ["agro", "agricultura", "campo", "cosecha", "exportación agropecu", "café", "cacao"],
    "tecnología": ["tech", "tecnología", "digital", "software", "startup", "innovación"],
    "salud": ["salud", "hospital", "clínica", "medicamento", "farmac"],
    "energía": ["energía", "minería", "petróleo", "gas", "solar", "eléctric"],
    "educación": ["educación", "escuela", "universidad", "capacitación", "beca"],
    "turismo": ["turismo", "hotel", "restaurante", "gastronomía"],
    "finanzas": ["crédito", "préstamo", "financiamiento", "bono", "fondo"],
}

def classify_sector(text):
    text_lower = text.lower()
    for sector, keywords in SECTORES.items():
        for kw in keywords:
            if kw in text_lower:
                return sector
    return "general"

def is_oportunidad(text):
    text_lower = text.lower()
    return any(kw in text_lower for kw in KEYWORDS_OPORTUNIDAD)

# Configuración de TODAS las fuentes en una sola lista
SCRAPER_CONFIGS = [
    {"url": "https://gestion.pe/ultimas-noticias/", "source": "Gestión", "article_based": True},
    {"url": "https://gestion.pe/economia/empresas/", "source": "Gestión", "article_based": True},
    {"url": "https://gestion.pe/economia/", "source": "Gestión", "article_based": True},
    {"url": "https://andina.pe/agencia/seccion-Economia-2.aspx", "source": "Andina", "article_based": False},
    {"url": "https://andina.pe/agencia/loultimo", "source": "Andina", "article_based": False},
    {"url": "https://elcomercio.pe/economia/", "source": "El Comercio", "article_based": True},
    {"url": "https://larepublica.pe/economia/", "source": "La República", "article_based": False},
    {"url": "https://peru21.pe/economia/", "source": "Peru21", "article_based": False},
    {"url": "https://elperuano.pe/", "source": "El Peruano", "article_based": False},
    {"url": "https://diariocorreo.pe/economia/", "source": "Correo", "article_based": False},
    {"url": "https://americatv.com.pe/noticias", "source": "América TV", "article_based": False},
    {"url": "https://ojo.pe/economia/", "source": "Ojo", "article_based": False},
]

def generic_scrape(config):
    """
    Función de scraping centralizada para evitar repetir código.
    """
    noticias = []
    url = config['url']
    source = config['source']
    is_article_based = config['article_based']
    
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        
        if is_article_based:
            articles = soup.find_all(["article", "div"], class_=re.compile(r"story|card|article|item|noticia"))
            for art in articles[:20]:
                a_tag = art.find("a", href=True)
                h_tag = art.find(["h2", "h3", "h1"])
                if not a_tag or not h_tag:
                    continue
                title = h_tag.get_text(strip=True)
                link = a_tag["href"]
                # Normalizar link absoluto
                link = urljoin(url, link)
                
                if is_oportunidad(title):
                    noticias.append({
                        "titulo": title, "url": link, "fuente": source,
                        "sector": classify_sector(title), "fecha": datetime.now().strftime("%Y-%m-%d")
                    })
        else:
            for a in soup.find_all("a", href=True):
                title = a.get_text(strip=True)
                link = a["href"]
                if len(title) < 20: continue
                # Normalizar link absoluto
                link = urljoin(url, link)
                
                if not link.startswith("http"): continue
                
                if is_oportunidad(title):
                    noticias.append({
                        "titulo": title, "url": link, "fuente": source,
                        "sector": classify_sector(title), "fecha": datetime.now().strftime("%Y-%m-%d")
                    })
    except Exception as e:
        print(f"[{source}] Error extrayendo {url}: {e}")
        
    return noticias

def run_all_scrapers():
    """
    Ejecuta el scraping de todos los medios utilizando paralelismo (Threads)
    para terminar mucho más rápido. Inserta automáticamente en la DB.
    """
    print("Iniciando scraping general asíncrono...")
    all_news = []
    
    # Usar ThreadPoolExecutor para raspar todas las URLs al mismo tiempo (conteo de threads: 5)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_config = {executor.submit(generic_scrape, conf): conf for conf in SCRAPER_CONFIGS}
        
        for future in concurrent.futures.as_completed(future_to_config):
            conf = future_to_config[future]
            try:
                results = future.result()
                all_news.extend(results)
                print(f"  [OK] {conf['source']} ({conf['url']}): {len(results)} oportunidades")
            except Exception as exc:
                print(f"  [ERROR] {conf['source']} generó una excepción: {exc}")

    # Guardar en Base de Datos de golpe (el DB maneja deduplicación vía UNIQUE url)
    inserciones_nuevas = insert_noticias(all_news)
    print(f"\nFinalizado. Total analizado: {len(all_news)} | Nuevas agregadas DB: {inserciones_nuevas}")
    return {"total_analizadas": len(all_news), "nuevas_insertadas": inserciones_nuevas, "data": all_news}

def scrape_custom_url(url):
    """
    Toma una URL abierta, y hace un chequeo heurístico general.
    """
    print(f"Iniciando scraping de URL personalizada: {url}")
    noticias = []
    try:
        r = requests.get(url, headers=HEADERS, timeout=12)
        soup = BeautifulSoup(r.text, "html.parser")
        
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            link = a["href"]
            if len(title) < 20: continue
            
            link = urljoin(url, link)
            if not link.startswith("http"): continue
            
            if is_oportunidad(title):
                noticias.append({
                    "titulo": title, "url": link, "fuente": "Personalizada",
                    "sector": classify_sector(title), "fecha": datetime.now().strftime("%Y-%m-%d")
                })
        
        # Deduplicar en memoria
        seen_urls = set()
        unique_news = []
        for n in noticias:
            if n["url"] not in seen_urls:
                seen_urls.add(n["url"])
                unique_news.append(n)
                
        # Insertar en la Base de Datos
        inserciones = insert_noticias(unique_news)
        print(f"  [OK] Analizadas: {len(unique_news)} | Insertadas DB: {inserciones}")
        return {"total_analizadas": len(unique_news), "nuevas_insertadas": inserciones, "data": unique_news}
    except Exception as e:
        print(f"[URL Personalizada] Error: {e}")
        return {"total_analizadas": 0, "nuevas_insertadas": 0, "data": [], "error": str(e)}

if __name__ == "__main__":
    # Test execution
    res = run_all_scrapers()
    print("Test local terminado.")

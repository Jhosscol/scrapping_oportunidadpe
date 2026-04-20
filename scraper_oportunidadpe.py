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

# HELPERS PROPIOS DE LA ARQUITECTURA
def process_a_tags(soup, source, base_url):
    noticias = []
    for a in soup.find_all("a", href=True):
        title = a.get_text(strip=True)
        link = urljoin(base_url, a["href"])
        if len(title) < 20 or not link.startswith("http"):
            continue
        if is_oportunidad(title):
            noticias.append({
                "titulo": title, "url": link, "fuente": source,
                "sector": classify_sector(title), "fecha": datetime.now().strftime("%Y-%m-%d")
            })
    return noticias

def process_article_tags(soup, source, base_url):
    noticias = []
    articles = soup.find_all(["article", "div"], class_=re.compile(r"story|card|article|item|noticia"))
    for art in articles[:25]:
        a_tag = art.find("a", href=True)
        h_tag = art.find(["h2", "h3", "h1"])
        if not a_tag or not h_tag: continue
        title = h_tag.get_text(strip=True)
        link = urljoin(base_url, a_tag["href"])
        if len(title) < 20 or not link.startswith("http"): continue
        if is_oportunidad(title):
             noticias.append({
                "titulo": title, "url": link, "fuente": source,
                "sector": classify_sector(title), "fecha": datetime.now().strftime("%Y-%m-%d")
            })
    return noticias

# ==========================================
# SCRAPERS INDIVIDUALIZADOS POR CADA SITIO
# ==========================================

def scrape_gestion():
    print("Scrapeando Gestión...")
    urls = ["https://gestion.pe/ultimas-noticias/", "https://gestion.pe/economia/empresas/", "https://gestion.pe/economia/"]
    noticias = []
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            noticias.extend(process_article_tags(soup, "Gestión", url))
        except Exception as e:
            print(f"[Gestión] Error: {e}")
    return noticias

def scrape_andina():
    print("Scrapeando Andina...")
    urls = ["https://andina.pe/agencia/seccion-Economia-2.aspx", "https://andina.pe/agencia/loultimo"]
    noticias = []
    for url in urls:
        try:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            noticias.extend(process_a_tags(soup, "Andina", url))
        except Exception as e:
            print(f"[Andina] Error: {e}")
    return noticias
    
def scrape_elcomercio():
    print("Scrapeando El Comercio...")
    noticias = []
    url = "https://elcomercio.pe/economia/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        noticias.extend(process_article_tags(soup, "El Comercio", url))
    except Exception as e:
        print(f"[El Comercio] Error: {e}")
    return noticias

def scrape_larepublica():
    print("Scrapeando La República...")
    noticias = []
    url = "https://larepublica.pe/economia/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        noticias.extend(process_a_tags(soup, "La República", url))
    except Exception as e:
        print(f"[La República] Error: {e}")
    return noticias

def scrape_peru21():
    print("Scrapeando Peru21...")
    noticias = []
    url = "https://peru21.pe/economia/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        noticias.extend(process_a_tags(soup, "Peru21", url))
    except Exception as e:
        print(f"[Peru21] Error: {e}")
    return noticias

def scrape_elperuano():
    print("Scrapeando El Peruano...")
    noticias = []
    url = "https://elperuano.pe/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        noticias.extend(process_a_tags(soup, "El Peruano", url))
    except Exception as e:
        print(f"[El Peruano] Error: {e}")
    return noticias

def scrape_correo():
    print("Scrapeando Correo...")
    noticias = []
    url = "https://diariocorreo.pe/economia/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        noticias.extend(process_a_tags(soup, "Correo", url))
    except Exception as e:
        print(f"[Correo] Error: {e}")
    return noticias

def scrape_americatv():
    print("Scrapeando América TV...")
    noticias = []
    url = "https://americatv.com.pe/noticias"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        noticias.extend(process_a_tags(soup, "América TV", url))
    except Exception as e:
        print(f"[América] Error: {e}")
    return noticias

def scrape_ojo():
    print("Scrapeando Ojo...")
    noticias = []
    url = "https://ojo.pe/economia/"
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        noticias.extend(process_a_tags(soup, "Ojo", url))
    except Exception as e:
        print(f"[Ojo] Error: {e}")
    return noticias

def run_all_scrapers():
    print("Iniciando scraping de los 9 medios individualizados...")
    all_news = []
    
    # Cada scraper separado listado aquí
    scrapers_funcs = [
        scrape_gestion, scrape_andina, scrape_elcomercio, scrape_larepublica,
        scrape_peru21, scrape_elperuano, scrape_correo, scrape_americatv, scrape_ojo
    ]
    
    # Seguimos ejecutando paralelamente para que sea rápido (Threading conserva el rendimiento)
    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as executor:
        future_to_func = {executor.submit(func): func for func in scrapers_funcs}
        
        for future in concurrent.futures.as_completed(future_to_func):
            func = future_to_func[future]
            try:
                results = future.result()
                all_news.extend(results)
                print(f"  [OK] {func.__name__} completado con {len(results)} oportunidades.")
            except Exception as exc:
                print(f"  [ERROR] {func.__name__} generó excepción: {exc}")

    inserciones_nuevas = insert_noticias(all_news)
    print(f"\nFinalizado. Total analizado: {len(all_news)} | Nuevas agregadas DB: {inserciones_nuevas}")
    return {"total_analizadas": len(all_news), "nuevas_insertadas": inserciones_nuevas, "data": all_news}

def scrape_custom_url(url):
    """
    Scraper reservado exclusivamente para la URL ingresada manualmente
    usando la modalidad "genérica" extrema (todas las etiquetas A).
    """
    print(f"Iniciando scraping de URL personalizada: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=15)
        soup = BeautifulSoup(r.text, "html.parser")
        
        unique_news = process_a_tags(soup, "Personalizada", url)
        
        # Eliminar duplicados en memoria
        seen_urls = set()
        dedup = []
        for n in unique_news:
            if n["url"] not in seen_urls:
                seen_urls.add(n["url"])
                dedup.append(n)
                
        inserciones = insert_noticias(dedup)
        return {"total_analizadas": len(dedup), "nuevas_insertadas": inserciones, "data": dedup}
    except Exception as e:
        print(f"[URL Personalizada] Error: {e}")
        return {"total_analizadas": 0, "nuevas_insertadas": 0, "data": [], "error": str(e)}

if __name__ == "__main__":
    res = run_all_scrapers()
    print("Test local individualizado terminado.")

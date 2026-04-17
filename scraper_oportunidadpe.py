"""
OportunidadPe - Scraper de noticias de oportunidades de negocio
Medios: Gestión, El Comercio, Andina, La República, Peru21, Correo, El Peruano, Ojo, América TV
"""

import requests
from bs4 import BeautifulSoup
from datetime import datetime
import json
import time
import re

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

def scrape_gestion():
    noticias = []
    try:
        urls = [
            "https://gestion.pe/ultimas-noticias/",
            "https://gestion.pe/economia/empresas/",
            "https://gestion.pe/economia/",
        ]
        for url in urls:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            articles = soup.find_all("article") or soup.find_all("div", class_=re.compile(r"story|article|card|item"))
            for art in articles[:15]:
                a_tag = art.find("a", href=True)
                h_tag = art.find(["h2", "h3", "h1"])
                if not a_tag or not h_tag:
                    continue
                title = h_tag.get_text(strip=True)
                link = a_tag["href"]
                if not link.startswith("http"):
                    link = "https://gestion.pe" + link
                if is_oportunidad(title):
                    noticias.append({
                        "titulo": title,
                        "url": link,
                        "fuente": "Gestión",
                        "sector": classify_sector(title),
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                    })
            time.sleep(0.5)
    except Exception as e:
        print(f"[Gestión] Error: {e}")
    return noticias

def scrape_andina():
    noticias = []
    try:
        urls = [
            "https://andina.pe/agencia/seccion-Economia-2.aspx",
            "https://andina.pe/agencia/loultimo",
        ]
        for url in urls:
            r = requests.get(url, headers=HEADERS, timeout=10)
            soup = BeautifulSoup(r.text, "html.parser")
            links = soup.find_all("a", href=True)
            for a in links:
                title = a.get_text(strip=True)
                link = a["href"]
                if len(title) < 20:
                    continue
                if not link.startswith("http"):
                    link = "https://andina.pe" + link
                if is_oportunidad(title):
                    noticias.append({
                        "titulo": title,
                        "url": link,
                        "fuente": "Andina",
                        "sector": classify_sector(title),
                        "fecha": datetime.now().strftime("%Y-%m-%d"),
                    })
            time.sleep(0.5)
    except Exception as e:
        print(f"[Andina] Error: {e}")
    return noticias

def scrape_elcomercio():
    noticias = []
    try:
        url = "https://elcomercio.pe/economia/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        articles = soup.find_all(["article", "div"], class_=re.compile(r"story|card|article|item|noticia"))
        for art in articles[:20]:
            a_tag = art.find("a", href=True)
            h_tag = art.find(["h2", "h3", "h1"])
            if not a_tag or not h_tag:
                continue
            title = h_tag.get_text(strip=True)
            link = a_tag["href"]
            if not link.startswith("http"):
                link = "https://elcomercio.pe" + link
            if is_oportunidad(title):
                noticias.append({
                    "titulo": title,
                    "url": link,
                    "fuente": "El Comercio",
                    "sector": classify_sector(title),
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                })
    except Exception as e:
        print(f"[El Comercio] Error: {e}")
    return noticias

def scrape_larepublica():
    noticias = []
    try:
        url = "https://larepublica.pe/economia/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            link = a["href"]
            if len(title) < 20:
                continue
            if not link.startswith("http"):
                link = "https://larepublica.pe" + link
            if is_oportunidad(title):
                noticias.append({
                    "titulo": title,
                    "url": link,
                    "fuente": "La República",
                    "sector": classify_sector(title),
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                })
    except Exception as e:
        print(f"[La República] Error: {e}")
    return noticias

def scrape_peru21():
    noticias = []
    try:
        url = "https://peru21.pe/economia/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            link = a["href"]
            if len(title) < 20:
                continue
            if not link.startswith("http"):
                link = "https://peru21.pe" + link
            if is_oportunidad(title):
                noticias.append({
                    "titulo": title,
                    "url": link,
                    "fuente": "Peru21",
                    "sector": classify_sector(title),
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                })
    except Exception as e:
        print(f"[Peru21] Error: {e}")
    return noticias

def scrape_elperuano():
    noticias = []
    try:
        url = "https://elperuano.pe/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            link = a["href"]
            if len(title) < 20:
                continue
            if not link.startswith("http"):
                link = "https://elperuano.pe" + link
            if is_oportunidad(title):
                noticias.append({
                    "titulo": title,
                    "url": link,
                    "fuente": "El Peruano",
                    "sector": classify_sector(title),
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                })
    except Exception as e:
        print(f"[El Peruano] Error: {e}")
    return noticias

def scrape_correo():
    noticias = []
    try:
        url = "https://diariocorreo.pe/economia/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            link = a["href"]
            if len(title) < 20:
                continue
            if not link.startswith("http"):
                link = "https://diariocorreo.pe" + link
            if is_oportunidad(title):
                noticias.append({
                    "titulo": title,
                    "url": link,
                    "fuente": "Correo",
                    "sector": classify_sector(title),
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                })
    except Exception as e:
        print(f"[Correo] Error: {e}")
    return noticias

def scrape_americatv():
    noticias = []
    try:
        url = "https://americatv.com.pe/noticias"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            link = a["href"]
            if len(title) < 20:
                continue
            if not link.startswith("http"):
                link = "https://americatv.com.pe" + link
            if is_oportunidad(title):
                noticias.append({
                    "titulo": title,
                    "url": link,
                    "fuente": "América TV",
                    "sector": classify_sector(title),
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                })
    except Exception as e:
        print(f"[América TV] Error: {e}")
    return noticias

def scrape_ojo():
    noticias = []
    try:
        url = "https://ojo.pe/economia/"
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            link = a["href"]
            if len(title) < 20:
                continue
            if not link.startswith("http"):
                link = "https://ojo.pe" + link
            if is_oportunidad(title):
                noticias.append({
                    "titulo": title,
                    "url": link,
                    "fuente": "Ojo",
                    "sector": classify_sector(title),
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                })
    except Exception as e:
        print(f"[Ojo] Error: {e}")
    return noticias

def run_all_scrapers():
    print("Iniciando scraping de los 9 medios peruanos...")
    all_news = []

    scrapers = [
        scrape_gestion,
        scrape_andina,
        scrape_elcomercio,
        scrape_larepublica,
        scrape_peru21,
        scrape_elperuano,
        scrape_correo,
        scrape_americatv,
        scrape_ojo,
    ]

    for scraper_fn in scrapers:
        results = scraper_fn()
        print(f"  [OK] {scraper_fn.__name__}: {len(results)} oportunidades encontradas")
        all_news.extend(results)

    # Deduplicar por título similar
    seen_titles = set()
    unique_news = []
    for n in all_news:
        key = n["titulo"][:50].lower()
        if key not in seen_titles:
            seen_titles.add(key)
            unique_news.append(n)

    print(f"\nTotal oportunidades únicas: {len(unique_news)}")
    return unique_news

def scrape_custom_url(url):
    noticias = []
    print(f"Iniciando scraping de URL personalizada: {url}")
    try:
        r = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(r.text, "html.parser")
        # Heurística simple: buscar enlaces dentro de la página
        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            link = a["href"]
            if len(title) < 20:
                continue
            
            # Normalizar URL relativa
            if link.startswith("/"):
                # extraer dominio base
                from urllib.parse import urlparse
                parsed_url = urlparse(url)
                base_domain = f"{parsed_url.scheme}://{parsed_url.netloc}"
                link = base_domain + link

            if not link.startswith("http"):
                continue

            if is_oportunidad(title):
                noticias.append({
                    "titulo": title,
                    "url": link,
                    "fuente": "Personalizada",
                    "sector": classify_sector(title),
                    "fecha": datetime.now().strftime("%Y-%m-%d"),
                })
        
        # Deduplicar
        seen_titles = set()
        unique_news = []
        for n in noticias:
            key = n["titulo"][:50].lower()
            if key not in seen_titles:
                seen_titles.add(key)
                unique_news.append(n)
                
        print(f"  [OK] Oportunidades encontradas: {len(unique_news)}")
        return unique_news
    except Exception as e:
        print(f"[URL Personalizada] Error: {e}")
        return []

if __name__ == "__main__":
    results = run_all_scrapers()
    with open("noticias.json", "w", encoding="utf-8") as f:
        json.dump(results, f, ensure_ascii=False, indent=2)
    print("Guardado en noticias.json")

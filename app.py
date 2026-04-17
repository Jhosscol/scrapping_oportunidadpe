from flask import Flask, request, jsonify, send_from_directory
import os
import json
from scraper_oportunidadpe import run_all_scrapers, scrape_custom_url

app = Flask(__name__)

# Configuración: sirve archivos estáticos desde el directorio actual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'OportunidadPe.html')

@app.route('/api/noticias', methods=['GET'])
def get_noticias():
    json_path = os.path.join(BASE_DIR, 'noticias.json')
    if os.path.exists(json_path):
        with open(json_path, 'r', encoding='utf-8') as f:
            try:
                data = json.load(f)
                return jsonify(data)
            except:
                return jsonify([])
    return jsonify([])

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    data = request.json or {}
    url = data.get('url')
    
    if url and url.strip():
        # Scrape de URL personalizada
        results = scrape_custom_url(url.strip())
        
        # Opcional: Podríamos mezclarlo con las noticias existentes
        json_path = os.path.join(BASE_DIR, 'noticias.json')
        existing = []
        if os.path.exists(json_path):
            try:
                with open(json_path, 'r', encoding='utf-8') as f:
                    existing = json.load(f)
            except:
                pass
        
        # Añadir las nuevas y deduplicar globalmente
        all_news = results + existing
        seen_titles = set()
        unique_news = []
        for n in all_news:
            key = n["titulo"][:50].lower()
            if key not in seen_titles:
                seen_titles.add(key)
                unique_news.append(n)
                
        # Guardar en json
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(unique_news, f, ensure_ascii=False, indent=2)
            
        return jsonify(unique_news)
    else:
        # Scrape general
        results = run_all_scrapers()
        # Guardar en json
        json_path = os.path.join(BASE_DIR, 'noticias.json')
        with open(json_path, "w", encoding="utf-8") as f:
            json.dump(results, f, ensure_ascii=False, indent=2)
            
        return jsonify(results)

if __name__ == '__main__':
    app.run(debug=True, port=5000)

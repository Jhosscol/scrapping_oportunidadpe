from flask import Flask, request, jsonify, send_from_directory
import os
import time
import threading
from scraper_oportunidadpe import run_all_scrapers, scrape_custom_url
from database import get_active_noticias, soft_delete_old_noticias

app = Flask(__name__)

# Configuracion: sirve archivos estáticos desde el directorio actual
BASE_DIR = os.path.dirname(os.path.abspath(__file__))

# Cargar variables de entorno localmente (.env) de forma segura sin requerir dependencias externas
env_path = os.path.join(BASE_DIR, '.env')
if os.path.exists(env_path):
    with open(env_path, 'r', encoding='utf-8') as f:
        for line in f:
            if '=' in line and not line.strip().startswith('#'):
                key, val = line.strip().split('=', 1)
                os.environ[key] = val

@app.route('/')
def index():
    return send_from_directory(BASE_DIR, 'OportunidadPe.html')

LAST_SCRAPE_TIME = 0
SCRAPE_COOLDOWN = 1800 # 30 minutos

def background_scrape_if_needed():
    global LAST_SCRAPE_TIME
    current_time = time.time()
    # Solo ejecuta si han pasado 30 minutos desde la última vez (evitamos sobrecarga)
    if current_time - LAST_SCRAPE_TIME > SCRAPE_COOLDOWN:
        LAST_SCRAPE_TIME = current_time
        try:
            run_all_scrapers()
        except Exception as e:
            print(f"Error en Scrape fantasma: {e}")

@app.route('/api/noticias', methods=['GET'])
def get_noticias():
    try:
        noticias = get_active_noticias()
        
        # Si la base de datos está totalmente vacía, forzamos un escaneo inmediato para no mostrar 0
        if len(noticias) == 0:
            run_all_scrapers()
            # Actualizamos el medidor de tiempo para que el fantasma descanse 30 min
            global LAST_SCRAPE_TIME
            LAST_SCRAPE_TIME = time.time()
            noticias = get_active_noticias() # Volver a leer la base de datos ya llena
        else:
            # Lanzamiento Fantasma / Híbrido: inicia el scrap en background pero NO frena el GET
            threading.Thread(target=background_scrape_if_needed, daemon=True).start()
        
        return jsonify({
            "success": True, 
            "message": f"Se obtuvieron {len(noticias)} oportunidades activas.", 
            "data": noticias
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error de Base de Datos: {e}", "data": []}), 500

@app.route('/api/scrape', methods=['POST'])
def api_scrape():
    """Ejecuta un scrape de URL o inicia el scrapeo general."""
    data = request.json or {}
    url = data.get('url')
    
    if url and str(url).strip():
        # Scrapeo de URL única: Sigue siendo síncrono porque es 1 sola web, es rápido
        try:
            results = scrape_custom_url(url.strip())
            
            if "error" in results:
                return jsonify({
                    "success": False, 
                    "message": "Error al analizar la URL. Verifica que esté accesible y sea completa (http://...).", 
                    "data": []
                }), 400
                
            return jsonify({
                "success": True,
                "message": f"Análisis finalizado. {results['total_analizadas']} encontradas, {results['nuevas_insertadas']} nuevas agregadas.",
                "data": results.get("data", [])
            }), 200
        except Exception as e:
            return jsonify({"success": False, "message": f"Fallo interno leyendo url: {e}", "data": []}), 500
    else:
        # Scrape general: Ejecutar directamente
        try:
            results = run_all_scrapers()
            return jsonify({
                "success": True,
                "message": f"Scraping completado. {results['total_analizadas']} analizadas. {results['nuevas_insertadas']} nuevas ingresadas.",
                "data": results.get("data", [])
            }), 200
        except Exception as e:
            return jsonify({"success": False, "message": f"Error iniciando proceso de scraping: {e}", "data": []}), 500

@app.route('/api/noticias/limpiar', methods=['POST'])
def limpia_noticias():
    """Aplica soft delete a las noticias más antiguas."""
    data = request.json or {}
    days = data.get('days', 30) # Parámetro días en el body (30 por defecto)
    
    try:
        if type(days) != int or days < 0:
            return jsonify({"success": False, "message": "Los días indicados son inválidos. Envía un número entero positivo.", "data": []}), 400
            
        modificados = soft_delete_old_noticias(days)
        return jsonify({
            "success": True,
            "message": f"Limpieza completada (Soft Delete). Se han ocultado {modificados} oportunidades más antiguas que {days} días.",
            "data": []
        }), 200
    except Exception as e:
        return jsonify({"success": False, "message": f"Error crítico al limpiar registros: {e}", "data": []}), 500

@app.route('/api/ask-ai', methods=['POST'])
def ask_ai():
    """Proxy seguro para conectar con Gemini sin exponer la API Key en HTML"""
    data = request.json or {}
    question = data.get("question", "")
    context = data.get("context", "")
    
    api_key = os.environ.get("GEMINI_API_KEY")
    if not api_key:
        return jsonify({"success": False, "message": "API Key de Gemini no configurada en el servidor (.env)."}), 500

    system_prompt = f"""Eres el asistente de OportunidadPe, un radar de oportunidades de negocio en Perú. 
Tienes acceso a las siguientes noticias de oportunidades detectadas hoy en 9 medios peruanos:

{context}

Responde en español, de forma concisa y práctica. Máximo 4-5 oraciones. 
Da consejos concretos para empresarios y emprendedores peruanos. 
Menciona montos, plazos y entidades cuando sea relevante."""

    url = f"https://generativelanguage.googleapis.com/v1beta/models/gemini-2.5-flash:generateContent?key={api_key}"
    payload = {
        "systemInstruction": { "parts": [{"text": system_prompt}] },
        "contents": [{ "parts": [{"text": question}] }],
        "generationConfig": { "maxOutputTokens": 1000 }
    }
    
    try:
        import requests
        resp = requests.post(url, json=payload, timeout=20)
        resp_data = resp.json()
        
        if "error" in resp_data:
            return jsonify({"success": False, "message": resp_data["error"].get("message", "Error de Gemini")}), 400
            
        text = resp_data.get("candidates", [{}])[0].get("content", {}).get("parts", [{}])[0].get("text", "Sin respuesta.")
        return jsonify({"success": True, "data": text})
    except Exception as e:
        return jsonify({"success": False, "message": f"Error de red contactando IA: {e}"}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)

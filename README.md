# 🇵🇪 OportunidadPe — Radar de Negocios Perú

Scraping automático de 9 medios peruanos para detectar oportunidades de negocio: licitaciones, convocatorias, fondos, inversiones públicas y privadas. Integrado con Gemini AI.

## Características

- **Scraping Concurrente**: Revisa 9 diarios peruanos simultáneamente en pocos segundos usando hilos de ejecución (*Threading*).
- **Base de Datos Robusta**: Usa SQLite (`noticias.db`) asegurando consultas veloces y un sistema de preservación de datos (*Soft Delete*).
- **Asistente IA Privado**: Las consultas a Gemini se procesan en tu propio servidor backend para nunca exponer tu API Key en el código fuente HTML visible.
- **Auto-Actualización**: La plataforma incluye un "Modo Fantasma" que escanea internet automáticamente en segundo plano si la base de datos está vacía o si pasaron 30 minutos desde la última lectura.

## Estructura del proyecto

```
oportunidad-pe/
├── app.py                      ← Servidor Flask principal y API REST (Backend)
├── database.py                 ← Base de Datos y lógica de Soft Delete
├── scraper_oportunidadpe.py    ← Motor de scraping concurrente unificado
├── OportunidadPe.html          ← Entorno visual amigable (Frontend)
├── .env.example                ← Plantilla base para credenciales
└── README.md                   ← Este manual
```

## Instalación y Uso

### 1. Instalar dependencias
Instala los módulos necesarios de Python en tu entorno:
```bash
pip install flask requests beautifulsoup4
```

### 2. Configurar la caja fuerte (IA)
Busca y renombra el archivo `.env.example` a `.env` y pega allí tu clave real de Gemini API.
```env
GEMINI_API_KEY=tu_clave_real_de_gemini
```
*(No te preocupes, el archivo `.env` ya ha sido configurado en `.gitignore` para jamás subir tus claves a GitHub).*

### 3. Iniciar el Super Servidor
Levanta el servidor con Flask directamente desde tu terminal:
```bash
python app.py
```

### 4. Abrir la plataforma
Entra a tu navegador web favorito y dirígete a **[http://localhost:5000](http://localhost:5000)**. En tu primer inicio, puede tomar entre 5 a 10 segundos cargar mientras la IA crea tu base de datos secreta de cero. ¡A partir de ahí, las consultas son inmediatas!

## Medios monitoreados actualmente
* Gestión | El Comercio | Andina | La República | Peru21 | El Peruano | Correo | América TV | Ojo

---
Desarrollado con Python + Gemini AI · OportunidadPe 2026

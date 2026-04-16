# 🇵🇪 OportunidadPe — Radar de Negocios Perú

Scraping automático de 9 medios peruanos para detectar oportunidades de negocio:
licitaciones, convocatorias, fondos, inversiones públicas y privadas.

## 📁 Estructura del proyecto

```
oportunidad-pe/
├── OportunidadPe.html          ← App web completa (abre en navegador)
├── scraper_oportunidadpe.py    ← Scraper Python para los 9 medios
├── noticias.json               ← Datos scrapeados (generado automáticamente)
└── README.md                   ← Este archivo
```

## 🚀 Cómo usar

### 1. Instalar dependencias Python
```bash
pip install requests beautifulsoup4
```

### 2. Ejecutar el scraper
```bash
python scraper_oportunidadpe.py
```
Genera `noticias.json` con las oportunidades encontradas.

### 3. Abrir la app web
Abre `OportunidadPe.html` directamente en tu navegador.
La app ya incluye datos de demo y IA integrada vía Claude API.

## ⚙️ Automatización (producción)

### Windows — Task Scheduler
```
Acción: python C:\ruta\scraper_oportunidadpe.py
Disparador: Cada 2 horas
```

### Linux/Mac — Cron
```bash
0 */2 * * * /usr/bin/python3 /ruta/scraper_oportunidadpe.py
```

### C# .NET — Hangfire (integración backend)
```csharp
RecurringJob.AddOrUpdate(
    "scraper-oportunidad",
    () => ScraperService.RunAsync(),
    Cron.HourInterval(2)
);
```

## 🧠 Medios monitoreados

| Medio | URL | Sección |
|-------|-----|---------|
| Gestión | gestion.pe | /ultimas-noticias/, /economia/ |
| El Comercio | elcomercio.pe | /economia/ |
| Andina | andina.pe | /seccion-Economia/ |
| La República | larepublica.pe | /economia/ |
| Peru21 | peru21.pe | /economia/ |
| El Peruano | elperuano.pe | / |
| Correo | diariocorreo.pe | /economia/ |
| América TV | americatv.com.pe | /noticias |
| Ojo | ojo.pe | /economia/ |

## 🔑 Keywords detectados

El scraper filtra noticias que contengan:
`licitación, convocatoria, adjudicación, inversión, proyecto, contrato,
fondo, financiamiento, subsidio, bono, startup, exportación, mype, pyme,
crédito, préstamo, ProInversión, concesión, obra pública...`

## 🏗️ Arquitectura sugerida (producción)

```
Python Scraper (cada 2h)
    ↓ REST API (FastAPI)
C# ASP.NET Core Backend
    ↓ PostgreSQL
Frontend Web / App móvil
    + Claude AI para análisis
```

## 💰 Modelo de negocio sugerido

- **Free**: Feed general, últimas 24h
- **Pro S/49/mes**: Alertas por email por sector, historial 30 días  
- **Business S/199/mes**: API access, alertas WhatsApp, análisis IA ilimitado

---
Desarrollado con Python + Claude AI · OportunidadPe 2026

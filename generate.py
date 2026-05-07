"""
generate.py — Generador del sitio SEO de SHENCOM.

Uso:
    python3 generate.py

Lee config-shencom.json + data.py y produce:
    dist/
        index.html                  (hub)
        planes-claro/<ciudad>/index.html  (15 ciudades)
        sitemap.xml
        robots.txt
        styles.css

URLs limpias (subfolder pattern), sin extensión .html visible.
"""

from __future__ import annotations

import html
import shutil
from datetime import date
from pathlib import Path

from data import CIUDADES, get_ciudades_vecinas, load_config

ROOT = Path(__file__).parent
DIST = ROOT / "dist"


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def fmt_phone_link(phone: str) -> str:
    """Convierte +593-2-000-0000 a +59320000000 para tel:."""
    return "".join(c for c in phone if c.isdigit() or c == "+")


def wa_link(e164: str, msg: str = "Hola SHENCOM, deseo información sobre planes Claro.") -> str:
    """Construye URL de WhatsApp con mensaje predefinido."""
    digits = "".join(c for c in e164 if c.isdigit())
    return f"https://wa.me/{digits}?text={msg.replace(' ', '%20')}"


def write(path: Path, content: str) -> None:
    """Escribe un archivo creando carpetas padre si no existen."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(content, encoding="utf-8")


# ---------------------------------------------------------------------------
# CSS — un solo stylesheet para todo el sitio
# ---------------------------------------------------------------------------

def render_css(cfg: dict) -> str:
    primario = cfg["sitio"]["color_primario"]
    secundario = cfg["sitio"]["color_secundario"]
    return f""":root {{
  --primario: {primario};
  --secundario: {secundario};
  --gris-claro: #f5f5f5;
  --gris-medio: #999;
  --gris-oscuro: #333;
  --blanco: #fff;
  --max-w: 1100px;
}}
* {{ box-sizing: border-box; margin: 0; padding: 0; }}
html {{ scroll-behavior: smooth; }}
body {{
  font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  color: var(--secundario);
  line-height: 1.6;
  background: var(--blanco);
}}
a {{ color: var(--primario); text-decoration: none; }}
a:hover {{ text-decoration: underline; }}

/* Banner promocional */
.banner-promo {{
  background: var(--primario);
  color: var(--blanco);
  text-align: center;
  padding: 10px 16px;
  font-weight: 600;
  font-size: 14px;
}}
.banner-promo a {{ color: var(--blanco); text-decoration: underline; }}

/* Header */
header.site {{
  background: var(--blanco);
  border-bottom: 1px solid #eee;
  position: sticky; top: 0; z-index: 100;
}}
header.site .wrap {{
  max-width: var(--max-w); margin: 0 auto;
  display: flex; justify-content: space-between; align-items: center;
  padding: 14px 20px;
}}
header.site .logo {{ font-weight: 800; font-size: 22px; color: var(--primario); }}
header.site nav a {{ margin-left: 18px; color: var(--secundario); font-weight: 500; }}
header.site .cta {{
  background: var(--primario); color: var(--blanco);
  padding: 8px 16px; border-radius: 6px; font-weight: 600;
}}
header.site .cta:hover {{ text-decoration: none; opacity: .9; }}

/* Hero */
.hero {{
  background: linear-gradient(135deg, var(--primario) 0%, #b8001f 100%);
  color: var(--blanco);
  padding: 70px 20px;
  text-align: center;
}}
.hero h1 {{ font-size: 38px; margin-bottom: 14px; line-height: 1.2; }}
.hero p {{ font-size: 18px; max-width: 720px; margin: 0 auto 26px; opacity: .95; }}
.hero .ctas {{ display: flex; gap: 12px; justify-content: center; flex-wrap: wrap; }}
.hero .btn {{
  background: var(--blanco); color: var(--primario);
  padding: 13px 26px; border-radius: 6px; font-weight: 700;
}}
.hero .btn.outline {{ background: transparent; color: var(--blanco); border: 2px solid var(--blanco); }}
.hero .btn:hover {{ text-decoration: none; transform: translateY(-1px); }}

/* Secciones */
section.contenido {{ max-width: var(--max-w); margin: 0 auto; padding: 60px 20px; }}
section.contenido h2 {{
  font-size: 28px; margin-bottom: 20px; color: var(--secundario);
}}
section.contenido p {{ margin-bottom: 14px; color: var(--gris-oscuro); }}

/* Tabla de planes */
.planes-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(230px, 1fr));
  gap: 16px; margin-top: 28px;
}}
.plan-card {{
  border: 2px solid #eee; border-radius: 10px; padding: 22px;
  background: var(--blanco); transition: transform .15s, box-shadow .15s;
}}
.plan-card:hover {{ transform: translateY(-3px); box-shadow: 0 8px 24px rgba(0,0,0,.08); }}
.plan-card.destacado, .plan-card.destacado-custom {{
  border-color: var(--primario);
  position: relative;
}}
.plan-card.destacado::before {{
  content: "MÁS POPULAR";
  position: absolute; top: -10px; right: 14px;
  background: var(--primario); color: var(--blanco);
  font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 4px;
  letter-spacing: 1px;
}}
.plan-badge {{
  position: absolute; top: -10px; right: 14px;
  background: var(--primario); color: var(--blanco);
  font-size: 10px; font-weight: 800; padding: 4px 10px; border-radius: 4px;
  letter-spacing: 1px;
}}
.plan-card.destacado-custom::before {{ content: none; }}
.plan-card h3 {{ font-size: 18px; margin-bottom: 8px; }}
.plan-card .precio {{
  font-size: 32px; font-weight: 800; color: var(--primario); margin: 12px 0;
  display: flex; align-items: baseline; gap: 10px; flex-wrap: wrap;
}}
.plan-card .precio small {{ font-size: 14px; color: var(--gris-medio); font-weight: 400; }}
.plan-card .precio-anterior {{
  font-size: 18px; color: var(--gris-medio); font-weight: 500;
  text-decoration: line-through; text-decoration-color: var(--primario);
}}
.plan-card ul {{ list-style: none; margin: 12px 0; }}
.plan-card ul li {{ padding: 4px 0; font-size: 14px; color: var(--gris-oscuro); }}
.plan-card ul li::before {{ content: "✓ "; color: var(--primario); font-weight: 700; }}
.plan-card a.btn-plan {{
  display: block; text-align: center;
  background: var(--primario); color: var(--blanco);
  padding: 10px; border-radius: 6px; font-weight: 600; margin-top: 14px;
}}

/* Sectores chips */
.chips {{ display: flex; flex-wrap: wrap; gap: 8px; margin: 16px 0; }}
.chip {{
  background: var(--gris-claro); padding: 6px 14px; border-radius: 20px;
  font-size: 13px; color: var(--gris-oscuro);
}}

/* Cards (grid de ciudades en hub) */
.ciudades-grid {{
  display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr));
  gap: 12px; margin-top: 24px;
}}
.ciudad-card {{
  background: var(--gris-claro); padding: 18px; border-radius: 8px;
  border-left: 4px solid var(--primario);
  transition: transform .15s;
}}
.ciudad-card:hover {{ transform: translateX(4px); }}
.ciudad-card h3 {{ font-size: 16px; margin-bottom: 4px; }}
.ciudad-card a {{ color: var(--secundario); }}
.ciudad-card .meta {{ font-size: 12px; color: var(--gris-medio); }}

/* FAQ */
.faq details {{
  border: 1px solid #eee; border-radius: 8px;
  padding: 14px 18px; margin-bottom: 10px;
}}
.faq details summary {{ font-weight: 600; cursor: pointer; }}
.faq details[open] summary {{ color: var(--primario); }}
.faq details p {{ margin-top: 10px; color: var(--gris-oscuro); }}

/* Footer */
footer.site {{
  background: var(--secundario); color: #ccc;
  padding: 40px 20px 20px;
  margin-top: 40px;
}}
footer.site .wrap {{ max-width: var(--max-w); margin: 0 auto; }}
footer.site .cols {{ display: grid; grid-template-columns: repeat(auto-fit, minmax(200px, 1fr)); gap: 30px; }}
footer.site h4 {{ color: var(--blanco); margin-bottom: 12px; font-size: 15px; }}
footer.site a {{ color: #ccc; display: block; padding: 3px 0; font-size: 14px; }}
footer.site a:hover {{ color: var(--blanco); }}
footer.site .legal {{ border-top: 1px solid #444; margin-top: 30px; padding-top: 20px; font-size: 13px; text-align: center; color: var(--gris-medio); }}

/* Floating WA */
.wa-float {{
  position: fixed; bottom: 20px; right: 20px;
  background: #25D366; color: var(--blanco);
  width: 56px; height: 56px; border-radius: 50%;
  display: flex; align-items: center; justify-content: center;
  font-size: 28px; box-shadow: 0 4px 14px rgba(0,0,0,.2);
  z-index: 200;
}}
.wa-float:hover {{ text-decoration: none; transform: scale(1.06); }}

/* Responsive */
@media (max-width: 720px) {{
  .hero h1 {{ font-size: 28px; }}
  header.site nav {{ display: none; }}
  section.contenido {{ padding: 40px 18px; }}
}}
"""


# ---------------------------------------------------------------------------
# Componentes HTML reutilizables
# ---------------------------------------------------------------------------

def render_banner(cfg: dict) -> str:
    """Renderiza todas las promociones activas (acepta lista nueva o banner único legacy)."""
    promos = cfg.get("promociones")
    if promos is None:
        # compatibilidad con estructura antigua banner_promocional
        b = cfg.get("banner_promocional", {})
        if not b.get("activo"):
            return ""
        promos = [{
            "activo": True,
            "texto": b.get("texto", ""),
            "url": b.get("url_destino") or "#planes",
            "color_fondo": b.get("color_fondo", cfg["sitio"]["color_primario"]),
        }]

    parts = []
    for p in promos:
        if not p.get("activo"):
            continue
        texto = html.escape(p.get("texto", ""))
        color = p.get("color_fondo", cfg["sitio"]["color_primario"])
        url = p.get("url") or "#planes"
        parts.append(f'<div class="banner-promo" style="background:{color}"><a href="{url}">{texto}</a></div>')
    return "".join(parts)


def render_header(cfg: dict, is_subpage: bool = False) -> str:
    base = "../../" if is_subpage else ""
    tel_link = fmt_phone_link(cfg["empresa"]["telefono_principal"])
    return f"""<header class="site">
  <div class="wrap">
    <a href="{base}index.html" class="logo">{html.escape(cfg["empresa"]["nombre_comercial"])}</a>
    <nav>
      <a href="{base}index.html#planes">Planes</a>
      <a href="{base}index.html#cobertura">Cobertura</a>
      <a href="{base}index.html#contacto">Contacto</a>
      <a href="tel:{tel_link}" class="cta">Llamar ahora</a>
    </nav>
  </div>
</header>"""


def render_planes_grid(cfg: dict, tipo: str = "internet_hogar") -> str:
    key = f"planes_{tipo}"
    planes = cfg.get(key, [])
    if not planes:
        return ""
    cards = []
    wa_base = cfg["empresa"]["whatsapp_e164"]
    for p in planes:
        clase = "plan-card destacado" if p.get("destacado") else "plan-card"

        # Beneficios desde JSON; fallback a defaults si no hay
        beneficios = p.get("beneficios")
        if not beneficios:
            beneficios = []
            if "velocidad_mbps" in p:
                beneficios = [f"{p['velocidad_mbps']} Mbps simétricos", "WiFi incluido", "Instalación profesional"]
            elif "datos_gb" in p:
                beneficios = [f"{p['datos_gb']} GB de datos móviles", f"Minutos {p.get('minutos', 'ilimitados').lower()}"]

        items_html = "".join(f"<li>{html.escape(i)}</li>" for i in beneficios)

        # Badge personalizado (sobreescribe el "MÁS POPULAR" automático del CSS si está)
        badge_html = ""
        badge_text = (p.get("badge") or "").strip()
        if badge_text:
            badge_html = f'<span class="plan-badge">{html.escape(badge_text)}</span>'
            # si tiene badge custom, no añadimos el "destacado" CSS para no duplicar
            if p.get("destacado") and badge_text:
                clase = "plan-card destacado-custom"

        # Precio anterior tachado (si aplica)
        precio_anterior = p.get("precio_anterior_usd") or 0
        precio_anterior_html = ""
        if precio_anterior and precio_anterior > p["precio_usd"]:
            precio_anterior_html = f'<span class="precio-anterior">${precio_anterior:.2f}</span>'

        # WhatsApp con mensaje específico al plan
        wa = wa_link(wa_base, f"Hola SHENCOM, deseo contratar el {p['nombre']}.")

        cards.append(f"""<div class="{clase}">
  {badge_html}
  <h3>{html.escape(p['nombre'])}</h3>
  <div class="precio">{precio_anterior_html}${p['precio_usd']:.2f}<small>/mes + IVA</small></div>
  <ul>{items_html}</ul>
  <a class="btn-plan" href="{wa}">Contratar por WhatsApp</a>
</div>""")
    return f'<div class="planes-grid">{"".join(cards)}</div>'


def render_footer(cfg: dict, is_subpage: bool = False) -> str:
    base = "../../" if is_subpage else ""
    emp = cfg["empresa"]
    redes = cfg.get("redes_sociales", {})
    redes_html = ""
    for nombre, url in redes.items():
        if url:
            redes_html += f'<a href="{html.escape(url)}" rel="noopener" target="_blank">{nombre.title()}</a>'

    ciudades_links = "".join(
        f'<a href="{base}planes-claro/{c["slug"]}/index.html">{html.escape(c["nombre"])}</a>'
        for c in CIUDADES[:8]
    )

    year = date.today().year
    return f"""<footer class="site">
  <div class="wrap">
    <div class="cols">
      <div>
        <h4>{html.escape(emp["nombre_comercial"])}</h4>
        <p style="font-size:14px;color:#aaa;margin-bottom:10px">{html.escape(emp["tagline"])}</p>
        <p style="font-size:13px;color:#888">RUC: {html.escape(emp["ruc"])}</p>
        <p style="font-size:13px;color:#888">{html.escape(emp["direccion_matriz"])}</p>
      </div>
      <div>
        <h4>Contacto</h4>
        <a href="tel:{fmt_phone_link(emp['telefono_principal'])}">📞 {html.escape(emp['telefono_principal'])}</a>
        <a href="{wa_link(emp['whatsapp_e164'])}">💬 WhatsApp</a>
        <a href="mailto:{html.escape(emp['email_ventas'])}">✉ {html.escape(emp['email_ventas'])}</a>
        <p style="font-size:13px;color:#888;margin-top:10px">{html.escape(emp['horario_atencion'])}</p>
      </div>
      <div>
        <h4>Cobertura</h4>
        {ciudades_links}
      </div>
      <div>
        <h4>Redes</h4>
        {redes_html or '<p style="font-size:13px;color:#888">Próximamente</p>'}
      </div>
    </div>
    <div class="legal">
      © {year} {html.escape(emp["nombre_comercial"])} — Distribuidor Autorizado de Claro Ecuador. Todos los derechos reservados.
    </div>
  </div>
</footer>
<a class="wa-float" href="{wa_link(emp['whatsapp_e164'])}" aria-label="Chatear por WhatsApp">💬</a>"""


# ---------------------------------------------------------------------------
# Schema.org JSON-LD
# ---------------------------------------------------------------------------

def render_schema_local_business(cfg: dict, ciudad=None) -> str:
    """JSON-LD LocalBusiness — variante por ciudad si aplica."""
    emp = cfg["empresa"]
    if ciudad:
        nombre = f"{emp['nombre_comercial']} — Sucursal {ciudad['nombre']}"
        tel = cfg["telefonos_zonales"].get(ciudad["nombre"], emp["telefono_principal"])
        locality = ciudad["nombre"]
        region = ciudad["provincia"]
    else:
        nombre = emp["nombre_comercial"]
        tel = emp["telefono_principal"]
        locality = emp["ciudad_matriz"]
        region = "Pichincha"

    import json as _json
    data = {
        "@context": "https://schema.org",
        "@type": "TelecommunicationsBusiness",
        "name": nombre,
        "description": emp["tagline"],
        "telephone": tel,
        "email": emp["email_ventas"],
        "address": {
            "@type": "PostalAddress",
            "addressLocality": locality,
            "addressRegion": region,
            "addressCountry": "EC",
            "streetAddress": emp["direccion_matriz"],
        },
        "url": cfg["sitio"]["dominio"],
    }
    return f'<script type="application/ld+json">{_json.dumps(data, ensure_ascii=False)}</script>'


# ---------------------------------------------------------------------------
# Páginas
# ---------------------------------------------------------------------------

def render_head(title: str, meta_desc: str, canonical: str, cfg: dict, is_subpage: bool = False) -> str:
    base = "../../" if is_subpage else ""
    ga = cfg["sitio"].get("google_analytics_id", "")
    ga_tag = ""
    if ga and not ga.startswith("G-XXXX"):
        ga_tag = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={ga}"></script>
<script>window.dataLayer=window.dataLayer||[];function gtag(){{dataLayer.push(arguments);}}gtag('js',new Date());gtag('config','{ga}');</script>"""
    gsc = cfg["sitio"].get("google_search_console_token", "")
    gsc_tag = f'<meta name="google-site-verification" content="{html.escape(gsc)}">' if gsc and not gsc.startswith("PEGAR") else ""
    return f"""<!DOCTYPE html>
<html lang="es-EC">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{html.escape(title)}</title>
<meta name="description" content="{html.escape(meta_desc)}">
<link rel="canonical" href="{canonical}">
<meta property="og:title" content="{html.escape(title)}">
<meta property="og:description" content="{html.escape(meta_desc)}">
<meta property="og:url" content="{canonical}">
<meta property="og:type" content="website">
<meta property="og:locale" content="es_EC">
<link rel="stylesheet" href="{base}styles.css">
{gsc_tag}
{ga_tag}
</head>
<body>"""


def render_index(cfg: dict) -> str:
    dominio = cfg["sitio"]["dominio"]
    title = cfg["sitio"]["titulo_marca"]
    desc = cfg["sitio"]["descripcion_meta"]
    head = render_head(title, desc, f"{dominio}/", cfg, is_subpage=False)
    banner = render_banner(cfg)
    header = render_header(cfg)
    schema = render_schema_local_business(cfg)

    ciudades_html = "".join(
        f'<a href="planes-claro/{c["slug"]}/index.html" class="ciudad-card-link"><div class="ciudad-card">'
        f'<h3>{html.escape(c["nombre"])}</h3>'
        f'<p class="meta">{html.escape(c["provincia"])} · {c["poblacion_aprox"]:,} hab.</p>'
        f'</div></a>'
        for c in CIUDADES
    )

    planes_internet = render_planes_grid(cfg, "internet_hogar")
    planes_movil = render_planes_grid(cfg, "pospago_movil")
    footer = render_footer(cfg)

    return f"""{head}
{banner}
{header}
<section class="hero">
  <h1>Planes Claro Ecuador con SHENCOM</h1>
  <p>Distribuidor autorizado de Claro. Internet hogar, planes móviles e instalación profesional en {len(CIUDADES)} ciudades del país.</p>
  <div class="ctas">
    <a class="btn" href="{wa_link(cfg['empresa']['whatsapp_e164'])}">Contratar por WhatsApp</a>
    <a class="btn outline" href="#planes">Ver planes</a>
  </div>
</section>

<section class="contenido" id="planes">
  <h2>Planes de Internet Hogar</h2>
  <p>Todas las velocidades incluyen instalación, equipo WiFi y soporte 24/7. Disponibilidad sujeta a cobertura de fibra óptica.</p>
  {planes_internet}
</section>

<section class="contenido">
  <h2>Planes Pospago Móvil</h2>
  <p>Minutos ilimitados a Ecuador, datos móviles, SMS y portabilidad gratuita.</p>
  {planes_movil}
</section>

<section class="contenido" id="cobertura">
  <h2>Cobertura por Ciudad</h2>
  <p>Selecciona tu ciudad para ver disponibilidad, sectores cubiertos y contacto local.</p>
  <div class="ciudades-grid">{ciudades_html}</div>
</section>

<section class="contenido faq" id="faq">
  <h2>Preguntas Frecuentes</h2>
  <details><summary>¿SHENCOM es Claro?</summary><p>SHENCOM es <strong>distribuidor autorizado</strong> de Claro Ecuador. Comercializa los servicios oficiales de Claro con respaldo y soporte directo.</p></details>
  <details><summary>¿Cuánto tarda la instalación?</summary><p>Entre 24 y 120 horas hábiles dependiendo de la ciudad y disponibilidad de cobertura. Verifica el detalle en la página de tu ciudad.</p></details>
  <details><summary>¿Qué documentos necesito para contratar?</summary><p>Cédula de identidad vigente y comprobante de domicilio (planilla de servicios básicos no mayor a 3 meses).</p></details>
  <details><summary>¿Hacen portabilidad de número?</summary><p>Sí, la portabilidad es gratuita y conservas tu número actual en menos de 24 horas.</p></details>
</section>

{footer}
{schema}
</body></html>"""


def render_ciudad(cfg: dict, ciudad: dict) -> str:
    dominio = cfg["sitio"]["dominio"]
    title = f"Planes Claro en {ciudad['nombre']} | SHENCOM Distribuidor Autorizado"
    desc = (f"Planes Claro internet hogar y pospago en {ciudad['nombre']}. "
            f"Distribuidor autorizado SHENCOM con cobertura en {', '.join(ciudad['sectores'][:4])} y más. "
            f"Instalación en {ciudad['tiempo_instalacion']}.")
    canonical = f"{dominio}/planes-claro/{ciudad['slug']}/"
    head = render_head(title, desc, canonical, cfg, is_subpage=True)
    banner = render_banner(cfg)
    header = render_header(cfg, is_subpage=True)
    schema = render_schema_local_business(cfg, ciudad)

    tel_zonal = cfg["telefonos_zonales"].get(ciudad["nombre"], cfg["empresa"]["telefono_principal"])
    wa = wa_link(cfg["empresa"]["whatsapp_e164"],
                 f"Hola SHENCOM, deseo información sobre planes Claro en {ciudad['nombre']}.")

    sectores_chips = "".join(f'<span class="chip">{html.escape(s)}</span>' for s in ciudad["sectores"])
    planes_internet = render_planes_grid(cfg, "internet_hogar")

    vecinas = get_ciudades_vecinas(ciudad["slug"])
    vecinas_html = ""
    if vecinas:
        vecinas_links = "".join(
            f'<a href="../{v["slug"]}/index.html" class="ciudad-card-link"><div class="ciudad-card">'
            f'<h3>Planes Claro en {html.escape(v["nombre"])}</h3>'
            f'<p class="meta">{html.escape(v["provincia"])}</p>'
            f'</div></a>'
            for v in vecinas
        )
        vecinas_html = f"""<section class="contenido">
  <h2>También cubrimos cerca de {html.escape(ciudad['nombre'])}</h2>
  <div class="ciudades-grid">{vecinas_links}</div>
</section>"""

    footer = render_footer(cfg, is_subpage=True)

    return f"""{head}
{banner}
{header}
<section class="hero">
  <h1>Planes Claro en {html.escape(ciudad['nombre'])}</h1>
  <p>Distribuidor autorizado de Claro en {html.escape(ciudad['provincia'])}. Internet hogar, pospago móvil e instalación profesional con atención local.</p>
  <div class="ctas">
    <a class="btn" href="{wa}">Cotizar por WhatsApp</a>
    <a class="btn outline" href="tel:{fmt_phone_link(tel_zonal)}">📞 {html.escape(tel_zonal)}</a>
  </div>
</section>

<section class="contenido">
  <h2>Servicios Claro disponibles en {html.escape(ciudad['nombre'])}</h2>
  <p>{html.escape(ciudad['paragraph_intro'])}</p>
  <p><strong>Cobertura:</strong> {html.escape(ciudad['cobertura_nota'])}</p>
  <p><strong>Tiempo promedio de instalación:</strong> {html.escape(ciudad['tiempo_instalacion'])}.</p>
</section>

<section class="contenido">
  <h2>Sectores con cobertura en {html.escape(ciudad['nombre'])}</h2>
  <p>SHENCOM gestiona instalaciones Claro en los siguientes sectores. Si tu zona no está listada, consulta disponibilidad puntual:</p>
  <div class="chips">{sectores_chips}</div>
</section>

<section class="contenido" id="planes">
  <h2>Planes de Internet Hogar para {html.escape(ciudad['nombre'])}</h2>
  <p>Velocidades simétricas con fibra óptica donde haya cobertura. Todos los planes incluyen instalación, router WiFi y soporte técnico.</p>
  {planes_internet}
</section>

<section class="contenido faq">
  <h2>Preguntas frecuentes — {html.escape(ciudad['nombre'])}</h2>
  <details><summary>¿Hay cobertura de fibra Claro en mi sector de {html.escape(ciudad['nombre'])}?</summary><p>Cobrimos los principales sectores: {html.escape(', '.join(ciudad['sectores'][:5]))} entre otros. Para verificar tu dirección exacta, contáctanos por WhatsApp.</p></details>
  <details><summary>¿Cuánto tarda la instalación en {html.escape(ciudad['nombre'])}?</summary><p>Entre {html.escape(ciudad['tiempo_instalacion'])} desde la confirmación del contrato y verificación de cobertura.</p></details>
  <details><summary>¿Qué teléfono debo llamar para soporte en {html.escape(ciudad['nombre'])}?</summary><p>Atención local en {html.escape(tel_zonal)}. También puedes escribir por WhatsApp para agilizar.</p></details>
  <details><summary>¿Puedo migrar desde otra operadora a Claro en {html.escape(ciudad['nombre'])}?</summary><p>Sí, la portabilidad es gratuita y SHENCOM gestiona todo el trámite por ti.</p></details>
</section>

{vecinas_html}

{footer}
{schema}
</body></html>"""


# ---------------------------------------------------------------------------
# Sitemap & robots
# ---------------------------------------------------------------------------

def render_sitemap(cfg: dict) -> str:
    dominio = cfg["sitio"]["dominio"]
    today = date.today().isoformat()
    urls = [f"{dominio}/"]
    urls += [f"{dominio}/planes-claro/{c['slug']}/" for c in CIUDADES]
    items = "\n".join(
        f"  <url><loc>{u}</loc><lastmod>{today}</lastmod><changefreq>weekly</changefreq>"
        f"<priority>{'1.0' if i == 0 else '0.8'}</priority></url>"
        for i, u in enumerate(urls)
    )
    return f"""<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">
{items}
</urlset>"""


def render_robots(cfg: dict) -> str:
    dominio = cfg["sitio"]["dominio"]
    return f"""User-agent: *
Allow: /

Sitemap: {dominio}/sitemap.xml
"""


def render_netlify_toml() -> str:
    return """# Configuración de Netlify (generada automáticamente)
[build]
  publish = "."

[[redirects]]
  from = "/planes-claro/:ciudad/index.html"
  to = "/planes-claro/:ciudad/"
  status = 301
  force = true

[[headers]]
  for = "/*"
  [headers.values]
    X-Frame-Options = "SAMEORIGIN"
    X-Content-Type-Options = "nosniff"
    Referrer-Policy = "strict-origin-when-cross-origin"
    Permissions-Policy = "geolocation=(), microphone=(), camera=()"

[[headers]]
  for = "/styles.css"
  [headers.values]
    Cache-Control = "public, max-age=604800"

[[headers]]
  for = "/sitemap.xml"
  [headers.values]
    Content-Type = "application/xml"
"""


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

def main() -> None:
    cfg = load_config()
    if DIST.exists():
        shutil.rmtree(DIST)
    DIST.mkdir(parents=True)

    # CSS
    write(DIST / "styles.css", render_css(cfg))

    # Hub
    write(DIST / "index.html", render_index(cfg))
    print("✓ index.html")

    # Páginas por ciudad
    for c in CIUDADES:
        path = DIST / "planes-claro" / c["slug"] / "index.html"
        write(path, render_ciudad(cfg, c))
        print(f"✓ planes-claro/{c['slug']}/")

    # Sitemap + robots + netlify.toml
    write(DIST / "sitemap.xml", render_sitemap(cfg))
    write(DIST / "robots.txt", render_robots(cfg))
    write(DIST / "netlify.toml", render_netlify_toml())
    print("✓ sitemap.xml")
    print("✓ robots.txt")
    print("✓ netlify.toml")

    total = 1 + len(CIUDADES)
    print(f"\n✅ Sitio generado en dist/  ({total} páginas + sitemap + robots + styles)")
    print(f"   Abrir: file://{DIST}/index.html")
    print(f"   Subir a Netlify: arrastra la carpeta 'dist' a app.netlify.com/drop")


if __name__ == "__main__":
    main()

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
    return """:root {
  --brand: #E60026;
  --brand-dark: #B8001F;
  --brand-soft: #FFE8EC;
  --ink: #0A0E1A;
  --ink-2: #111827;
  --gray-700: #374151;
  --gray-500: #6B7280;
  --gray-400: #9CA3AF;
  --gray-300: #D1D5DB;
  --gray-200: #E5E7EB;
  --gray-100: #F3F4F6;
  --gray-50: #F9FAFB;
  --bg: #FFFFFF;
  --bg-soft: #FAFAFA;
  --success: #10B981;
  --shadow-sm: 0 1px 2px rgba(15,23,42,.04), 0 1px 3px rgba(15,23,42,.06);
  --shadow-md: 0 4px 12px rgba(15,23,42,.06), 0 2px 4px rgba(15,23,42,.04);
  --shadow-lg: 0 12px 32px rgba(15,23,42,.08), 0 4px 12px rgba(15,23,42,.04);
  --shadow-xl: 0 24px 48px rgba(15,23,42,.10);
  --radius-sm: 6px;
  --radius-md: 10px;
  --radius-lg: 16px;
  --max-w: 1200px;
  --max-w-narrow: 960px;
  --transition: 200ms cubic-bezier(.4,0,.2,1);
}
* { box-sizing: border-box; margin: 0; padding: 0; }
*:focus-visible { outline: 2px solid var(--brand); outline-offset: 2px; border-radius: 2px; }
html { scroll-behavior: smooth; -webkit-text-size-adjust: 100%; }
body {
  font-family: 'Inter', -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;
  font-feature-settings: 'cv02','cv03','cv11';
  color: var(--ink); line-height: 1.6; background: var(--bg);
  -webkit-font-smoothing: antialiased; text-rendering: optimizeLegibility;
}
img { max-width: 100%; display: block; }
a { color: var(--brand); text-decoration: none; transition: color var(--transition); }
a:hover { color: var(--brand-dark); }

/* Banner promo */
.banner-promo { background: var(--ink); color: #fff; text-align: center; padding: 10px 16px; font-size: 13.5px; font-weight: 500; }
.banner-promo a { color: #fff; text-decoration: none; }
.banner-promo a:hover { text-decoration: underline; }

/* Header */
header.site {
  background: rgba(255,255,255,.85);
  backdrop-filter: saturate(180%) blur(14px);
  -webkit-backdrop-filter: saturate(180%) blur(14px);
  border-bottom: 1px solid var(--gray-200);
  position: sticky; top: 0; z-index: 100;
}
header.site .wrap { max-width: var(--max-w); margin: 0 auto; display: flex; justify-content: space-between; align-items: center; padding: 14px 24px; gap: 24px; }
header.site .logo { font-weight: 800; font-size: 22px; color: var(--ink); letter-spacing: -0.02em; display: flex; align-items: center; gap: 8px; }
header.site .logo .dot { width: 10px; height: 10px; border-radius: 50%; background: var(--brand); }
header.site nav { display: flex; align-items: center; gap: 4px; }
header.site nav a { color: var(--gray-700); font-weight: 500; font-size: 14.5px; padding: 8px 14px; border-radius: var(--radius-sm); }
header.site nav a:hover { color: var(--ink); background: var(--gray-100); }
header.site .cta { background: var(--ink); color: #fff !important; padding: 10px 18px; border-radius: var(--radius-sm); font-weight: 600; font-size: 14px; box-shadow: var(--shadow-sm); }
header.site .cta:hover { background: var(--brand); }

/* Hero */
.hero { position: relative; isolation: isolate; padding: 110px 24px 90px; color: #fff; overflow: hidden; background: #0A0E1A; }
.hero::before {
  content: ""; position: absolute; inset: 0; z-index: -2;
  background-image: url('https://images.unsplash.com/photo-1451187580459-43490279c0fa?w=2400&q=80&auto=format&fit=crop');
  background-size: cover; background-position: center;
  filter: brightness(.42) saturate(1.1);
}
.hero::after {
  content: ""; position: absolute; inset: 0; z-index: -1;
  background:
    radial-gradient(60% 80% at 80% 20%, rgba(230,0,38,.30), transparent 60%),
    linear-gradient(180deg, rgba(10,14,26,.55) 0%, rgba(10,14,26,.85) 100%);
}
.hero .wrap { max-width: var(--max-w); margin: 0 auto; }
.hero .eyebrow {
  display: inline-flex; align-items: center; gap: 8px;
  background: rgba(255,255,255,.10);
  border: 1px solid rgba(255,255,255,.18);
  backdrop-filter: blur(8px);
  padding: 6px 14px; border-radius: 100px;
  font-size: 13px; font-weight: 500; color: #fff; margin-bottom: 22px;
}
.hero .eyebrow .pulse { width: 8px; height: 8px; background: var(--success); border-radius: 50%; box-shadow: 0 0 0 4px rgba(16,185,129,.25); }
.hero h1 { font-size: clamp(34px, 5.5vw, 60px); line-height: 1.05; letter-spacing: -0.035em; font-weight: 800; max-width: 880px; margin-bottom: 22px; }
.hero h1 .accent { background: linear-gradient(135deg, #FF3650 0%, #E60026 100%); -webkit-background-clip: text; background-clip: text; -webkit-text-fill-color: transparent; }
.hero .lead { font-size: clamp(16px, 1.6vw, 19px); color: rgba(255,255,255,.78); max-width: 640px; margin-bottom: 36px; }
.hero .ctas { display: flex; gap: 12px; flex-wrap: wrap; }

/* Buttons */
.btn { display: inline-flex; align-items: center; justify-content: center; gap: 8px; padding: 14px 26px; border-radius: var(--radius-sm); font-weight: 600; font-size: 15px; transition: all var(--transition); border: 1px solid transparent; cursor: pointer; }
.btn-primary { background: var(--brand); color: #fff !important; box-shadow: 0 8px 24px -8px rgba(230,0,38,.65); }
.btn-primary:hover { background: var(--brand-dark); transform: translateY(-1px); box-shadow: 0 12px 28px -10px rgba(230,0,38,.75); }
.btn-ghost { background: rgba(255,255,255,.10); color: #fff !important; border-color: rgba(255,255,255,.20); backdrop-filter: blur(8px); }
.btn-ghost:hover { background: rgba(255,255,255,.18); }
.btn-dark { background: var(--ink); color: #fff !important; }
.btn-dark:hover { background: var(--brand); }

/* Hero stats */
.hero-stats { display: grid; grid-template-columns: repeat(auto-fit, minmax(160px, 1fr)); gap: 32px; margin-top: 56px; padding-top: 36px; border-top: 1px solid rgba(255,255,255,.12); max-width: 720px; }
.hero-stats .stat .num { display: block; font-size: 32px; font-weight: 800; color: #fff; letter-spacing: -0.02em; line-height: 1; margin-bottom: 6px; }
.hero-stats .stat .lbl { font-size: 13px; color: rgba(255,255,255,.65); font-weight: 500; }

/* Sections */
section { padding: 96px 24px; }
.wrap { max-width: var(--max-w); margin: 0 auto; }
.wrap-narrow { max-width: var(--max-w-narrow); margin: 0 auto; }
.section-head { max-width: 720px; margin-bottom: 56px; }
.section-head.center { margin: 0 auto 56px; text-align: center; }
.section-eyebrow { display: inline-block; font-size: 13px; font-weight: 600; color: var(--brand); text-transform: uppercase; letter-spacing: 0.08em; margin-bottom: 14px; }
.section-head h2 { font-size: clamp(28px, 3.5vw, 44px); line-height: 1.1; letter-spacing: -0.025em; font-weight: 800; color: var(--ink); }
.section-head p { font-size: 18px; color: var(--gray-700); margin-top: 18px; line-height: 1.55; }
section.alt { background: var(--bg-soft); border-top: 1px solid var(--gray-100); border-bottom: 1px solid var(--gray-100); }
section.dark { background: var(--ink); color: #fff; }
section.dark .section-head h2 { color: #fff; }
section.dark .section-head p { color: rgba(255,255,255,.7); }
section.dark .section-eyebrow { color: #FF3650; }

/* Logos */
.logos-row { display: grid; grid-template-columns: repeat(auto-fit, minmax(120px, 1fr)); gap: 32px; align-items: center; opacity: .55; }
.logos-row .logo-mark { display: flex; align-items: center; justify-content: center; height: 36px; color: var(--gray-500); font-weight: 700; font-size: 17px; letter-spacing: -0.02em; }

/* Valores */
.values-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 24px; }
.value { padding: 28px; background: #fff; border: 1px solid var(--gray-200); border-radius: var(--radius-lg); transition: all var(--transition); }
.value:hover { border-color: var(--gray-300); box-shadow: var(--shadow-md); transform: translateY(-2px); }
.value .icon { width: 44px; height: 44px; display: flex; align-items: center; justify-content: center; background: var(--brand-soft); color: var(--brand); border-radius: 10px; margin-bottom: 18px; font-size: 22px; }
.value h3 { font-size: 18px; font-weight: 700; letter-spacing: -0.01em; margin-bottom: 8px; color: var(--ink); }
.value p { font-size: 15px; color: var(--gray-700); line-height: 1.55; }

/* Plan cards */
.planes-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(260px, 1fr)); gap: 20px; align-items: stretch; }
.plan-card { position: relative; background: #fff; border: 1px solid var(--gray-200); border-radius: var(--radius-lg); padding: 32px 28px; transition: all var(--transition); display: flex; flex-direction: column; }
.plan-card:hover { border-color: var(--gray-300); box-shadow: var(--shadow-lg); transform: translateY(-3px); }
.plan-card.destacado, .plan-card.destacado-custom { border-color: var(--ink); background: var(--ink); color: #fff; box-shadow: var(--shadow-xl); }
.plan-card.destacado h3, .plan-card.destacado-custom h3 { color: #fff; }
.plan-card.destacado .precio, .plan-card.destacado-custom .precio { color: #fff; }
.plan-card.destacado .precio small, .plan-card.destacado-custom .precio small { color: rgba(255,255,255,.6); }
.plan-card.destacado ul li, .plan-card.destacado-custom ul li { color: rgba(255,255,255,.85); border-color: rgba(255,255,255,.10); }
.plan-card.destacado ul li::before, .plan-card.destacado-custom ul li::before { background: rgba(230,0,38,.20); color: #FF3650; }
.plan-card.destacado .btn-plan, .plan-card.destacado-custom .btn-plan { background: var(--brand); }
.plan-card.destacado .btn-plan:hover, .plan-card.destacado-custom .btn-plan:hover { background: var(--brand-dark); }

.plan-badge { position: absolute; top: -12px; left: 50%; transform: translateX(-50%); background: var(--brand); color: #fff; font-size: 11px; font-weight: 700; padding: 6px 14px; border-radius: 100px; letter-spacing: 0.04em; box-shadow: 0 4px 12px -2px rgba(230,0,38,.5); white-space: nowrap; }
.plan-card h3 { font-size: 17px; font-weight: 700; letter-spacing: -0.01em; color: var(--ink); margin-bottom: 16px; }
.plan-card .precio { font-size: 44px; font-weight: 800; color: var(--ink); letter-spacing: -0.03em; line-height: 1; margin: 4px 0 18px; display: flex; align-items: baseline; gap: 6px; flex-wrap: wrap; }
.plan-card .precio small { font-size: 14px; font-weight: 500; color: var(--gray-500); }
.plan-card .precio-anterior { font-size: 18px; color: var(--gray-400); font-weight: 500; text-decoration: line-through; text-decoration-color: var(--brand); margin-right: 4px; }
.plan-card ul { list-style: none; margin: 0 0 24px; padding: 0; flex: 1; }
.plan-card ul li { position: relative; padding: 10px 0 10px 28px; font-size: 14.5px; color: var(--gray-700); border-top: 1px solid var(--gray-100); }
.plan-card ul li:first-child { border-top: 0; }
.plan-card ul li::before { content: "✓"; position: absolute; left: 0; top: 11px; width: 18px; height: 18px; background: var(--brand-soft); color: var(--brand); border-radius: 50%; display: inline-flex; align-items: center; justify-content: center; font-size: 11px; font-weight: 800; }
.btn-plan { display: block; text-align: center; background: var(--ink); color: #fff !important; padding: 13px 18px; border-radius: var(--radius-sm); font-weight: 600; font-size: 14.5px; transition: all var(--transition); }
.btn-plan:hover { background: var(--brand); transform: translateY(-1px); }

/* Ciudades cards */
.ciudades-grid { display: grid; grid-template-columns: repeat(auto-fit, minmax(220px, 1fr)); gap: 14px; }
.ciudad-card-link { display: block; }
.ciudad-card { background: #fff; padding: 22px; border: 1px solid var(--gray-200); border-radius: var(--radius-md); transition: all var(--transition); position: relative; overflow: hidden; }
.ciudad-card::before { content: ""; position: absolute; left: 0; top: 0; bottom: 0; width: 3px; background: var(--brand); transform: scaleY(0); transform-origin: bottom; transition: transform var(--transition); }
.ciudad-card:hover { border-color: var(--gray-300); box-shadow: var(--shadow-md); transform: translateY(-2px); }
.ciudad-card:hover::before { transform: scaleY(1); transform-origin: top; }
.ciudad-card h3 { font-size: 16px; font-weight: 700; letter-spacing: -0.01em; color: var(--ink); margin-bottom: 4px; }
.ciudad-card .meta { font-size: 13px; color: var(--gray-500); }

/* Comparativo */
.compare-wrap { background: #fff; border: 1px solid var(--gray-200); border-radius: var(--radius-lg); overflow: hidden; box-shadow: var(--shadow-md); }
.compare { width: 100%; border-collapse: collapse; font-size: 15px; }
.compare th, .compare td { padding: 18px 20px; text-align: left; border-bottom: 1px solid var(--gray-100); }
.compare th { background: var(--gray-50); font-weight: 600; color: var(--gray-700); font-size: 12.5px; text-transform: uppercase; letter-spacing: .04em; }
.compare th:nth-child(2) { color: var(--brand); }
.compare td:nth-child(1) { font-weight: 500; color: var(--ink); }
.compare td:nth-child(2) { font-weight: 600; color: var(--ink); }
.compare td:nth-child(3) { color: var(--gray-500); }
.compare tr:last-child td { border-bottom: 0; }
.compare .yes { color: var(--success); font-weight: 700; }
.compare .no { color: var(--gray-400); }

/* Testimonios */
.testimonials { display: grid; grid-template-columns: repeat(auto-fit, minmax(280px, 1fr)); gap: 24px; }
.testimonial { padding: 32px; background: #fff; border: 1px solid var(--gray-200); border-radius: var(--radius-lg); }
.testimonial .stars { color: #F59E0B; font-size: 14px; letter-spacing: 2px; margin-bottom: 14px; }
.testimonial blockquote { font-size: 16px; line-height: 1.6; color: var(--ink-2); margin-bottom: 22px; font-weight: 500; }
.testimonial .author { display: flex; align-items: center; gap: 12px; }
.testimonial .avatar { width: 42px; height: 42px; border-radius: 50%; background: linear-gradient(135deg, var(--brand) 0%, var(--brand-dark) 100%); color: #fff; display: flex; align-items: center; justify-content: center; font-weight: 700; font-size: 16px; }
.testimonial .author-info strong { display: block; font-size: 14.5px; color: var(--ink); font-weight: 600; }
.testimonial .author-info span { font-size: 13px; color: var(--gray-500); }

/* FAQ */
.faq { max-width: 820px; margin: 0 auto; }
.faq details { background: #fff; border: 1px solid var(--gray-200); border-radius: var(--radius-md); padding: 0; margin-bottom: 12px; transition: all var(--transition); }
.faq details[open] { border-color: var(--gray-300); box-shadow: var(--shadow-sm); }
.faq summary { list-style: none; cursor: pointer; padding: 20px 24px; font-weight: 600; font-size: 16px; color: var(--ink); display: flex; justify-content: space-between; align-items: center; }
.faq summary::-webkit-details-marker { display: none; }
.faq summary::after { content: "+"; font-size: 22px; color: var(--gray-400); font-weight: 400; transition: transform var(--transition); }
.faq details[open] summary::after { content: "−"; color: var(--brand); }
.faq details[open] summary { color: var(--brand); }
.faq details p { padding: 0 24px 22px; color: var(--gray-700); font-size: 15px; line-height: 1.6; }

/* CTA banda */
.cta-band { position: relative; isolation: isolate; padding: 80px 24px; color: #fff; overflow: hidden; background: var(--ink); }
.cta-band::before { content: ""; position: absolute; inset: 0; z-index: -1; opacity: .4; background: radial-gradient(50% 60% at 100% 50%, rgba(230,0,38,.45), transparent 60%), radial-gradient(40% 70% at 0% 100%, rgba(230,0,38,.30), transparent 60%); }
.cta-band .wrap { display: flex; align-items: center; justify-content: space-between; gap: 40px; flex-wrap: wrap; }
.cta-band h2 { font-size: clamp(26px, 3vw, 38px); line-height: 1.1; letter-spacing: -0.025em; font-weight: 800; max-width: 600px; }
.cta-band p { color: rgba(255,255,255,.75); margin-top: 10px; font-size: 16px; }
.cta-band .btns { display: flex; gap: 12px; flex-wrap: wrap; }

/* Sectores chips */
.chips { display: flex; flex-wrap: wrap; gap: 8px; }
.chip { background: #fff; border: 1px solid var(--gray-200); padding: 6px 14px; border-radius: 100px; font-size: 13px; color: var(--gray-700); font-weight: 500; }

/* Footer */
footer.site { background: var(--ink); color: rgba(255,255,255,.7); padding: 72px 24px 28px; }
footer.site .wrap { max-width: var(--max-w); margin: 0 auto; }
footer.site .cols { display: grid; grid-template-columns: 2fr 1fr 1fr 1fr; gap: 48px; padding-bottom: 48px; border-bottom: 1px solid rgba(255,255,255,.10); }
footer.site .brand-col h4 { color: #fff; font-size: 22px; font-weight: 800; letter-spacing: -0.02em; margin-bottom: 12px; display: flex; align-items: center; gap: 8px; }
footer.site .brand-col h4::before { content: ""; width: 10px; height: 10px; background: var(--brand); border-radius: 50%; }
footer.site .brand-col p { font-size: 14.5px; color: rgba(255,255,255,.6); margin-bottom: 16px; line-height: 1.6; max-width: 360px; }
footer.site .brand-col .meta { font-size: 13px; color: rgba(255,255,255,.45); margin-bottom: 4px; }
footer.site h5 { color: #fff; font-size: 13px; font-weight: 600; text-transform: uppercase; letter-spacing: 0.06em; margin-bottom: 16px; }
footer.site a { color: rgba(255,255,255,.65); display: block; padding: 4px 0; font-size: 14.5px; transition: color var(--transition); }
footer.site a:hover { color: #fff; }
footer.site .legal { margin-top: 28px; font-size: 13px; color: rgba(255,255,255,.4); text-align: center; }

/* WhatsApp float */
.wa-float { position: fixed; bottom: 24px; right: 24px; width: 60px; height: 60px; border-radius: 50%; background: #25D366; color: #fff; display: flex; align-items: center; justify-content: center; font-size: 28px; box-shadow: 0 12px 28px rgba(37,211,102,.45), 0 4px 12px rgba(0,0,0,.15); z-index: 200; transition: all var(--transition); }
.wa-float:hover { transform: scale(1.08); color: #fff; }
.wa-float::before { content: ""; position: absolute; inset: -4px; border-radius: 50%; background: rgba(37,211,102,.35); animation: pulse 2s ease-out infinite; z-index: -1; }
@keyframes pulse { 0% { transform: scale(.8); opacity: .8; } 100% { transform: scale(1.4); opacity: 0; } }

/* Responsive */
@media (max-width: 900px) { footer.site .cols { grid-template-columns: 1fr 1fr; gap: 36px; } }
@media (max-width: 720px) {
  section { padding: 64px 20px; }
  .hero { padding: 80px 20px 60px; }
  .hero-stats { gap: 24px; margin-top: 40px; padding-top: 28px; }
  header.site nav { display: none; }
  .compare th, .compare td { padding: 12px 14px; font-size: 13.5px; }
  footer.site .cols { grid-template-columns: 1fr; gap: 32px; }
  footer.site { padding: 48px 20px 24px; }
}
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
    <a href="{base}index.html" class="logo"><span class="dot"></span>{html.escape(cfg["empresa"]["nombre_comercial"])}</a>
    <nav>
      <a href="{base}index.html#planes">Planes</a>
      <a href="{base}index.html#empresas">Empresas</a>
      <a href="{base}index.html#cobertura">Cobertura</a>
      <a href="{base}index.html#faq">FAQ</a>
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
  <div class="precio">{precio_anterior_html}${p['precio_usd']:.2f}<small>/mes</small></div>
  <ul>{items_html}</ul>
  <a class="btn-plan" href="{wa}">Contratar por WhatsApp</a>
</div>""")
    return f'<div class="planes-grid">{"".join(cards)}</div>'


def render_logos_row() -> str:
    """Logos placeholder de marcas / servicios incluidos (en gris)."""
    marcas = ["Claro", "HBO Max", "Amazon Prime", "Disney+", "Claro Video", "ECDF"]
    items = "".join(f'<div class="logo-mark">{html.escape(m)}</div>' for m in marcas)
    return f'<div class="logos-row">{items}</div>'


def render_valores() -> str:
    valores = [
        ("🛡️", "Distribuidor autorizado", "Operamos con respaldo oficial de Claro Ecuador desde 2015. Servicios, equipos y facturación 100% Claro."),
        ("⚡", "Instalación rápida", "De 24 a 120 horas en las principales ciudades del país. Coordinamos visita técnica y activación sin que muevas un dedo."),
        ("📍", "Cobertura nacional", "Atendemos 15 ciudades de Ecuador con asesores locales. La red Claro cubre el 97% de la población."),
        ("💬", "Soporte humano", "Atención por WhatsApp, teléfono y oficina en Quito. Resolvemos dudas antes, durante y después de contratar."),
        ("💰", "Precio para siempre", "Sin alzas tras los primeros meses. La tarifa que contratas es la que pagas mientras dure tu plan."),
        ("🎁", "Beneficios incluidos", "HBO Max, Amazon Prime, Claro Video y telefonía fija ilimitada vienen incluidos según tu plan."),
    ]
    items = "".join(
        f'<div class="value"><div class="icon">{i}</div><h3>{html.escape(t)}</h3><p>{html.escape(d)}</p></div>'
        for i, t, d in valores
    )
    return f'<div class="values-grid">{items}</div>'


def render_pymes(cfg: dict) -> str:
    """Bloque de planes empresariales / negocios — extraído de la guía comercial."""
    wa_base = cfg["empresa"]["whatsapp_e164"]
    planes = [
        ("Plan Negocios 25 Plus", 40, "Ilimitados + 100 LDI", 28.75,
         ["40 GB de datos móviles", "Minutos ilimitados multidestino + 100 min LDI", "500 SMS", "Redes sociales ilimitadas (PUJ 5 GB c/app)", "WhatsApp ilimitado en roaming"]),
        ("Plan Negocios 35 Plus", 60, "Ilimitados + 150 LDI", 40.25,
         ["60 GB de datos móviles", "Minutos ilimitados multidestino + 150 min LDI", "500 SMS", "Redes sociales ilimitadas (PUJ 10 GB c/app)", "WhatsApp ilimitado en roaming"]),
        ("Plan Negocios 50 Plus", 90, "Ilimitados + 200 LDI", 57.50,
         ["90 GB de datos móviles", "Minutos ilimitados multidestino + 200 min LDI", "500 SMS", "Redes sociales ilimitadas (PUJ 15 GB c/app)", "WhatsApp ilimitado en roaming", "Roaming con navegación libre"]),
    ]
    cards = []
    for nombre, gb, mins, precio, beneficios in planes:
        items = "".join(f"<li>{html.escape(b)}</li>" for b in beneficios)
        wa = wa_link(wa_base, f"Hola SHENCOM, deseo información del {nombre} para mi empresa.")
        destacado = ' destacado' if "35 Plus" in nombre else ''
        badge = '<span class="plan-badge">RECOMENDADO PYME</span>' if "35 Plus" in nombre else ''
        cards.append(f"""<div class="plan-card{destacado}">
  {badge}
  <h3>{html.escape(nombre)}</h3>
  <div class="precio">${precio:.2f}<small>/mes</small></div>
  <ul>{items}</ul>
  <a class="btn-plan" href="{wa}">Cotizar para mi empresa</a>
</div>""")
    return f'<div class="planes-grid">{"".join(cards)}</div>'


def render_comparativo() -> str:
    filas = [
        ("Velocidad simétrica fibra óptica", "Hasta 1 Gbps", "Variable, asimétrica"),
        ("Telefonía fija ilimitada", "✓ Incluida", "Costo extra mensual"),
        ("TV Streaming 91 canales", "✓ Desde 3 Play", "Servicio aparte"),
        ("HBO Max + Amazon Prime", "✓ Permanente", "Solo promo temporal"),
        ("Precio garantizado para siempre", "✓ Sin alzas", "Sube tras 6 meses"),
        ("Cobertura nacional", "97% del Ecuador", "Limitada a ciudades"),
        ("Soporte 24/7 con atención local", "✓ SHENCOM", "Call center genérico"),
        ("Instalación gratis", "✓ 100% incluida", "Costo de $30–80"),
    ]
    rows = "".join(
        f'<tr><td>{html.escape(b)}</td><td><span class="yes">{html.escape(c)}</span></td><td><span class="no">{html.escape(o)}</span></td></tr>'
        for b, c, o in filas
    )
    return f"""<div class="compare-wrap">
  <table class="compare">
    <thead><tr><th>Beneficio</th><th>Claro · SHENCOM</th><th>Competencia típica</th></tr></thead>
    <tbody>{rows}</tbody>
  </table>
</div>"""


def render_testimonios() -> str:
    items = [
        ("MR", "Mariana R.", "Cliente residencial · Quito", 5,
         "La instalación llegó al día siguiente. El asesor me explicó todo, el WiFi llega hasta el patio y nunca he tenido cortes. Me cambié desde otra operadora y la diferencia es enorme."),
        ("DG", "Diego G.", "Gerente PYME · Guayaquil", 5,
         "Necesitábamos 12 líneas pospago para el equipo de ventas. SHENCOM nos hizo la migración en menos de una semana y consolidó todo en una sola factura. Servicio impecable."),
        ("LV", "Luisa V.", "Emprendedora · Cuenca", 5,
         "Llevaba años con la competencia y siempre subían el precio. Aquí me garantizaron la tarifa para siempre. Además HBO Max viene incluido — eso solo ya cubre lo que pago de más."),
    ]
    cards = "".join(
        f'<div class="testimonial">'
        f'<div class="stars">{"★" * stars}</div>'
        f'<blockquote>"{html.escape(quote)}"</blockquote>'
        f'<div class="author"><div class="avatar">{html.escape(initials)}</div>'
        f'<div class="author-info"><strong>{html.escape(nombre)}</strong><span>{html.escape(rol)}</span></div></div>'
        f'</div>'
        for initials, nombre, rol, stars, quote in items
    )
    return f'<div class="testimonials">{cards}</div>'


def render_cta_band(cfg: dict) -> str:
    wa = wa_link(cfg["empresa"]["whatsapp_e164"])
    tel = fmt_phone_link(cfg["empresa"]["telefono_principal"])
    return f"""<section class="cta-band">
  <div class="wrap">
    <div>
      <h2>¿Listo para conectarte con Claro?</h2>
      <p>Te damos la mejor cobertura, precio garantizado y atención local. Hablemos hoy.</p>
    </div>
    <div class="btns">
      <a class="btn btn-primary" href="{wa}">💬 WhatsApp directo</a>
      <a class="btn btn-ghost" href="tel:{tel}">📞 {html.escape(cfg['empresa']['telefono_principal'])}</a>
    </div>
  </div>
</section>"""


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
      <div class="brand-col">
        <h4>{html.escape(emp["nombre_comercial"])}</h4>
        <p>{html.escape(emp["tagline"])}</p>
        <p class="meta">RUC: {html.escape(emp["ruc"])}</p>
        <p class="meta">{html.escape(emp["direccion_matriz"])}</p>
      </div>
      <div>
        <h5>Contacto</h5>
        <a href="tel:{fmt_phone_link(emp['telefono_principal'])}">{html.escape(emp['telefono_principal'])}</a>
        <a href="{wa_link(emp['whatsapp_e164'])}">WhatsApp directo</a>
        <a href="mailto:{html.escape(emp['email_ventas'])}">{html.escape(emp['email_ventas'])}</a>
        <p class="meta" style="margin-top:12px">{html.escape(emp['horario_atencion'])}</p>
      </div>
      <div>
        <h5>Cobertura</h5>
        {ciudades_links}
      </div>
      <div>
        <h5>Recursos</h5>
        <a href="{base}#planes">Planes Hogar</a>
        <a href="{base}#movil">Planes Móvil</a>
        <a href="{base}#empresas">Para empresas</a>
        <a href="{base}#faq">Preguntas frecuentes</a>
        {('<div class="social-row" style="margin-top:14px;display:flex;gap:10px;flex-wrap:wrap">' + redes_html + '</div>') if redes_html else ''}
      </div>
    </div>
    <div class="legal">
      © {year} {html.escape(emp["nombre_comercial"])} · Distribuidor Autorizado de Claro Ecuador · Razón social: {html.escape(emp["razon_social"])} · Todos los derechos reservados.
    </div>
  </div>
</footer>
<a class="wa-float" href="{wa_link(emp['whatsapp_e164'])}" aria-label="Chatear por WhatsApp">
  <svg viewBox="0 0 24 24" width="28" height="28" fill="currentColor" aria-hidden="true"><path d="M20.52 3.48A11.94 11.94 0 0 0 12 0C5.37 0 .04 5.33.04 11.95c0 2.11.55 4.16 1.6 5.97L0 24l6.24-1.63a11.96 11.96 0 0 0 5.76 1.47h.01c6.62 0 11.95-5.33 11.95-11.95 0-3.19-1.24-6.19-3.44-8.41Zm-8.52 18.4h-.01a9.93 9.93 0 0 1-5.06-1.39l-.36-.21-3.7.97.99-3.61-.24-.37a9.92 9.92 0 0 1-1.52-5.32c0-5.49 4.47-9.96 9.96-9.96 2.66 0 5.16 1.04 7.04 2.92a9.9 9.9 0 0 1 2.92 7.04c0 5.5-4.47 9.93-9.92 9.93Zm5.45-7.42c-.3-.15-1.77-.87-2.04-.97-.27-.1-.47-.15-.66.15-.2.3-.76.97-.93 1.17-.17.2-.34.22-.64.07-.3-.15-1.27-.47-2.42-1.49-.9-.8-1.5-1.79-1.67-2.09-.17-.3-.02-.46.13-.61.13-.13.3-.34.45-.51.15-.17.2-.3.3-.5.1-.2.05-.37-.02-.52-.07-.15-.66-1.6-.91-2.19-.24-.58-.49-.5-.66-.51l-.57-.01c-.2 0-.52.07-.79.37-.27.3-1.04 1.02-1.04 2.48s1.07 2.88 1.22 3.07c.15.2 2.1 3.2 5.08 4.49.71.31 1.27.49 1.7.63.71.23 1.36.2 1.87.12.57-.08 1.77-.72 2.02-1.42.25-.7.25-1.3.17-1.42-.07-.13-.27-.2-.57-.35Z"/></svg>
</a>"""


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
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700;800;900&display=swap" rel="stylesheet">
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
    logos = render_logos_row()
    valores = render_valores()
    pymes = render_pymes(cfg)
    comparativo = render_comparativo()
    testimonios = render_testimonios()
    cta_band = render_cta_band(cfg)
    footer = render_footer(cfg)
    wa = wa_link(cfg["empresa"]["whatsapp_e164"])

    return f"""{head}
{banner}
{header}
<section class="hero">
  <div class="wrap">
    <div class="eyebrow"><span class="pulse"></span> Distribuidor Autorizado · Claro Ecuador</div>
    <h1>Internet, móvil y TV de <span class="accent">Claro Ecuador</span> con instalación profesional.</h1>
    <p class="lead">Planes hogar desde $23, pospago móvil desde $16 y atención local en {len(CIUDADES)} ciudades. Precio garantizado, cobertura nacional y respaldo oficial Claro.</p>
    <div class="ctas">
      <a class="btn btn-primary" href="{wa}">💬 Contratar por WhatsApp</a>
      <a class="btn btn-ghost" href="#planes">Ver planes y precios</a>
    </div>
    <div class="hero-stats">
      <div class="stat"><span class="num">+10</span><span class="lbl">años distribuidor Claro</span></div>
      <div class="stat"><span class="num">{len(CIUDADES)}</span><span class="lbl">ciudades con cobertura</span></div>
      <div class="stat"><span class="num">97%</span><span class="lbl">del Ecuador con red Claro</span></div>
      <div class="stat"><span class="num">24h</span><span class="lbl">tiempo promedio instalación</span></div>
    </div>
  </div>
</section>

<section class="section alt" aria-label="Servicios incluidos">
  <div class="wrap">
    {logos}
  </div>
</section>

<section class="section" id="por-que">
  <div class="wrap">
    <div class="section-head center">
      <span class="section-eyebrow">Por qué SHENCOM</span>
      <h2>Lo que hace diferente contratar Claro con nosotros</h2>
      <p>Somos distribuidor autorizado oficial. Los servicios, equipos y facturación son 100% Claro — lo que sumamos es asesoría humana, instalación coordinada y soporte sin call center.</p>
    </div>
    {valores}
  </div>
</section>

<section class="section alt" id="planes">
  <div class="wrap">
    <div class="section-head">
      <span class="section-eyebrow">Internet Hogar</span>
      <h2>Fibra óptica simétrica con TV, telefonía y streaming</h2>
      <p>Cuatro planes Claro Hogar con velocidades reales de 300 Mbps a 1 Gbps. Instalación 100% gratis, router WiFi incluido y precio garantizado mientras dure tu plan.</p>
    </div>
    {planes_internet}
  </div>
</section>

<section class="section" id="movil">
  <div class="wrap">
    <div class="section-head">
      <span class="section-eyebrow">Pospago Móvil</span>
      <h2>Planes Plus Max con redes y WhatsApp ilimitados</h2>
      <p>Minutos multidestino, gigas para todo y suscripciones premium incluidas. Portabilidad gratuita conservando tu número actual en menos de 24 horas.</p>
    </div>
    {planes_movil}
  </div>
</section>

<section class="section alt" id="empresas">
  <div class="wrap">
    <div class="section-head">
      <span class="section-eyebrow">Para tu empresa</span>
      <h2>Planes Negocios PYME con consolidación de cuentas</h2>
      <p>Convergencia móvil + internet, una sola factura, asesor dedicado y migración acompañada para equipos de cualquier tamaño.</p>
    </div>
    {pymes}
  </div>
</section>

<section class="section" id="cobertura">
  <div class="wrap">
    <div class="section-head">
      <span class="section-eyebrow">Cobertura</span>
      <h2>Atendemos {len(CIUDADES)} ciudades del Ecuador</h2>
      <p>Selecciona tu ciudad para ver sectores con cobertura, tiempos de instalación y contacto local.</p>
    </div>
    <div class="ciudades-grid">{ciudades_html}</div>
  </div>
</section>

<section class="section alt" aria-label="Comparativo">
  <div class="wrap">
    <div class="section-head center">
      <span class="section-eyebrow">Comparativo</span>
      <h2>Claro con SHENCOM vs. la competencia</h2>
      <p>Una mirada honesta a lo que recibes contratando con un distribuidor autorizado Claro frente a una operadora típica.</p>
    </div>
    {comparativo}
  </div>
</section>

<section class="section" aria-label="Testimonios">
  <div class="wrap">
    <div class="section-head center">
      <span class="section-eyebrow">Clientes reales</span>
      <h2>Lo que dicen quienes ya se cambiaron</h2>
    </div>
    {testimonios}
  </div>
</section>

<section class="section alt" id="faq">
  <div class="wrap">
    <div class="section-head center">
      <span class="section-eyebrow">FAQ</span>
      <h2>Preguntas frecuentes</h2>
      <p>Lo que más nos preguntan antes de contratar. Si no encuentras tu duda, escríbenos por WhatsApp.</p>
    </div>
    <div class="faq">
      <details><summary>¿SHENCOM es Claro?</summary><p>SHENCOM es <strong>distribuidor autorizado oficial</strong> de Claro Ecuador. Los planes, equipos y facturación son 100% Claro. Lo que sumamos es asesoría humana, gestión de instalación y soporte cercano.</p></details>
      <details><summary>¿Cuánto tarda la instalación de internet hogar?</summary><p>Entre 24 y 120 horas hábiles dependiendo de la ciudad y verificación de cobertura. En Quito y Guayaquil suele ser al día siguiente. Revisa la página de tu ciudad para detalles.</p></details>
      <details><summary>¿Qué documentos necesito para contratar?</summary><p>Cédula de identidad vigente del titular y comprobante de domicilio (planilla de luz, agua o teléfono no mayor a 3 meses). Para empresas: RUC y nombramiento del representante legal.</p></details>
      <details><summary>¿Hacen portabilidad de número desde otra operadora?</summary><p>Sí, la portabilidad es gratuita. Conservas tu número actual y la activación se completa en menos de 24 horas hábiles. Nosotros gestionamos todo el trámite.</p></details>
      <details><summary>¿El precio sube después de unos meses?</summary><p>No. Lo que contratas es lo que pagas mientras dure tu plan. No tenemos esquemas promocionales que se disparan a los 6 meses como otras operadoras.</p></details>
      <details><summary>¿Tienen planes para empresas?</summary><p>Sí. Manejamos los Planes Negocios Plus de Claro con consolidación en una sola factura, asesor dedicado, migración acompañada y descuentos por volumen. Mira la sección <a href="#empresas">Para tu empresa</a>.</p></details>
      <details><summary>¿Qué incluye la instalación gratis?</summary><p>Visita técnica, cableado interno hasta el punto que elijas, configuración del router WiFi y pruebas de velocidad. No hay costos ocultos: la instalación es 100% gratuita en todos los planes hogar.</p></details>
    </div>
  </div>
</section>

{cta_band}

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
    planes_movil = render_planes_grid(cfg, "pospago_movil")
    valores = render_valores()
    comparativo = render_comparativo()
    cta_band = render_cta_band(cfg)

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
        vecinas_html = f"""<section class="section alt" aria-label="Ciudades cercanas">
  <div class="wrap">
    <div class="section-head">
      <span class="section-eyebrow">Cobertura cercana</span>
      <h2>También cubrimos cerca de {html.escape(ciudad['nombre'])}</h2>
    </div>
    <div class="ciudades-grid">{vecinas_links}</div>
  </div>
</section>"""

    footer = render_footer(cfg, is_subpage=True)

    return f"""{head}
{banner}
{header}
<section class="hero">
  <div class="wrap">
    <div class="eyebrow"><span class="pulse"></span> Cobertura activa · {html.escape(ciudad['provincia'])}</div>
    <h1>Planes Claro en <span class="accent">{html.escape(ciudad['nombre'])}</span> con instalación profesional.</h1>
    <p class="lead">Distribuidor autorizado de Claro Ecuador en {html.escape(ciudad['nombre'])}. Internet hogar de fibra óptica, pospago móvil y atención local en {html.escape(ciudad['tiempo_instalacion'])}.</p>
    <div class="ctas">
      <a class="btn btn-primary" href="{wa}">💬 Cotizar por WhatsApp</a>
      <a class="btn btn-ghost" href="tel:{fmt_phone_link(tel_zonal)}">📞 {html.escape(tel_zonal)}</a>
    </div>
    <div class="hero-stats">
      <div class="stat"><span class="num">{ciudad['poblacion_aprox']:,}</span><span class="lbl">habitantes en {html.escape(ciudad['nombre'])}</span></div>
      <div class="stat"><span class="num">{len(ciudad['sectores'])}+</span><span class="lbl">sectores con cobertura</span></div>
      <div class="stat"><span class="num">{html.escape(ciudad['tiempo_instalacion'].split('-')[0].strip() if '-' in ciudad['tiempo_instalacion'] else ciudad['tiempo_instalacion'])}</span><span class="lbl">tiempo de instalación</span></div>
    </div>
  </div>
</section>

<section class="section">
  <div class="wrap">
    <div class="section-head">
      <span class="section-eyebrow">Servicios disponibles</span>
      <h2>Claro en {html.escape(ciudad['nombre'])}: lo que puedes contratar hoy</h2>
      <p>{html.escape(ciudad['paragraph_intro'])}</p>
    </div>
    <div class="info-grid" style="display:grid;grid-template-columns:repeat(auto-fit,minmax(260px,1fr));gap:24px;">
      <div class="value"><div class="icon">📍</div><h3>Cobertura</h3><p>{html.escape(ciudad['cobertura_nota'])}</p></div>
      <div class="value"><div class="icon">⚡</div><h3>Tiempo de instalación</h3><p>Entre {html.escape(ciudad['tiempo_instalacion'])} desde la confirmación del contrato y la verificación de cobertura en tu dirección.</p></div>
      <div class="value"><div class="icon">📞</div><h3>Atención local</h3><p>Asesor zonal en {html.escape(ciudad['nombre'])}: {html.escape(tel_zonal)}. También por WhatsApp con respuesta el mismo día hábil.</p></div>
    </div>
  </div>
</section>

<section class="section alt" aria-label="Sectores con cobertura">
  <div class="wrap">
    <div class="section-head">
      <span class="section-eyebrow">Sectores</span>
      <h2>Zonas de {html.escape(ciudad['nombre'])} con cobertura Claro</h2>
      <p>SHENCOM gestiona instalaciones en estos sectores. Si tu zona no aparece, escríbenos por WhatsApp y validamos disponibilidad puntual en tu dirección.</p>
    </div>
    <div class="chips">{sectores_chips}</div>
  </div>
</section>

<section class="section" id="planes">
  <div class="wrap">
    <div class="section-head">
      <span class="section-eyebrow">Internet Hogar</span>
      <h2>Planes Claro Hogar para {html.escape(ciudad['nombre'])}</h2>
      <p>Fibra óptica simétrica donde haya cobertura. Todos los planes incluyen instalación gratuita, router WiFi y soporte técnico 24/7.</p>
    </div>
    {planes_internet}
  </div>
</section>

<section class="section alt" id="movil">
  <div class="wrap">
    <div class="section-head">
      <span class="section-eyebrow">Pospago Móvil</span>
      <h2>Planes móviles Claro disponibles en {html.escape(ciudad['nombre'])}</h2>
      <p>Minutos multidestino, gigas para todo y portabilidad gratuita conservando tu número.</p>
    </div>
    {planes_movil}
  </div>
</section>

<section class="section" aria-label="Por qué SHENCOM">
  <div class="wrap">
    <div class="section-head center">
      <span class="section-eyebrow">Por qué SHENCOM</span>
      <h2>Razones para contratar Claro con un distribuidor autorizado</h2>
    </div>
    {valores}
  </div>
</section>

<section class="section alt" aria-label="Comparativo">
  <div class="wrap">
    <div class="section-head center">
      <span class="section-eyebrow">Comparativo</span>
      <h2>Claro · SHENCOM vs. otras operadoras en {html.escape(ciudad['nombre'])}</h2>
    </div>
    {comparativo}
  </div>
</section>

<section class="section" id="faq">
  <div class="wrap">
    <div class="section-head center">
      <span class="section-eyebrow">FAQ</span>
      <h2>Preguntas frecuentes — {html.escape(ciudad['nombre'])}</h2>
    </div>
    <div class="faq">
      <details><summary>¿Hay cobertura de fibra Claro en mi sector de {html.escape(ciudad['nombre'])}?</summary><p>Cubrimos los principales sectores: {html.escape(', '.join(ciudad['sectores'][:5]))} entre otros. Para verificar tu dirección exacta, contáctanos por WhatsApp y validamos en minutos.</p></details>
      <details><summary>¿Cuánto tarda la instalación en {html.escape(ciudad['nombre'])}?</summary><p>Entre {html.escape(ciudad['tiempo_instalacion'])} desde la confirmación del contrato y verificación de cobertura. Coordinamos visita técnica en horario laboral.</p></details>
      <details><summary>¿A qué número llamo para soporte local en {html.escape(ciudad['nombre'])}?</summary><p>Atención zonal directa en {html.escape(tel_zonal)}. También puedes escribirnos por WhatsApp para agilizar la respuesta.</p></details>
      <details><summary>¿Puedo migrar desde otra operadora a Claro en {html.escape(ciudad['nombre'])}?</summary><p>Sí, la portabilidad es gratuita, conservas tu número y SHENCOM gestiona todo el trámite por ti. La activación demora menos de 24 horas hábiles.</p></details>
      <details><summary>¿La instalación tiene algún costo en {html.escape(ciudad['nombre'])}?</summary><p>No. La instalación de los planes hogar es 100% gratuita: incluye visita técnica, cableado interno, configuración del router y pruebas de velocidad.</p></details>
    </div>
  </div>
</section>

{vecinas_html}

{cta_band}

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

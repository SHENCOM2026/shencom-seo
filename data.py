"""
data.py — Datasets fijos del sitio SEO de SHENCOM.

Aquí viven los datos que NO cambian frecuentemente (datos demográficos
de las ciudades, sectores cubiertos, etc.). Los datos editables por
el cliente (teléfonos, precios, RUC, etc.) están en config-shencom.json.

Para añadir/quitar ciudades: edita la lista CIUDADES más abajo.
Para cambiar teléfonos o precios: edita config-shencom.json.
"""

from __future__ import annotations

import json
from pathlib import Path
from typing import Optional, List

# ---------------------------------------------------------------------------
# Carga del JSON editable
# ---------------------------------------------------------------------------

CONFIG_PATH = Path(__file__).parent / "config-shencom.json"

def load_config() -> dict:
    """Lee config-shencom.json y lo retorna como dict."""
    with open(CONFIG_PATH, encoding="utf-8") as f:
        return json.load(f)


# ---------------------------------------------------------------------------
# Dataset de ciudades — contenido único por página (evita thin content)
# ---------------------------------------------------------------------------
# Cada ciudad aporta:
#   - provincia, poblacion_aprox: contexto demográfico
#   - sectores: barrios principales (mejora intención local + cobertura)
#   - paragraph_intro: párrafo único introductorio (2-3 oraciones)
#   - cobertura_nota: nota específica sobre cobertura Claro en esa ciudad
#   - tiempo_instalacion: SLA típico
#   - vecinas: ciudades cercanas para internal linking

CIUDADES = [
    {
        "slug": "quito",
        "nombre": "Quito",
        "provincia": "Pichincha",
        "poblacion_aprox": 2_780_000,
        "sectores": ["Norte", "Sur", "Centro Histórico", "La Carolina", "Cumbayá",
                     "Tumbaco", "Calderón", "Quitumbe", "Valle de los Chillos", "Pomasqui"],
        "paragraph_intro": (
            "Quito, capital de Ecuador y sede del Distrito Metropolitano, concentra la mayor "
            "demanda de servicios de telecomunicaciones del país. Como distribuidor autorizado de "
            "Claro, SHENCOM brinda atención presencial y técnica a hogares y empresas en los "
            "principales valles y sectores de la ciudad."
        ),
        "cobertura_nota": (
            "Cobertura de fibra óptica disponible en la mayoría de sectores residenciales "
            "del Norte, Sur y los valles. En zonas de cobertura limitada se ofrece tecnología HFC."
        ),
        "tiempo_instalacion": "24 a 72 horas hábiles",
        "vecinas": ["santo-domingo", "latacunga", "ibarra"],
    },
    {
        "slug": "guayaquil",
        "nombre": "Guayaquil",
        "provincia": "Guayas",
        "poblacion_aprox": 2_720_000,
        "sectores": ["Urdesa", "Samborondón", "Vía a la Costa", "Los Ceibos", "Kennedy",
                     "Sauces", "Alborada", "Guasmo", "Garzota", "Daule"],
        "paragraph_intro": (
            "Guayaquil es la ciudad más poblada y el principal puerto comercial de Ecuador. "
            "SHENCOM atiende a clientes residenciales, PYMEs y corporativos en toda la ciudad y "
            "sus zonas periféricas con planes Claro adaptados a la dinámica costera."
        ),
        "cobertura_nota": (
            "Amplia disponibilidad de fibra óptica simétrica en sectores residenciales y "
            "comerciales. Ideal para teletrabajo, gaming y streaming en alta resolución."
        ),
        "tiempo_instalacion": "24 a 72 horas hábiles",
        "vecinas": ["machala", "babahoyo", "quevedo"],
    },
    {
        "slug": "cuenca",
        "nombre": "Cuenca",
        "provincia": "Azuay",
        "poblacion_aprox": 636_000,
        "sectores": ["Centro Histórico", "El Vergel", "Totoracocha", "Ricaurte",
                     "Yanuncay", "Monay", "El Batán", "Misicata"],
        "paragraph_intro": (
            "Cuenca, Patrimonio Cultural de la Humanidad, combina historia y modernidad. La "
            "demanda de internet de alta velocidad ha crecido de la mano del trabajo remoto y la "
            "comunidad de expatriados. SHENCOM ofrece servicios Claro con cobertura en todo el cantón."
        ),
        "cobertura_nota": (
            "Cobertura de fibra óptica en la mayoría de parroquias urbanas. Se recomienda "
            "verificar disponibilidad por dirección exacta antes de contratar."
        ),
        "tiempo_instalacion": "48 a 96 horas hábiles",
        "vecinas": ["loja", "machala"],
    },
    {
        "slug": "santo-domingo",
        "nombre": "Santo Domingo",
        "provincia": "Santo Domingo de los Tsáchilas",
        "poblacion_aprox": 462_000,
        "sectores": ["Centro", "Río Verde", "Plan de Vivienda", "Los Rosales",
                     "Santa Martha", "Las Acacias", "Vía Quevedo"],
        "paragraph_intro": (
            "Santo Domingo es un nodo logístico clave entre la Sierra y la Costa. "
            "Su crecimiento comercial demanda conectividad estable para negocios y hogares. "
            "SHENCOM, como distribuidor autorizado de Claro, ofrece servicios con respaldo técnico local."
        ),
        "cobertura_nota": (
            "Cobertura mixta: fibra óptica en zonas urbanas consolidadas y soluciones "
            "inalámbricas en sectores periféricos."
        ),
        "tiempo_instalacion": "48 a 96 horas hábiles",
        "vecinas": ["quito", "quevedo", "esmeraldas"],
    },
    {
        "slug": "machala",
        "nombre": "Machala",
        "provincia": "El Oro",
        "poblacion_aprox": 280_000,
        "sectores": ["Puerto Bolívar", "Las Brisas", "La Aurora", "El Bosque",
                     "Unioro", "9 de Octubre"],
        "paragraph_intro": (
            "Machala, capital bananera del mundo, requiere conectividad robusta para su "
            "actividad agroexportadora y comercial. SHENCOM ofrece planes Claro para hogar y "
            "empresa con instalación en toda la zona urbana."
        ),
        "cobertura_nota": (
            "Cobertura de fibra óptica en el centro y sectores residenciales consolidados. "
            "Ideal para empresas con necesidades de subida estable."
        ),
        "tiempo_instalacion": "48 a 96 horas hábiles",
        "vecinas": ["guayaquil", "loja", "cuenca"],
    },
    {
        "slug": "manta",
        "nombre": "Manta",
        "provincia": "Manabí",
        "poblacion_aprox": 264_000,
        "sectores": ["Tarqui", "Los Esteros", "Umiña", "San Mateo", "Barrio Córdova",
                     "La Pradera", "El Palmar"],
        "paragraph_intro": (
            "Manta, principal puerto pesquero y polo turístico de la costa ecuatoriana, "
            "demanda servicios de telecomunicaciones de alta disponibilidad. SHENCOM atiende a "
            "clientes residenciales y a la creciente comunidad de nómadas digitales."
        ),
        "cobertura_nota": (
            "Cobertura de fibra óptica en sectores residenciales y turísticos. Disponibilidad "
            "específica varía por urbanización."
        ),
        "tiempo_instalacion": "48 a 96 horas hábiles",
        "vecinas": ["portoviejo", "esmeraldas"],
    },
    {
        "slug": "portoviejo",
        "nombre": "Portoviejo",
        "provincia": "Manabí",
        "poblacion_aprox": 240_000,
        "sectores": ["Picoazá", "Andrés de Vera", "Colón", "La Pradera",
                     "12 de Marzo", "El Florón"],
        "paragraph_intro": (
            "Portoviejo, capital provincial de Manabí, es un centro administrativo y "
            "universitario importante. SHENCOM ofrece planes Claro para estudiantes, hogares y "
            "PYMEs con atención técnica regional."
        ),
        "cobertura_nota": (
            "Cobertura ampliada tras la reconstrucción post-terremoto. Fibra óptica disponible "
            "en sectores residenciales principales."
        ),
        "tiempo_instalacion": "48 a 96 horas hábiles",
        "vecinas": ["manta", "santo-domingo"],
    },
    {
        "slug": "ambato",
        "nombre": "Ambato",
        "provincia": "Tungurahua",
        "poblacion_aprox": 180_000,
        "sectores": ["Ficoa", "Atocha", "Ingahurco", "Huachi Loreto",
                     "La Vicentina", "Miraflores"],
        "paragraph_intro": (
            "Ambato, conocida como la 'Ciudad de las Flores y las Frutas', es uno de los "
            "centros comerciales más dinámicos de la Sierra centro. SHENCOM atiende su densa red "
            "de comerciantes y hogares con planes Claro."
        ),
        "cobertura_nota": (
            "Cobertura de fibra óptica consolidada en parroquias urbanas. Soluciones para "
            "comercios pequeños con planes flexibles."
        ),
        "tiempo_instalacion": "48 a 96 horas hábiles",
        "vecinas": ["riobamba", "latacunga"],
    },
    {
        "slug": "riobamba",
        "nombre": "Riobamba",
        "provincia": "Chimborazo",
        "poblacion_aprox": 170_000,
        "sectores": ["La Condamine", "Bellavista", "La Paz", "Lican",
                     "Las Acacias", "El Recreo"],
        "paragraph_intro": (
            "Riobamba, 'Sultana de los Andes', combina tradición y vida universitaria. La "
            "demanda de internet residencial y empresarial crece cada año. SHENCOM brinda servicios "
            "Claro con instalación local."
        ),
        "cobertura_nota": (
            "Fibra óptica disponible en gran parte del casco urbano. Verificar disponibilidad "
            "en sectores rurales del cantón."
        ),
        "tiempo_instalacion": "48 a 96 horas hábiles",
        "vecinas": ["ambato", "latacunga"],
    },
    {
        "slug": "loja",
        "nombre": "Loja",
        "provincia": "Loja",
        "poblacion_aprox": 180_000,
        "sectores": ["La Tebaida", "Capulí Loma", "San Sebastián", "Sauces Norte",
                     "Punzara", "Época"],
        "paragraph_intro": (
            "Loja, cuna de músicos y universidades, demanda servicios de telecomunicaciones "
            "estables para su comunidad académica y profesional. SHENCOM ofrece planes Claro con "
            "atención técnica en la zona sur."
        ),
        "cobertura_nota": (
            "Cobertura de fibra óptica en sectores universitarios y residenciales. Tiempos de "
            "instalación pueden variar por la geografía montañosa."
        ),
        "tiempo_instalacion": "72 a 120 horas hábiles",
        "vecinas": ["machala", "cuenca"],
    },
    {
        "slug": "esmeraldas",
        "nombre": "Esmeraldas",
        "provincia": "Esmeraldas",
        "poblacion_aprox": 165_000,
        "sectores": ["Las Palmas", "La Tolita", "El Cabezón", "Centro",
                     "Codesa", "Vuelta Larga"],
        "paragraph_intro": (
            "Esmeraldas, principal ciudad del norte costero, requiere infraestructura de "
            "telecomunicaciones que respalde su actividad portuaria, turística y refinera. SHENCOM "
            "ofrece servicios Claro con cobertura en sectores urbanos."
        ),
        "cobertura_nota": (
            "Cobertura de fibra en sectores residenciales del centro y Las Palmas. Soluciones "
            "alternativas para zonas costeras periféricas."
        ),
        "tiempo_instalacion": "72 a 120 horas hábiles",
        "vecinas": ["santo-domingo", "manta"],
    },
    {
        "slug": "ibarra",
        "nombre": "Ibarra",
        "provincia": "Imbabura",
        "poblacion_aprox": 150_000,
        "sectores": ["Caranqui", "El Olivo", "Yacucalle", "La Victoria",
                     "Alpachaca", "La Florida"],
        "paragraph_intro": (
            "Ibarra, 'Ciudad Blanca a la que siempre se vuelve', es un destino turístico y "
            "centro provincial. SHENCOM atiende a hogares, hostales y comercios con planes Claro "
            "adaptados a la región andina."
        ),
        "cobertura_nota": (
            "Fibra óptica disponible en parroquias urbanas. Cobertura especial para "
            "establecimientos turísticos de El Olivo y Caranqui."
        ),
        "tiempo_instalacion": "72 a 120 horas hábiles",
        "vecinas": ["quito"],
    },
    {
        "slug": "latacunga",
        "nombre": "Latacunga",
        "provincia": "Cotopaxi",
        "poblacion_aprox": 110_000,
        "sectores": ["La Estación", "San Buenaventura", "El Niagara", "La Laguna",
                     "Loma Grande"],
        "paragraph_intro": (
            "Latacunga, a los pies del volcán Cotopaxi, es un nodo agroindustrial y turístico. "
            "SHENCOM ofrece servicios Claro con instalación rápida para hogares y haciendas con "
            "necesidades de conectividad."
        ),
        "cobertura_nota": (
            "Cobertura de fibra óptica en el casco urbano. Soluciones inalámbricas y satelitales "
            "para zonas rurales del cantón."
        ),
        "tiempo_instalacion": "72 a 120 horas hábiles",
        "vecinas": ["ambato", "riobamba", "quito"],
    },
    {
        "slug": "quevedo",
        "nombre": "Quevedo",
        "provincia": "Los Ríos",
        "poblacion_aprox": 175_000,
        "sectores": ["7 de Octubre", "San Camilo", "Venus del Río", "24 de Mayo",
                     "Nicolás Infante Díaz", "La Esmeralda"],
        "paragraph_intro": (
            "Quevedo, importante centro agrícola y comercial de Los Ríos, demanda servicios "
            "estables para su sector productivo. SHENCOM atiende a hogares, comercios y "
            "agronegocios con planes Claro."
        ),
        "cobertura_nota": (
            "Cobertura de fibra óptica en sectores residenciales y comerciales del centro. "
            "Disponibilidad creciente en zonas periféricas."
        ),
        "tiempo_instalacion": "72 a 120 horas hábiles",
        "vecinas": ["babahoyo", "santo-domingo", "guayaquil"],
    },
    {
        "slug": "babahoyo",
        "nombre": "Babahoyo",
        "provincia": "Los Ríos",
        "poblacion_aprox": 100_000,
        "sectores": ["Barreiro", "Centro", "La Ventura", "Puerta Negra",
                     "Las Mercedes"],
        "paragraph_intro": (
            "Babahoyo, capital provincial de Los Ríos, es un centro arrocero y administrativo. "
            "SHENCOM ofrece planes Claro con cobertura en la cabecera cantonal y soluciones "
            "técnicas para empresas agrícolas."
        ),
        "cobertura_nota": (
            "Cobertura de fibra óptica en el centro y Barreiro. Verificar disponibilidad "
            "específica por dirección."
        ),
        "tiempo_instalacion": "72 a 120 horas hábiles",
        "vecinas": ["quevedo", "guayaquil"],
    },
]


def get_ciudad_by_slug(slug: str) -> Optional[dict]:
    """Retorna el dict de una ciudad por su slug, o None."""
    for c in CIUDADES:
        if c["slug"] == slug:
            return c
    return None


def get_ciudades_vecinas(slug: str, max_n: int = 3) -> List[dict]:
    """Retorna las ciudades vecinas (para internal linking)."""
    ciudad = get_ciudad_by_slug(slug)
    if not ciudad:
        return []
    vecinas = []
    for v_slug in ciudad.get("vecinas", [])[:max_n]:
        v = get_ciudad_by_slug(v_slug)
        if v:
            vecinas.append(v)
    return vecinas

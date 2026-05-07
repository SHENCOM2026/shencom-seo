# SHENCOM — Sitio SEO programático

Distribuidor autorizado de Claro Ecuador. Sitio estático generado desde Python.

## Estructura

```
shencom-seo/
├── config-shencom.json    ← ÚNICO archivo que tú editas
├── data.py                ← datasets de ciudades (no editar salvo añadir ciudades)
├── generate.py            ← generador, no editar
├── README.md              ← este archivo
└── dist/                  ← OUTPUT — esto se sube a Netlify
    ├── index.html
    ├── planes-claro/<ciudad>/index.html
    ├── styles.css
    ├── sitemap.xml
    └── robots.txt
```

## Cómo regenerar el sitio

Desde la terminal (Aplicaciones → Utilidades → Terminal):

```bash
cd ~/shencom-seo
python3 generate.py
```

Eso reemplaza el contenido de `dist/` con la versión actualizada.

## Cómo editar los datos

1. Abre `config-shencom.json` con **TextEdit** (en modo texto plano) o **VS Code**.
   - **NO uses Word**. Word corrompe el formato JSON.
2. Cambia los valores entre comillas. Ejemplos:
   - `"telefono_principal": "+593-2-256-8901"`
   - `"whatsapp_e164": "+593987654321"` (sin guiones, formato E.164)
   - `"ruc": "1791234567001"`
3. Para activar el banner promocional: cambia `"activo": false` → `"activo": true`.
4. Guarda el archivo.
5. Corre `python3 generate.py`.

## Cómo añadir una ciudad nueva

1. Abre `data.py`.
2. Copia el bloque de cualquier ciudad existente (ej. Quito) y pégalo al final de la lista `CIUDADES`.
3. Cambia: `slug`, `nombre`, `provincia`, `poblacion_aprox`, `sectores`, `paragraph_intro`, `cobertura_nota`, `tiempo_instalacion`, `vecinas`.
4. Añade el teléfono zonal en `config-shencom.json` bajo `"telefonos_zonales"`.
5. Corre `python3 generate.py`.

## Cómo desplegar

### Opción A — Netlify Drop (la más simple)
1. Ir a https://app.netlify.com/drop
2. Arrastrar la carpeta `dist/` completa a la zona de drop.
3. Listo. Netlify te da una URL temporal (`xxx.netlify.app`).
4. Para conectar tu dominio `shencom.ec`: en el panel de Netlify → Domain settings → Add custom domain.

### Opción B — Netlify CLI (regenerar y subir con un comando)
```bash
npm install -g netlify-cli
cd ~/shencom-seo
netlify deploy --dir=dist --prod
```

## Verificación previa al despliegue

Antes de subir, abre el sitio localmente:

```bash
cd ~/shencom-seo/dist
python3 -m http.server 8000
```

Luego visita http://localhost:8000 en tu navegador. Revisa:
- [ ] Hub principal carga correctamente
- [ ] Páginas de ciudades funcionan (clic en cualquiera de las 15)
- [ ] Botones de WhatsApp abren con número correcto
- [ ] Botones de teléfono usan el número correcto
- [ ] Banner promocional aparece/desaparece según config

## Datos pendientes de rellenar (placeholders)

Antes del lanzamiento, reemplaza estos valores en `config-shencom.json`:

| Campo | Estado |
|---|---|
| `empresa.razon_social` | `PEGAR_AQUI_RAZON_SOCIAL` |
| `empresa.ruc` | `PEGAR_AQUI_RUC_13_DIGITOS` |
| `empresa.direccion_matriz` | `PEGAR_AQUI_DIRECCION_COMPLETA` |
| `empresa.telefono_principal` | `+593-2-000-0000` |
| `empresa.whatsapp_e164` | `+593990000000` |
| `telefonos_zonales.*` | 15 teléfonos por ciudad |
| `sitio.google_analytics_id` | `G-XXXXXXXXXX` |
| `sitio.google_search_console_token` | `PEGAR_AQUI_META_TAG...` |
| `planes_internet_hogar` | Verificar precios reales Claro |
| `planes_pospago_movil` | Verificar precios reales Claro |

## Stack y por qué

- **Python 3** (incluido en macOS): cero dependencias externas.
- **HTML estático puro**: máximo rendimiento (Core Web Vitals altos = mejor SEO).
- **CSS plano**: sin frameworks ni build tools.
- **Schema.org JSON-LD**: estructurado para Google (LocalBusiness por ciudad).
- **Sitemap + robots.txt**: incluidos automáticamente.
- **15 páginas únicas** con contenido específico por ciudad (evita penalización por thin content).

## Mantenimiento

- **Semanal**: revisar Search Console por errores.
- **Mensual**: actualizar precios en `config-shencom.json` si Claro los cambia.
- **Trimestral**: añadir 1-2 ciudades nuevas si hay demanda.
- **Anual**: renovar dominio `.ec` y revisar contenido por ciudad.

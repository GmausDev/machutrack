# machutrack

Registra cada 15 minutos durante el horario de venta (y cada 2 horas el resto del día) la disponibilidad de entradas de **venta presencial** para
Machu Picchu que publica el Ministerio de Cultura en
<https://tuboleto.cultura.pe/disponibilidad/llaqta_machupicchu>, para ver si vale la
pena ir sin entrada y comprarla en el Centro Cultural (Machu Picchu Pueblo).

Esa página muestra, para el **día siguiente**:
- entradas por ruta: aforo, vendidas y disponibles;
- turnos de la cola: entregados y disponibles;
- hora de inicio de la venta (06:00).

## Cómo funciona

- `tracker/scrape.py` abre la página en Chromium headless (es una app Angular, así que
  sin navegador no hay datos), lee el texto y añade una fila por ruta a
  `data/snapshots.csv`.
- `tracker/report.py` genera `REPORT.md`: la hora a la que se agota cada ruta, cada día
  y la mediana entre días.
- `site/index.html` es el dashboard: lee `data/snapshots.csv` y muestra, para cada día
  de visita, lo que queda por ruta, la evolución a lo largo del día, los turnos de la cola
  y a qué hora suele agotarse cada ruta.
- `.github/workflows/track.yml` ejecuta todo en GitHub Actions (cada 15 min de 05:00 a 17:00 de Lima, cada 2 h el resto), hace
  commit de los datos y publica el dashboard en GitHub Pages.

## Disparador externo (recomendado)

El cron de GitHub no es fiable: retrasa o se salta ejecuciones, a veces durante horas
(el 24/09/2026 no lanzó ninguna entre las 05:00 y las 09:50 de Lima). Para no perder la
franja clave, un servicio externo lanza el workflow cada 15 min y el cron de GitHub
queda como respaldo. El workflow no ejecuta dos capturas a la vez, así que no se
duplican.

### 1. Token de GitHub

En <https://github.com/settings/personal-access-tokens/new> (fine-grained token):

- **Repository access:** *Only select repositories* → `machutrack`.
- **Permissions → Repository permissions → Actions:** *Read and write*. Nada más.
- **Expiration:** que cubra hasta después del viaje.

Copia el token (`github_pat_...`); solo se muestra una vez.

### 2. Tarea en cron-job.org

En <https://cron-job.org> (gratis) → *Create cronjob*:

- **URL:** `https://api.github.com/repos/GmausDev/machutrack/actions/workflows/track.yml/dispatches`
- **Schedule:** *Custom* → minutos `0,15,30,45`, horas `5-17`, todos los días.
  Zona horaria del job: **America/Lima**.
- **Advanced → Request method:** `POST`
- **Advanced → Headers:**
  - `Accept: application/vnd.github+json`
  - `Authorization: Bearer github_pat_...` (tu token)
  - `X-GitHub-Api-Version: 2022-11-28`
  - `Content-Type: application/json`
- **Advanced → Request body:** `{"ref":"main"}`
- **Notifications:** activa el aviso por email si falla.

Pulsa *Test run*: la respuesta correcta es **204 No Content** y en la pestaña Actions
aparece una ejecución `workflow_dispatch`. Un 401 es un token mal copiado, un 403 o 404
es que le falta el permiso *Actions: Read and write* o el acceso a `machutrack`.

Opcional: crea una segunda tarea igual con horas `19,21,23,1,3` y minuto `0` para las
capturas nocturnas.

## Uso local

```bash
pip install -r requirements.txt
python -m playwright install chromium
python -m tracker.scrape   # una captura
python -m tracker.report   # regenera REPORT.md
python -m pytest -q

# ver el dashboard con tus datos
mkdir -p _site/data && cp site/index.html _site/ && cp data/snapshots.csv _site/data/
python -m http.server -d _site 8000   # http://localhost:8000
```

## Cómo leer los datos

La pregunta clave es **a qué hora se agota cada ruta**. Si la «Hora mediana de
agotamiento» de la ruta que quieres es media mañana o más tarde, llegar a Aguas
Calientes la tarde anterior y ponerte en la cola a primera hora es viable. Si se agota
a los pocos minutos de abrir la venta, necesitas llegar muy pronto o elegir otra ruta
(la 2-A Clásica tiene el aforo más grande, 600 en venta presencial).

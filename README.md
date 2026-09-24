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

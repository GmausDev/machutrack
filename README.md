# machutrack

Registra cada 30 minutos la disponibilidad de entradas de **venta presencial** para
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
- `.github/workflows/track.yml` ejecuta ambos cada 30 minutos en GitHub Actions y
  hace commit de los datos.

Para activarlo, el workflow tiene que estar en la rama por defecto (`main`); los cron
de GitHub solo se ejecutan ahí. También se puede lanzar a mano desde la pestaña
Actions (**Run workflow**).

## Uso local

```bash
pip install -r requirements.txt
python -m playwright install chromium
python -m tracker.scrape   # una captura
python -m tracker.report   # regenera REPORT.md
python -m pytest -q
```

## Cómo leer los datos

La pregunta clave es **a qué hora se agota cada ruta**. Si la «Hora mediana de
agotamiento» de la ruta que quieres es media mañana o más tarde, llegar a Aguas
Calientes la tarde anterior y ponerte en la cola a primera hora es viable. Si se agota
a los pocos minutos de abrir la venta, necesitas llegar muy pronto o elegir otra ruta
(la 2-A Clásica tiene el aforo más grande, 600 en venta presencial).

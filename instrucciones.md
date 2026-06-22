# Modificación de interfaz web Red Pitaya STEMLab 125-14

Placa de referencia: **STEMLab 125-14**, IP `10.42.0.180`, ecosistema `2.07-51`.

---

## Qué hace esta modificación

1. **Pantalla principal**: muestra solo 4 entradas (oculta el resto).
   - System *(grupo)*
   - Development *(grupo)*
   - Oscilloscope
   - DFT Spectrum Analyser

2. **Título del browser**: todas las pestañas muestran **"Edge"** en lugar de "Red Pitaya" / "My Red Pitaya".

3. **Favicon**: reemplaza el ícono de Red Pitaya por `logo4.png` en todas las pestañas.

4. **Logo de navbar** (esquina superior izquierda de cada app): reemplaza `navigation_logo.png` por `logo1.png`.

5. **Ícono de External Connections** (botón de conexiones externas): reemplaza `ext_conections_w.png` por `logo6.png`.

6. **Centrado del logo de navbar**: corrige el margen en el CSS de cada app a `11px 0px 0px 14px`.

7. **Escala del espectrograma waterfall** (DFT Spectrum Analyser): corrige la posición de los números de escala para que aparezcan al pie del gráfico en lugar del centro.

---

## Archivos locales necesarios

Todos están en este directorio (`/home/facu-edge/web_pitaya/`):

| Archivo local | Destino en la placa | Uso |
|---|---|---|
| `black_list_app.js` | `.../assets/black_list_app.js` | Whitelist de apps en pantalla principal |
| `favicon.ico` | `.../apps/favicon.ico` | Favicon (ICO generado de logo4.png) |
| `logos/logo1.png` | `.../assets/images/logo1.png` | Logo de navbar |
| `logos/logo4.png` | `.../apps/logo4.png` | Imagen fuente del favicon |
| `logos/logo6_icon.png` | `.../assets/images/logo6.png` | Ícono External Connections (36×22px) |

> El prefijo `...` es `/opt/redpitaya/www/apps`.

---

## Pasos para aplicar en una nueva placa

### 1. Remuntar la partición en modo escritura

La partición `/opt/redpitaya` es **vfat** y se monta **read-only** por defecto desde `/dev/mmcblk0p1`.

```bash
ssh root@<IP_PLACA>
mount -o remount,rw /opt/redpitaya
```

### 2. Hacer backups

```bash
BASE=/opt/redpitaya/www/apps

cp $BASE/assets/black_list_app.js   $BASE/assets/black_list_app.js.bak
cp $BASE/favicon.ico                $BASE/favicon.ico.bak
cp $BASE/index.html                 $BASE/index.html.bak
cp $BASE/scopegenpro/index.html     $BASE/scopegenpro/index.html.bak
cp $BASE/spectrumpro/index.html     $BASE/spectrumpro/index.html.bak
cp $BASE/updater/index.html         $BASE/updater/index.html.bak
cp $BASE/network_manager/index.html $BASE/network_manager/index.html.bak
cp $BASE/scpi_manager/index.html    $BASE/scpi_manager/index.html.bak
cp $BASE/calib_app/index.html       $BASE/calib_app/index.html.bak
cp $BASE/spectrumpro/js/scope.js    $BASE/spectrumpro/js/scope.js.bak
```

### 3. Subir archivos locales

Ejecutar desde la máquina local:

```bash
IP=<IP_PLACA>
BASE=root@$IP:/opt/redpitaya/www/apps

scp /home/facu-edge/web_pitaya/black_list_app.js     $BASE/assets/black_list_app.js
scp /home/facu-edge/web_pitaya/favicon.ico           $BASE/favicon.ico
scp /home/facu-edge/web_pitaya/logos/logo4.png       $BASE/logo4.png
scp /home/facu-edge/web_pitaya/logos/logo1.png       $BASE/assets/images/logo1.png
scp /home/facu-edge/web_pitaya/logos/logo6_icon.png  $BASE/assets/images/logo6.png
```

### 4. Aplicar modificaciones en HTML, CSS y JS

Ejecutar en la placa vía SSH (un único script Python hace todo):

```bash
python3 << 'EOF'
import re, os

BASE = '/opt/redpitaya/www/apps'
FAVICON = '    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" />\n    <link rel="icon" href="/favicon.ico" type="image/x-icon">\n'

def patch(path):
    with open(path) as f: return f.read()
def save(path, c):
    with open(path, 'w') as f: f.write(c)
    print(f'OK: {path.replace(BASE+"/","")}')

# ── Pantalla principal: título + favicon ─────────────────────────────────────
p = f'{BASE}/index.html'
c = patch(p)
c = c.replace('<title>My Red Pitaya</title>', '<title>Edge</title>')
c = c.replace('<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" />',
              '<link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" />')
save(p, c)

# ── Oscilloscope y DFT: título + favicon ─────────────────────────────────────
for app in ['scopegenpro', 'spectrumpro']:
    p = f'{BASE}/{app}/index.html'
    c = patch(p)
    c = c.replace('<title>Red Pitaya</title>', '<title>Edge</title>')
    if '/favicon.ico' not in c:
        c = c.replace('</head>', FAVICON + '</head>', 1)
    save(p, c)

# ── Oscilloscope y DFT: logo navbar + ícono ext_connections ──────────────────
adc_files = [
    f'{BASE}/scopegenpro/2ch_adc.html',
    f'{BASE}/scopegenpro/4ch_adc.html',
    f'{BASE}/spectrumpro/2ch_adc.html',
    f'{BASE}/spectrumpro/4ch_adc.html',
]
for p in adc_files:
    c = patch(p)
    c = c.replace('src="../assets/images/navigation_logo.png"',
                  'src="../assets/images/logo1.png"')
    c = c.replace('ext_conections_w.png', 'logo6.png')
    c = re.sub(r'(id="ext_con_but"[^>]*><img[^>]*?)height: 20px', r'\1height: 22px', c)
    save(p, c)

# ── Apps de System y Development: título + favicon + logo navbar ──────────────
simple_apps = ['updater', 'network_manager', 'calib_app']
for app in simple_apps:
    p = f'{BASE}/{app}/index.html'
    c = patch(p)
    c = c.replace('<title>Red Pitaya</title>', '<title>Edge</title>')
    if '/favicon.ico' not in c:
        c = c.replace('</head>', FAVICON + '</head>', 1)
    c = c.replace('src="../assets/images/navigation_logo.png"',
                  'src="../assets/images/logo1.png"')
    save(p, c)

# scpi_manager: igual que arriba + ext_connections
p = f'{BASE}/scpi_manager/index.html'
c = patch(p)
c = c.replace('<title>Red Pitaya</title>', '<title>Edge</title>')
if '/favicon.ico' not in c:
    c = c.replace('</head>', FAVICON + '</head>', 1)
c = c.replace('src="../assets/images/navigation_logo.png"',
              'src="../assets/images/logo1.png"')
c = c.replace('ext_conections_w.png', 'logo6.png')
c = re.sub(r'(id="ext_con_but"[^>]*><img[^>]*?)height: 20px', r'\1height: 22px', c)
save(p, c)

# calib_app: logo navbar en archivos adc
for variant in ['2ch_adc.html', '4ch_adc.html']:
    p = f'{BASE}/calib_app/{variant}'
    c = patch(p)
    c = c.replace('src="../assets/images/navigation_logo.png"',
                  'src="../assets/images/logo1.png"')
    save(p, c)

# ── CSS: centrado del logo de navbar (.logo margin) ───────────────────────────
css_files = [
    f'{BASE}/scopegenpro/css/style.css',
    f'{BASE}/spectrumpro/css/style.css',
    f'{BASE}/updater/css/style.css',
    f'{BASE}/network_manager/css/style.css',
    f'{BASE}/scpi_manager/css/style.css',
    f'{BASE}/calib_app/css/style.css',
]
for p in css_files:
    c = patch(p)
    updated = re.sub(
        r'(\.logo\s*\{[^}]*margin:\s*)[^;]+(;)',
        lambda m: m.group(1) + '11px 0px 0px 14px' + m.group(2),
        c
    )
    save(p, updated)

# ── scope.js: escala del waterfall al pie del gráfico ────────────────────────
p = f'{BASE}/spectrumpro/js/scope.js'
c = patch(p)
c = c.replace('modifynode.css("top","65px")', 'modifynode.css("top","248px")')
save(p, c)

EOF
```

### 5. Restaurar la partición a solo-lectura

```bash
mount -o remount,ro /opt/redpitaya
```

### 6. Recargar en el browser

**Ctrl+Shift+R** en cada pestaña para forzar recarga de cache. No se requiere reiniciar la placa.

---

## Cómo revertir todo

```bash
ssh root@<IP_PLACA>
mount -o remount,rw /opt/redpitaya

BASE=/opt/redpitaya/www/apps
for f in \
  assets/black_list_app.js \
  favicon.ico \
  index.html \
  scopegenpro/index.html \
  spectrumpro/index.html \
  updater/index.html \
  network_manager/index.html \
  scpi_manager/index.html \
  calib_app/index.html \
  spectrumpro/js/scope.js
do
  [ -f "$BASE/$f.bak" ] && cp "$BASE/$f.bak" "$BASE/$f" && echo "restored: $f"
done

mount -o remount,ro /opt/redpitaya
```

> Los CSS no tienen backup automático. Para revertirlos, cambiar `margin: 11px 0px 0px 14px` a `margin: 5px 0px 0px 15px` en los 6 archivos `css/style.css` de cada app.

---

## Para modificar qué apps se muestran en la pantalla principal

Editar `black_list_app.js` (local) y buscar al final de la función `filterApps`:

```javascript
// Whitelist: only show these apps at root level (no group)
var allowed_root = ["scopegenpro", "spectrumpro"];
```

Agregar o quitar IDs. Los IDs corresponden al nombre del directorio en `/opt/redpitaya/www/apps/`.

### IDs de apps disponibles (STEM 125-14)

| ID | Nombre visible |
|---|---|
| `scopegenpro` | Oscilloscope |
| `spectrumpro` | DFT Spectrum Analyser |
| `ba_pro` | Bode Analyser |
| `lcr_meter` | LCR meter |
| `impedance_analyzer` | Impedance Analyser |
| `la_pro` | Logic analyser |
| `streaming_manager` | Data stream control |
| `arb_manager` | ARB manager |
| `calib_app` | Calibration |
| `network_manager` | Network Manager |
| `scpi_manager` | Remote control (SCPI) |
| `jupyter_manager` | Jupyter notebook |
| `updater` | Red Pitaya OS Update |

Los grupos `System` y `Development` siempre se muestran — no son apps, se agregan al DOM después del filtro en `desktop.js`.

---

## Notas técnicas

- La partición `/opt/redpitaya` es `vfat` montada desde `/dev/mmcblk0p1` (tarjeta SD, partición 1). Requiere `remount,rw` antes de cualquier cambio y `remount,ro` al terminar.
- El favicon se generó convirtiendo `logo4.png` (116×187px RGBA) a formato ICO con 3 tamaños (16×16, 32×32, 48×48) usando Python PIL. El archivo `favicon.ico` local ya contiene esta conversión.
- El ícono `logo6.png` fue redimensionado a 36×22px (proporción original 223×139) y guardado como `logos/logo6_icon.png`. El archivo subido a la placa como `logo6.png` es esa versión redimensionada.
- El logo de navbar `logo1.png` (782×147px) se muestra con `width=110` y `margin: 11px 0px 0px 14px` para centrarlo verticalmente en la navbar Bootstrap de 50px de altura.
- La escala del waterfall en DFT (`spectrumpro/js/scope.js`) clona etiquetas del eje X del gráfico Flot y las reposiciona con `top` fijo. El valor original era `65px` (quedaba en el medio del canvas de 240px dentro del holder de 280px). El valor correcto es `248px` (240px del canvas + 8px de margen).
- El filtro whitelist en `black_list_app.js` actúa dentro de `Desktop.filterApps()`, que corre después de asignar grupos a las apps pero antes de agregar los íconos de grupo al DOM. Por eso `System` y `Development` no son afectados por el filtro.

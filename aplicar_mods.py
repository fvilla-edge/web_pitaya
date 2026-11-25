#!/usr/bin/env python3
"""Aplica la personalizacion Edge a la web de Red Pitaya (ecosistema 3.00).

Correr EN LA PLACA, con /opt/redpitaya montado rw y los logos ya subidos
(ver instrucciones.md). Primero verifica que todo lo que va a reemplazar
este en su valor de stock; si algo no coincide no escribe nada.
Hace .bak de cada archivo (solo si no existe uno), asi el revert vuelve a stock.
"""
import os
import re
import shutil
import sys

BASE = os.environ.get('WEB_BASE', '/opt/redpitaya/www/apps')

# Rango de frecuencia del DFT (lo guarda la app, no la web): 0-62,5 MHz -> 0-1 MHz
DFT_CONFIG = os.environ.get(
    'DFT_CONFIG', '/root/.config/redpitaya/apps/spectrumpro_2/config.json')
XMAX_STOCK, XMAX = 62500000, 1000000

# Waterfall del DFT (ecosistema 3.00): canvas 60 -> 300
CANVAS_STOCK, CANVAS = 60, 300
HOLDER_STOCK, HOLDER = 80, 320
MULT_STOCK, MULT = 95, 335
TOP_STOCK, TOP = 65, 305

ALLOWED_ROOT = ['scopegenpro', 'spectrumpro']

FAVICON = ('    <link rel="shortcut icon" href="/favicon.ico" type="image/x-icon" />\n'
           '    <link rel="icon" href="/favicon.ico" type="image/x-icon">\n')
WHITELIST = '''
        // Whitelist: only show these apps at root level (no group)
        var allowed_root = %s;
        for (var i = listOfapplications.length - 1; i >= 0; i -= 1) {
            var app = listOfapplications[i];
            if ((app.group === "" || app.group === undefined || app.group === null) && !app.is_group) {
                if (allowed_root.indexOf(app.id) === -1) {
                    listOfapplications.splice(i, 1);
                }
            }
        }

        return listOfapplications;
    }

})(window.Desktop = window.Desktop || {}, jQuery);''' % (
    '[' + ', '.join('"%s"' % a for a in ALLOWED_ROOT) + ']')



def rango_dft():
    """Pone xmax del DFT en 1 MHz. Independiente del resto (otro archivo,
    lo reescribe la app): correr con el DFT CERRADO o la app lo pisa."""
    if not os.path.isfile(DFT_CONFIG):
        print(f'AVISO rango DFT: no existe {DFT_CONFIG}; abrir el DFT una vez, '
              'cerrarlo y correr: python3 aplicar_mods.py --solo-rango-dft')
        return False
    with open(DFT_CONFIG, newline='') as f:
        c = f.read()
    m = re.findall(r'"xmax":(\d+)', c)
    if m == [str(XMAX)]:
        print(f'rango DFT: ya estaba en {XMAX} Hz')
        return True
    if m != [str(XMAX_STOCK)]:
        print(f'AVISO rango DFT: xmax esperado {XMAX_STOCK}, hay {m}; no se toca')
        return False
    if not os.path.exists(DFT_CONFIG + '.bak'):
        shutil.copy2(DFT_CONFIG, DFT_CONFIG + '.bak')
    with open(DFT_CONFIG, 'w', newline='') as f:
        f.write(c.replace(f'"xmax":{XMAX_STOCK}', f'"xmax":{XMAX}'))
    os.sync()
    print(f'OK: rango DFT 0-{XMAX} Hz ({DFT_CONFIG})')
    return True


if '--solo-rango-dft' in sys.argv[1:]:
    sys.exit(0 if rango_dft() else 1)

cambios = {}   # ruta -> contenido nuevo
errores = []


def leer(rel):
    p = os.path.join(BASE, rel)
    if p in cambios:
        return cambios[p]
    with open(p, newline='') as f:
        return f.read()


def reemplazar(rel, viejo, nuevo, veces=1, regex=False):
    """Reemplaza exactamente `veces` ocurrencias; si no, registra error."""
    c = leer(rel)
    n = len(re.findall(viejo, c)) if regex else c.count(viejo)
    if n != veces:
        errores.append(f'{rel}: esperaba {veces} de {viejo!r}, hay {n}')
        return
    c = re.sub(viejo, nuevo, c) if regex else c.replace(viejo, nuevo)
    cambios[os.path.join(BASE, rel)] = c


def favicon_y_titulo(rel, titulo_stock):
    reemplazar(rel, f'<title>{titulo_stock}</title>', '<title>Edge</title>')
    if '/favicon.ico' not in leer(rel):
        reemplazar(rel, '</head>', FAVICON + '</head>')


# Pantalla principal
favicon_y_titulo('index.html', 'My Red Pitaya')
c = leer('assets/black_list_app.js')
if 'allowed_root' in c:
    errores.append('assets/black_list_app.js: ya tiene allowed_root (¿ya aplicado?)')
else:
    reemplazar('assets/black_list_app.js',
               r'\n\s*return listOfapplications;\s*\}\s*\}\)\(window\.Desktop = window\.Desktop \|\| \{\}, jQuery\);\s*$',
               lambda m: WHITELIST + '\n', regex=True)

# Oscilloscope y DFT: titulo, favicon, logo navbar, icono External Connections
for app in ['scopegenpro', 'spectrumpro']:
    favicon_y_titulo(f'{app}/index.html', 'Red Pitaya')
    for v in ['2ch_adc.html', '4ch_adc.html']:
        rel = f'{app}/{v}'
        reemplazar(rel, 'src="../assets/images/navigation_logo.png"',
                   'src="../assets/images/logo1.png"')
        reemplazar(rel, 'ext_conections_w.png', 'logo6.png')

# System / Development
for app in ['updater', 'network_manager', 'scpi_manager']:
    favicon_y_titulo(f'{app}/index.html', 'Red Pitaya')
    reemplazar(f'{app}/index.html', 'src="../assets/images/navigation_logo.png"',
               'src="../assets/images/logo1.png"')
if 'ext_conections_w.png' in leer('scpi_manager/index.html'):
    reemplazar('scpi_manager/index.html', 'ext_conections_w.png', 'logo6.png')
favicon_y_titulo('calib_app/index.html', 'Red Pitaya')
for v in ['2ch_adc.html', '4ch_adc.html']:
    rel = f'calib_app/{v}'
    if 'navigation_logo.png' in leer(rel):
        reemplazar(rel, 'src="../assets/images/navigation_logo.png"',
                   'src="../assets/images/logo1.png"')

# Margen del logo de navbar
for app in ['scopegenpro', 'spectrumpro', 'updater', 'network_manager',
            'scpi_manager', 'calib_app']:
    rel = f'{app}/css/style.css'
    c = leer(rel)
    if re.search(r'\n\.logo\s*\{[^}]*margin:', c):
        reemplazar(rel, r'(\n\.logo\s*\{[^}]*margin:\s*)[^;]+(;)',
                   r'\g<1>11px 0px 0px 14px\g<2>', regex=True)

# Waterfall del DFT
css = 'spectrumpro/css/style.css'
reemplazar(css, r'(\.waterfall-holder \{[^}]*min-height: )%dpx' % HOLDER_STOCK,
           r'\g<1>%dpx' % HOLDER, regex=True)
reemplazar(css, r'(\.waterfall-holder \{[^}]*max-height: )%dpx' % HOLDER_STOCK,
           r'\g<1>%dpx' % HOLDER, regex=True)
reemplazar(css, r'(\.waterfall-graph \{[^}]*min-height: )%dpx' % CANVAS_STOCK,
           r'\g<1>%dpx' % CANVAS, regex=True)
reemplazar(css, r'(\.waterfall-graph \{[^}]*max-height: )%dpx' % CANVAS_STOCK,
           r'\g<1>%dpx' % CANVAS, regex=True)
reemplazar(css, r'(\.waterfall_canvas \{[^}]*height: )%dpx' % CANVAS_STOCK,
           r'\g<1>%dpx' % CANVAS, regex=True)

js = 'spectrumpro/js/scope.js'
reemplazar(js, r"(\.width\(\), )%d\)" % CANVAS_STOCK, r'\g<1>%d)' % CANVAS,
           veces=4, regex=True)
reemplazar(js, 'setSize(ww, %d)' % CANVAS_STOCK, 'setSize(ww, %d)' % CANVAS)
reemplazar(js, '%d * SPEC.visibleCount() + 10' % MULT_STOCK,
           '%d * SPEC.visibleCount() + 10' % MULT)
reemplazar(js, 'modifynode.css("top","%dpx")' % TOP_STOCK,
           'modifynode.css("top","%dpx")' % TOP)

for f in ['favicon.ico', 'logo4.png', 'assets/images/logo1.png', 'assets/images/logo6.png']:
    if not os.path.isfile(os.path.join(BASE, f)):
        errores.append(f'falta {f} (subirlo antes con scp)')

if errores:
    print('NO SE APLICO NADA:')
    for e in errores:
        print('  -', e)
    sys.exit(1)

for p, c in cambios.items():
    if not os.path.exists(p + '.bak'):
        shutil.copy2(p, p + '.bak')
    with open(p, 'w', newline='') as f:
        f.write(c)
    print('OK:', p.replace(BASE + '/', ''))
os.sync()
print(f'{len(cambios)} archivos modificados')
rango_dft()

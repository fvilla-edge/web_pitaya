# Modificación de interfaz web Red Pitaya STEMLab 125-14

Placa de referencia original: **STEMLab 125-14**, IP `10.42.0.180`, ecosistema `2.07-51`.
Placa de campo (sand monitoring): IP `192.168.0.54` (varía según red), ecosistema `3.00-e00665135` (kernel 2026.1).
Placa de laboratorio `rp-f0fd8c` (ecosistema 3.00): aplicado con `aplicar_mods.py` el 20/11/2026 (demo del 10/12).

> **Los valores en px del punto 8 son específicos del ecosistema y NO son intercambiables entre versiones.**
> Antes de aplicar el paso 8 en una placa nueva, verificar los valores de stock reales (ver "Antes de tocar el waterfall" más abajo) — aplicarlos a ciegas dejó el waterfall roto (franja angosta + hueco enorme) la primera vez que se corrió este doc contra la placa de ecosistema `3.00`.

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

8. **Tamaño de `root_plot` y `root_waterfall`** (DFT Spectrum Analyser): ajusta ambos bloques para que el waterfall se vea bien y entre en pantalla sin scroll. El tamaño de stock varía por ecosistema — ver tabla abajo.

9. **Rango de frecuencia del DFT 0–1 MHz** (de stock 0–62,5 MHz): no es un archivo de la web sino la configuración que guarda la app, `/root/.config/redpitaya/apps/spectrumpro_2/config.json` (`"xmax":62500000` → `"xmax":1000000`). Ese archivo lo reescribe la app, así que hay que cambiarlo **con el DFT cerrado**, y solo existe después de haber abierto el DFT al menos una vez. Si alguien restablece los valores por defecto de la app o cambia el campo de frecuencia máxima en pantalla, se pierde (se arregla escribiendo 1000000 en ese campo).

### Antes de tocar el waterfall: verificar valores de stock

El tamaño del waterfall depende de 4 cosas que hay que revisar en la placa ANTES de tocar nada (los valores de ejemplo son de las dos placas ya probadas):

| Elemento | Dónde | Ecosistema `2.07-51` (original) | Ecosistema `3.00` (campo) |
|---|---|---|---|
| Canvas/graph CSS | `.waterfall-holder .waterfall-graph` min/max-height | 240px | 60px |
| Holder CSS | `.waterfall-holder` min/max-height | 280px | 80px |
| **Resolución real del canvas (JS, no CSS)** | `scope.js`: `$.createWaterfall(..., N)` (×4, una por canal) y `setSize(ww, N)` en el resize handler | 240 | 60 |
| Multiplicador contenedor | `scope.js`: `N * SPEC.visibleCount() + 10` | 95 (stock) | 95 (stock) |
| Offset de escala | `scope.js`: `modifynode.css("top","Npx")` | 65px (stock, antes de reducir) | 65px (stock) |

**El punto que instrucciones.md original NO documentaba**: la resolución real de dibujo del canvas está hardcodeada en JS (`createWaterfall(..., 60)` y `setSize(ww, 60)`), separada del tamaño CSS. Agrandar/achicar solo el CSS sin tocar estos valores de JS deja el canvas estirado o con un hueco vacío — hay que cambiar los dos juntos, al mismo número.

**Segundo punto que tampoco se documentaba, y causó una vuelta extra en la placa de campo**: además de `.waterfall-holder .waterfall-graph` (la altura del DIV contenedor), existe una regla CSS separada `.waterfall_canvas { height: 60px; }` (con guión bajo, distinta clase) que aplica directo sobre el `<canvas>` real que crea `waterfall.js`. Esta regla es MÁS específica que la del div contenedor y gana la cascada — si no se cambia también, el canvas visualmente queda clavado en 60px aunque el contenedor, la resolución JS y todo lo demás ya estén en el valor nuevo (así se ve: franja de color chica arriba + hueco vacío abajo dentro de un contenedor que sí creció). Buscar `grep -n 'waterfall_canvas' css/style.css` (guión bajo) antes de dar por buena cualquier corrección de tamaño — es fácil de pasar por alto porque el nombre es casi idéntico a `.waterfall-holder` / `.waterfall-graph` (guión medio).

**Cómo elegir los nuevos valores** (ejemplo: agrandar canvas de 60px a 180px en la placa de campo):
1. Canvas nuevo = el que se quiera (ej. 180px). Aplicar ese mismo número en CSS (`.waterfall-graph`) y en JS (los 5 lugares con la resolución hardcodeada).
2. Holder nuevo = canvas_nuevo + (holder_stock − canvas_stock). Ej: 180 + (80−60) = 200px.
3. Multiplicador nuevo = holder_nuevo + (multiplicador_stock − holder_stock). Ej: 200 + (95−80) = 215.
4. Offset de escala nuevo = canvas_nuevo + (offset_stock − canvas_stock). Ej: 180 + (65−60) = 185px.

Aplicado finalmente así en la placa de campo (ecosistema `3.00`, canvas 60→300px, tras dos vueltas — la primera a 180px no incluía el fix de `.waterfall_canvas`):
   - CSS: `.waterfall-holder` 80px → 320px, `.waterfall-holder .waterfall-graph` 60px → 300px, **`.waterfall_canvas` 60px → 300px (el fix real, ver arriba)**.
   - JS `scope.js`: las 5 llamadas de resolución del canvas (`createWaterfall` ×4 + `setSize`) `60` → `300`.
   - JS `scope.js`: fórmula de altura del contenedor waterfall `95 × canales + 10` → `335 × canales + 10`.
   - JS `scope.js`: posición de la escala `top: 65px` → `top: 305px`.

En la placa original de referencia (ecosistema `2.07-51`, canvas 240→180px, es decir una *reducción*) se había aplicado:
   - CSS: `.waterfall-holder` 280 px → 210 px, canvas/graph 240 px → 180 px, margen `.wait` -120 px → -90 px.
   - JS `scope.js`: fórmula de altura del contenedor waterfall `95 × canales + 10` → `220 × canales + 10`.
   - JS `scope.js`: posición de la escala `top: 248px` → `top: 188px` (180 px de canvas + 8 px de margen).
   - (esa placa no tenía el problema del canvas hardcodeado documentado — no se verificó en su momento; si se vuelve a tocar esa placa, revisar `createWaterfall`/`setSize` igual que en el punto de arriba antes de asumir que solo el CSS alcanza)

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

### 2. Respaldar el favicon de stock (se pisa con scp)

```bash
B=/opt/redpitaya/www/apps
[ -f $B/favicon.ico.bak ] || cp -p $B/favicon.ico $B/favicon.ico.bak
```

### 3. Subir logos y script (desde la PC)

```bash
IP=<IP_PLACA>
BASE=root@$IP:/opt/redpitaya/www/apps

scp /home/facu-edge/web_pitaya/favicon.ico           $BASE/favicon.ico
scp /home/facu-edge/web_pitaya/logos/logo4.png       $BASE/logo4.png
scp /home/facu-edge/web_pitaya/logos/logo1.png       $BASE/assets/images/logo1.png
scp /home/facu-edge/web_pitaya/logos/logo6_icon.png  $BASE/assets/images/logo6.png
scp /home/facu-edge/web_pitaya/aplicar_mods.py       root@$IP:/root/aplicar_mods_web.py
```

> **No subir `black_list_app.js` local encima del de la placa.** El local está hecho sobre el ecosistema 2.07; el de 3.00 trae modelos y apps nuevos (Thetis, modelos 31/32). El script inserta solo el bloque `allowed_root` en el archivo de la placa. El `black_list_app.js` local queda como referencia del bloque.

### 4. Aplicar (en la placa)

```bash
python3 /root/aplicar_mods_web.py
```

`aplicar_mods.py` (ecosistema 3.00):
- Verifica primero que cada cosa a reemplazar esté en su valor de stock (titles, logos, `ext_conections_w.png`, márgenes `.logo`, waterfall 80/60/60/95/65). Si algo no coincide, **no escribe nada** y lista qué falló (ej. ya aplicado, o ecosistema distinto).
- Crea `.bak` de cada archivo que toca (solo si no existe), CSS incluidos.
- Conserva los finales de línea CRLF de los HTML (`newline=''`).
- Valores del waterfall y lista de apps: constantes al principio del script (`CANVAS`, `HOLDER`, `MULT`, `TOP`, `ALLOWED_ROOT`).
- Prueba en seco en la PC: copiar los archivos de la placa a una carpeta y correr `WEB_BASE=<carpeta> python3 aplicar_mods.py`.
- Al final aplica el punto 9 (rango DFT 1 MHz) por separado: si el `config.json` no existe o tiene otro valor, solo avisa y no frena lo demás (`.bak` al lado del archivo). Para hacer **solo** ese paso (placa ya modificada, o después de abrir el DFT por primera vez), con el DFT cerrado:
  ```bash
  python3 /root/aplicar_mods_web.py --solo-rango-dft
  ```
  Constantes `XMAX`/`XMAX_STOCK`; prueba en la PC con `DFT_CONFIG=<archivo>`.

Para ecosistema 2.07 el script NO sirve tal cual (stock distinto: canvas 240, holder 280); ver la tabla de arriba.

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
cd /opt/redpitaya/www/apps
find . -name "*.bak" | while read f; do cp -p "$f" "${f%.bak}" && echo "restored: ${f%.bak}"; done
sync
mount -o remount,ro /opt/redpitaya
```

Todos los archivos tocados (CSS incluidos) tienen `.bak`. El rango del DFT se revierte aparte: `cp -p /root/.config/redpitaya/apps/spectrumpro_2/config.json.bak /root/.config/redpitaya/apps/spectrumpro_2/config.json` (con el DFT cerrado). Los logos subidos (`logo1.png`, `logo6.png`, `logo4.png`) son archivos nuevos y pueden quedar.

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
- La escala del waterfall en DFT (`spectrumpro/js/scope.js`) clona etiquetas del eje X del gráfico Flot y las reposiciona con `top` fijo. El valor original era `65px` (quedaba en el medio del canvas). Tras la reducción de tamaño el valor correcto es `188px` (180px de canvas + 8px de margen).
- Los bloques `root_plot` (flex: 1) y `root_waterfall` del DFT se dimensionan así: `root_plot` toma el espacio restante del viewport menos lo que ocupa `root_waterfall`. La altura visual del waterfall la controla el CSS de `.waterfall-holder` (210px por canal). La fórmula JS `220 × canales + 10` setea la altura del *contenedor* `root_waterfall` para que coincida con el contenido CSS y no haya overflow que cause scroll en el body.
- El filtro whitelist en `black_list_app.js` actúa dentro de `Desktop.filterApps()`, que corre después de asignar grupos a las apps pero antes de agregar los íconos de grupo al DOM. Por eso `System` y `Development` no son afectados por el filtro.

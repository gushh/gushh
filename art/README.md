# 🎨 art/ — el taller de pixel art

Todo el arte del perfil sale de acá. No hay imágenes dibujadas en un editor:
cada sprite, fuente y escena está definida como texto y se exporta a SVG.

```bash
python3 art/build.py      # regenera assets/*.svg y site/gen/ (solo stdlib)
pip install fonttools
python3 art/webfont.py    # convierte la fuente bitmap en un .woff para el sitio
```

| Archivo | Qué hace |
| :-- | :-- |
| `pixel.py` | Motor mínimo: capas de píxeles → SVG con `crispEdges`, un `<path>` por color. |
| `fonts.py` | Dos fuentes bitmap hechas a mano (5×7 y 3×5), con tildes y ñ. |
| `sprites.py` | elePHPant, el dev, ítems RPG, íconos y escenografía en ASCII. |
| `build.py` | Compone cada pieza (hero, botones, inventario, logros…) en versión clara y oscura. |
| `webfont.py` | Genera *Gus Pixel*, la fuente del sitio de GitHub Pages. |

## Cómo editar

- **Cambiar un dato:** los textos viven en `build.py` (`BUTTONS`, `SECTIONS`, `STACK`, `ACHIEVEMENTS`).
  Agregar una tecnología es sumar una tupla `("Nombre", "#color")` en `STACK`.
- **Dibujar:** en `sprites.py` cada carácter es un píxel (`.` = transparente) y la paleta se
  resuelve al dibujar, así un mismo sprite se recolorea (cada espada toma el color de su tecnología).
- **Animar:** las animaciones son CSS dentro del SVG, siempre con `steps()` para que todo
  se mueva de a un píxel. `prefers-reduced-motion` las apaga.

Todo se dibuja en una grilla de 280 px y se exporta a 3×, así el README muestra el mismo
tamaño de píxel en todas las imágenes.

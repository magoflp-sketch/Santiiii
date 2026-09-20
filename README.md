# Regalos

Dos páginas HTML interactivas, cada una un regalo para alguien. Sin build y sin
dependencias: se abre el archivo en cualquier navegador (pensadas primero para
celular) y listo.

- `index.html` — **El EP del Gordo**, para Santy Casinelli.
- `sofi.html` — **Carta para Sofi**, de parte de Lola y Mago.

---

# El EP del Gordo (`index.html`)

Regalo de cumpleaños interactivo para Santy Casinelli.

## Qué es

Una experiencia de ocho "candados" que hay que abrir para llegar al regalo real
— la producción completa de tres temas, un EP. Cada acto es una interacción
distinta:

| Acto | Interacción |
|---|---|
| I | Terminal que tipea sola y busca el regalo del año pasado |
| II | Botón de reclamo que se escapa del dedo |
| III | Cronología de excusas con scroll horizontal |
| IV | Test psicotécnico de cuatro preguntas |
| V | Fader con fuga + perilla giratoria, ambos al máximo |
| VI | Mantener apretado hasta renderizar el 100% |
| VII | Tres tarjetas de tema que se dan vuelta en 3D |
| VIII | Contrato que se firma con el dedo sobre un canvas |

Al completar los ocho se abre la bóveda: certificado, detalle de lo que incluye
el regalo y la carta.

## Detalles técnicos

- HTML + CSS + JS vanilla en un solo archivo.
- Tipografías: Bungee, Syne y Space Mono (Google Fonts).
- Sonido sintetizado con Web Audio API — sin archivos de audio.
- Papelitos y firma con Canvas 2D; sin librerías externas.
- Todas las interacciones usan Pointer Events, así que funcionan igual con dedo,
  mouse o teclado.
- El progreso se guarda en `localStorage` y respeta `prefers-reduced-motion`.

---

# Carta para Sofi (`sofi.html`)

Una carta de Lola y Mago para Sofi. No hay chiste ni ocasión: el único mensaje es
que la quieren con todo el corazón y que la quieren acompañar en todo lo que ella
elija. El tono es el opuesto al del regalo de Santy — cálido, tranquilo y luminoso.

## Qué es

Cinco momentos para tocar antes de llegar a la carta final:

| Paso | Interacción |
|---|---|
| 1 | Un sobre que se abre arrastrando la solapa hacia abajo |
| 2 | Doce luces que flotan en un cielo; al encenderlas todas se acomodan en un corazón |
| 3 | Seis promesas en un carrusel horizontal, la última en blanco a propósito |
| 4 | Un corazón que hay que mantener apretado hasta llenarlo, latido a latido |
| 5 | Una cajita con veintidós notas sueltas que se saca al azar y no se acaba |

Al completar los cinco aparece la carta, la firma escrita a mano y los pétalos.

## Detalles técnicos

- HTML + CSS + JS vanilla en un solo archivo.
- Tipografías: Fraunces (con ejes `SOFT` y `WONK`), Karla y Caveat.
- Constelación, motas de luz y pétalos en Canvas 2D, sin librerías.
- Campanitas en escala pentatónica con Web Audio API — sin archivos de audio.
- Pointer Events en todo, así que anda igual con dedo, mouse o teclado.
- Progreso en `localStorage` y `prefers-reduced-motion` respetado.

# El EP del Gordo

Regalo de cumpleaños interactivo para Santy Casinelli.

Una sola página HTML, sin build y sin dependencias: se abre `index.html` en
cualquier navegador (pensada primero para celular) y listo.

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

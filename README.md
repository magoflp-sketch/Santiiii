# Regalos

Tres páginas HTML interactivas, cada una un regalo para alguien. Sin build y sin
dependencias: se abre el archivo en cualquier navegador (pensadas primero para
celular) y listo.

- `index.html` — **El EP del Gordo**, para Santy Casinelli.
- `sofi.html` — **Carta para Sofi**, de parte de Lola y Mago.
- `kala.html` — **Kalalandia**, para Kala.

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

---

# Kalalandia (`kala.html`)

Regalo para Kala: la producción completa de un tema. Pero la página no lo dice:
al principio es solo un parque de diversiones privado, con una sola visitante, y
cinco juegos de feria. El regalo aparece recién al raspar la tarjeta final, y
ahí se revela el truco: los juegos eran la ficha del tema disfrazada (la
canción que no se saca de la cabeza es la referencia, la frase de la
tragamonedas es el estribillo, la comida es el rider). Los textos están
escritos como Mago hablándole por un altavoz, en tono de chat, y el altavoz a
veces se equivoca al tipear y se corrige solo.

## Qué es

Una ficha de admisión, cinco juegos en cualquier orden y una raspadita final:

| Parte | Interacción |
|---|---|
| Boletería | Ficha (nombre, comida, canción que no se saca de la cabeza, nivel de diva); imprime un ticket que se arranca tirando de la parte roja |
| El Kala-sino | Tragamonedas de frases absurdas; arranca "fuera de servicio" y hay que pegarle tres veces |
| La Grúa | Máquina de peluches en canvas; la garra falla a propósito hasta que se apiada, y el premio es la copa de oro |
| Topos | Aplastar excusas en 30 segundos sin pegarle a "tu risa"; baja la exigencia si fallás |
| La Rueda | Sorteo de la música de la fiesta; la primera tirada es siempre QUIEBRA y cada género suena unos segundos |
| La Consola | Cuatro perillas en su franja verde; "vos" pedís más volumen y la perilla no se deja bajar |
| Premio mayor | Raspadita de verdad en canvas que revela la producción completa |

Al raspar se hace de noche y aparecen el certificado, la explicación del truco,
un teaser sonoro en el género que tocó, la **ficha del tema** (para sacarle
captura y mandarla), un vale para juntarse cuando ella quiera (o irse a Mar Azul
a hacer un tema) y la carta. El género sorteado es solo un chiste: el de verdad
lo elige ella. Hay 15 figuritas para coleccionar (las repetidas no se cambian) y
algunos secretos: tocar las letras del cartel, tocar el nombre del ticket,
escribir "kala".

## Detalles técnicos

- HTML + CSS + JS vanilla en un solo archivo, sin librerías. A diferencia de los otros dos,
  este es un documento completo (doctype, vista previa para WhatsApp, `noindex`), así que
  se puede publicar tal cual en cualquier hosting estático.
- Tipografías: Bagel Fat One, Bricolage Grotesque y DM Mono (Google Fonts).
- Todo el sonido está sintetizado con Web Audio API: efectos, música de calesita,
  ocho géneros para el teaser (con un "KA-LA" cantado por formantes) y visualizador.
  Cero archivos de audio.
- Canvas 2D para la grúa, la rueda, la raspadita, el confeti y las estrellas.
- El altavoz puede leer en voz alta con `speechSynthesis` si el navegador lo trae
  (botón del globito, apagado por defecto).
- Pointer Events y teclado; funciona en celular y escritorio. Progreso y sonido
  en `localStorage`; respeta `prefers-reduced-motion`.

## Personalizarlo

Arriba de todo en el `<script>` está `CONFIG`: quién regala (`from`), el nombre por
defecto de la visitante (`guest`), los párrafos de la carta (`letter`) y la firma.


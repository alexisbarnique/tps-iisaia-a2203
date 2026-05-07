# Registro de Proceso: prompts.md

Este documento detalla la secuencia de interacción con la IA para la creación del artefacto.

### Prompt 1: Definición de la Base y Estructura
**Prompt:** > "Actúa como un desarrollador de videojuegos frontend y un experto en "Evil UX" (Interfaces Hostiles). Mi objetivo es cumplir con un desafío técnico de crear un artefacto funcional en un "single-file".

El Concepto:
Necesito que generes un único archivo index.html que contenga un minijuego web llamado "Atrapa la Snitch: Chaos Edition". El objetivo del jugador es simple: hacer clic en una "Snitch Dorada" que se mueve por la pantalla para ganar puntos. Sin embargo, el juego debe estar diseñado para ser frustrante y poner a prueba la paciencia del jugador.

Constraints Técnicos (Innegociables):

    Un solo archivo: Todo (HTML, CSS y JS) debe estar dentro de index.html.

    Cero dependencias externas: Nada de Phaser, React, ni librerías de físicas. Todo debe ser Vanilla JS y el renderizado puede usar el DOM o <canvas>.

    Cero activos externos: No puedes cargar imágenes ni fuentes externas. La "Snitch" debe ser dibujada usando SVG embebido, CSS puro o caracteres ASCII.

Mecánicas del "Caos" (Instrucciones para la v1):

    Movimiento errático: La Snitch debe moverse usando requestAnimationFrame rebotando por los bordes, pero debe acelerar drásticamente cuando el cursor del mouse se acerque a ella.

    Falsos positivos: Cada 3 clics fallidos, la pantalla debe temblar ligeramente (efecto CSS).

    El marcador hostil: El contador de "Puntos" debe ocasionalmente restar un punto sin motivo o cambiar de lugar en la pantalla.

Crea la estructura inicial, el diseño visual (fondo de cielo oscuro, la Snitch dorada con pequeñas alas SVG) y el loop principal del juego."

**Anotación:** El objetivo era establecer el boilerplate técnico y verificar que la IA respetara la restricción de un solo archivo y el movimiento básico por proximidad. También se intenta que la IA maneje múltiples estados de animación simultáneos en Vanilla JS.

### Prompt 2: Mejorar el aspecto del cursor
**Prompt:**
> "Al cursor le hace falta que visualmente este ambientado en el mundo Harry Potter o del quiditch. La idea es que permanezca todo en el mismo archivo index.html"

**Anotación:** Ya que está basado en el universo de Harry Potter, el cursor también debe respetar ese aspecto.

### Prompt 3: Ambiente Quidditch más inmersivo
**Prompt:**
> "Para recrear un ambiente de Quidditch más inmersivo puedes agregar: sonido de viento, crowd ambience y  pitch wobble al acercarte a la Snitch, música que acelera cuando el mouse se acerca. Todo sin romper el requisito de single-file y generando el nuevo index.html con esta modificación"

**Anotación:** **Para agregarle más molestia al juego.** Con esto se hacer más inspportable jugarlo.


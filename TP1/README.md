# Atrapa la Snitch: Chaos Edition ⚡️🏆

## Descripción
Este es un artefacto experimental de "Evil UX" diseñado para poner a prueba la resiliencia del usuario. A través de un minijuego basado en el universo de Harry Potter, el objetivo es atrapar la Snitch Dorada. Sin embargo, la interfaz está programada para ser hostil, errática y psicológicamente agotadora.

El proyecto explora el concepto de **caos y resiliencia** en sistemas interactivos, transformando errores comunes de usabilidad en mecánicas de juego deliberadas.

Y ya que soy potterhead... porque no hacerlo de ese motivo. "Juro solemnemente que mis intenciones no son buenas."

## Autor
**Alexis Barniquez** Ingeniera de Sistemas | Especialista en IA

## Características Técnicas
- **Single-file:** Todo el sistema reside en un único archivo `index.html`.
- **Vanilla Tech:** Construido exclusivamente con HTML5, CSS3 y JavaScript puro.
- **Cero Dependencias:** Sin librerías externas, CDNs ni activos locales. Los gráficos de la Snitch están generados mediante SVG embebido.
- **Motor de Caos:** Implementación de lógica de huida mediante vectores y eventos de proximidad.

## Qué funcionó y qué no
### Lo que funcionó:
- La lógica de evasión de la Snitch resultó ser altamente efectiva; el uso de `requestAnimationFrame` permite una fluidez que realmente "tortura" al jugador.
- El sistema de "falsos positivos" en el marcador genera el nivel de frustración deseado para el experimento.
- El diseño visual se mantiene profesional y minimalista a pesar de las restricciones de no usar archivos externos.

### Retos y limitaciones:
- La detección de colisiones (hitbox) en dispositivos táctiles fue un reto sin usar librerías de físicas, por lo que se optimizó para puntero (mouse).
- Mantener la legibilidad del código en un solo archivo de más de 300 líneas requiere una organización estricta de funciones.

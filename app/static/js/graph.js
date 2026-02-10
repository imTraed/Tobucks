document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('graph');
  if (!container) return;

  fetch('/recommendations/graph.json')
    .then((response) => response.json())
    .then((data) => {
      if (!data || !data.nodes || !data.links) {
        return;
      }
      
      const width = container.clientWidth;
      const height = container.clientHeight;
      const cx = width / 2;
      const cy = height / 2;

      // ============================================================
      // 1. PREPARACIÓN DE DATOS PARA EL EFECTO FLOTANTE
      // ============================================================
      // Asignamos a cada nodo valores aleatorios para su movimiento único
      data.nodes.forEach(d => {
        // Velocidad: qué tan rápido "flota" (muy lento para ser elegante)
        d.floatSpeed = (Math.random() * 0.001) + 0.0005; 
        // Fase: para que no todos se muevan al mismo tiempo (desincronizados)
        d.floatPhase = Math.random() * Math.PI * 2;
        // Radio: qué tan lejos se mueve de su centro (5px a 15px)
        d.floatRadius = 5 + Math.random() * 10; 
      });

      // SVG
      const svg = d3.select('#graph').append('svg')
        .attr('width', width)
        .attr('height', height)
        .style('background-color', '#1a1a1a');

      // Fondo
      svg.append('image')
        .attr('href', 'https://images.unsplash.com/photo-1475274047050-1d0c0975c63e?fm=jpg&q=60&w=3000')
        .attr('width', '100%').attr('height', '100%')
        .attr('preserveAspectRatio', 'xMidYMid slice')
        .style('opacity', 0.5);

      const g = svg.append('g');

      // ============================================================
      // 2. FÍSICA ESTRUCTURAL
      // ============================================================
      
      const simulation = d3.forceSimulation(data.nodes)
        .force('link', d3.forceLink(data.links).id(d => d.id).distance(130).strength(0.05))
        .force('charge', d3.forceManyBody().strength(-450))
        // Radios de colisión amplios para mantener la separación
        .force('collide', d3.forceCollide().radius(d => {
            if (d.type === 'user') return 90;
            if (d.type === 'genre') return 65;
            return 90; 
        }).iterations(3))
        // Estructura de anillos
        .force('radial', d3.forceRadial(d => {
            if (d.type === 'user') return 0;
            if (d.type === 'genre') return 220; 
            return 450;
        }, cx, cy).strength(0.8));

      // ============================================================
      // 3. DIBUJO DE ELEMENTOS
      // ============================================================

      const link = g.append('g')
        .selectAll('line')
        .data(data.links)
        .enter().append('line')
        .attr('stroke', '#a6c1ee')
        .attr('stroke-width', 0.5)
        .attr('stroke-opacity', 0.65);

      const node = g.append('g')
        .selectAll('.node')
        .data(data.nodes)
        .enter().append('g')
        .attr('class', 'node')
        .call(d3.drag()
            .on('start', (event, d) => {
                // Al arrastrar, "calentamos" la simulación
                if (!event.active) simulation.alphaTarget(0.3).restart();
                d.fx = d.x; d.fy = d.y;
            })
            .on('drag', (event, d) => { d.fx = event.x; d.fy = event.y; })
            .on('end', (event, d) => {
                // Al soltar, volvemos al modo flotante perpetuo (alpha 0.01)
                if (!event.active) simulation.alphaTarget(0.01); 
                d.fx = null; d.fy = null;
            }));

      // --- Estilos Visuales (Glow y Tamaños) ---
      
      // Usuario
      node.filter(d => d.type === 'user')
        .append('circle')
        .attr('r', 45)
        .attr('fill', '#FFD700')
        .attr('stroke', '#fff')
        .attr('stroke-width', 3)
        .style('filter', 'drop-shadow(0 0 8px rgba(255, 215, 0, 0.8))');

      // Géneros
      node.filter(d => d.type === 'genre')
        .append('circle')
        .attr('r', 38)
        .attr('fill', '#1a1a1a')
        .attr('stroke', '#ffffff')
        .attr('stroke-width', 2)
        .style('filter', 'drop-shadow(0 0 6px rgba(255, 255, 255, 0.6))');

      // Películas
      const movieNodes = node.filter(d => d.type === 'movie');
      movieNodes.append('rect')
        .attr('x', -22).attr('y', -32)
        .attr('width', 44).attr('height', 64)
        .attr('fill', '#000')
        .attr('stroke', '#fff')
        .attr('stroke-width', 2)
        .style('filter', 'drop-shadow(0 0 6px rgba(255, 255, 255, 0.8))');

      movieNodes.append('image')
        .attr('href', d => d.poster ? `/static/${d.poster}` : '')
        .attr('x', -20).attr('y', -30)
        .attr('width', 40).attr('height', 60)
        .attr('preserveAspectRatio', 'none');

      // --- Etiquetas ---
      node.filter(d => d.type === 'user')
        .append('text').text("YO").attr('dy', '0.35em').attr('text-anchor', 'middle')
        .style('font-weight', 'bold').style('font-size', '16px').style('fill', '#000');

      node.filter(d => d.type === 'genre')
        .append('text').text(d => d.label).attr('dy', '0.35em').attr('text-anchor', 'middle')
        .style('fill', '#ffffff').style('font-size', '12px').style('font-weight', 'bold')
        .style('text-shadow', '0 1px 3px #000');

      movieNodes.append('text')
        .text(d => d.label.length > 15 ? d.label.substring(0, 12) + '...' : d.label)
        .attr('dy', 50).attr('text-anchor', 'middle')
        .style('fill', '#ddd').style('font-size', '9px').style('text-shadow', '0 0 3px #000')
        .style('opacity', 0.9);

      // ============================================================
      // 4. EL MOTOR DE MOVIMIENTO "FLOTANTE"
      // ============================================================

      // Esta función se ejecuta en cada frame
      simulation.on('tick', () => {
        const now = Date.now(); // Tiempo actual en milisegundos

        // Calculamos la posición visual (física + flotación)
        data.nodes.forEach(d => {
            // Usamos Seno y Coseno para crear un movimiento circular suave e infinito
            // d.x es la posición física (estructura)
            // Math.cos(...) es el desplazamiento flotante
            d.visualX = d.x + Math.cos(now * d.floatSpeed + d.floatPhase) * d.floatRadius;
            d.visualY = d.y + Math.sin(now * d.floatSpeed + d.floatPhase) * d.floatRadius;
        });

        // Actualizamos las LÍNEAS usando las coordenadas visuales
        link
          .attr('x1', d => d.source.visualX)
          .attr('y1', d => d.source.visualY)
          .attr('x2', d => d.target.visualX)
          .attr('y2', d => d.target.visualY);

        // Actualizamos los NODOS usando las coordenadas visuales
        node.attr('transform', d => `translate(${d.visualX},${d.visualY})`);
      });

      const zoom = d3.zoom().on('zoom', e => g.attr('transform', e.transform));
      svg.call(zoom);

      const initialScale = 0.7;
      svg.call(zoom.transform, d3.zoomIdentity
        .translate(width/2, height/2)
        .scale(initialScale)
        .translate(-cx, -cy));
      
      // ESTO ES CLAVE: Mantiene la simulación corriendo "suavemente" para siempre
      // AlphaTarget > 0 impide que la simulación se "duerma"
      simulation.alphaTarget(0.01).restart();
    });
});
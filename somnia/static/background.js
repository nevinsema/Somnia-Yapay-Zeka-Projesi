const canvas = document.getElementById("background-stars");
if (canvas) {
  const ctx = canvas.getContext("2d");

  function resize() {
    canvas.width = window.innerWidth;
    canvas.height = window.innerHeight;
  }
  window.addEventListener("resize", resize);
  resize();

  const N = 70;
  const nodes = [];
  for (let i = 0; i < N; i++) {
    nodes.push({
      x: Math.random() * canvas.width,
      y: Math.random() * canvas.height,
      vx: (Math.random() - 0.5) * 0.3,
      vy: (Math.random() - 0.5) * 0.3
    });
  }

  function step() {
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    // Çizgiler
    for (let i = 0; i < N; i++) {
      for (let j = i + 1; j < N; j++) {
        const dx = nodes[i].x - nodes[j].x;
        const dy = nodes[i].y - nodes[j].y;
        const dist = Math.sqrt(dx * dx + dy * dy);
        if (dist < 140) {
          const alpha = 1 - dist / 140;
          ctx.strokeStyle = `rgba(0,255,220,${alpha * 0.25})`;
          ctx.lineWidth = 1;
          ctx.beginPath();
          ctx.moveTo(nodes[i].x, nodes[i].y);
          ctx.lineTo(nodes[j].x, nodes[j].y);
          ctx.stroke();
        }
      }
    }

    // Noktalar
    for (const n of nodes) {
      ctx.fillStyle = "rgba(151, 255, 255, 0.9)";
      ctx.beginPath();
      ctx.arc(n.x, n.y, 2, 0, Math.PI * 2);
      ctx.fill();

      n.x += n.vx;
      n.y += n.vy;

      if (n.x < 0) n.x = canvas.width;
      if (n.x > canvas.width) n.x = 0;
      if (n.y < 0) n.y = canvas.height;
      if (n.y > canvas.height) n.y = 0;
    }

    requestAnimationFrame(step);
  }

  step();
}

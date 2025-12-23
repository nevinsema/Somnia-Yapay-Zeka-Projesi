// === SOMNIA INDEX PAGE - MOON RIPPLE BACKGROUND ===

document.addEventListener("DOMContentLoaded", () => {
    const canvas = document.createElement("canvas");
    canvas.id = "moonRippleCanvas";
    canvas.style.position = "fixed";
    canvas.style.top = 0;
    canvas.style.left = 0;
    canvas.style.width = "100%";
    canvas.style.height = "100%";
    canvas.style.pointerEvents = "none";
    canvas.style.zIndex = "-1";

    document.body.appendChild(canvas);
    const ctx = canvas.getContext("2d");

    function resize() {
        canvas.width = window.innerWidth;
        canvas.height = window.innerHeight;
    }
    resize();
    window.addEventListener("resize", resize);

    let ripples = [];

    function createRipple() {
        // ripple bir noktadan expand ediyor
        const x = canvas.width * 0.5;
        const y = canvas.height * 0.45;

        ripples.push({
            x,
            y,
            r: 0,
            alpha: 0.25,
        });
    }

    setInterval(createRipple, 2200); // 2.2s'de bir yeni dalga

    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        ripples.forEach((rp, i) => {
            ctx.beginPath();
            ctx.arc(rp.x, rp.y, rp.r, 0, Math.PI * 2);

            // Neon moon ripple gradient (Turkuaz-Mor-Pembe)
            const g = ctx.createRadialGradient(rp.x, rp.y, rp.r * 0.2, rp.x, rp.y, rp.r);
            g.addColorStop(0, `rgba(103, 249, 255, ${rp.alpha})`); // turkuaz
            g.addColorStop(0.5, `rgba(192, 155, 255, ${rp.alpha * 0.6})`); // mor
            g.addColorStop(1, `rgba(255, 124, 181, 0)`); // pembe fade out
            ctx.fillStyle = g;
            ctx.fill();

            rp.r += 0.45; // expansion speed
            rp.alpha *= 0.985; // fade out
            if (rp.alpha < 0.01) ripples.splice(i, 1);
        });

        requestAnimationFrame(draw);
    }

    draw();
});

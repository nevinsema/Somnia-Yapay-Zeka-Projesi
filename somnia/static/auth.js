// === SOMNIA AUTH PAGES - DREAM GLOW + FLOATING DUST ===

document.addEventListener("DOMContentLoaded", () => {
    // Bu script sadece login ve register sayfalarında çalışsın
    const pageTitle = document.querySelector("h1");
    if (!pageTitle) return;
    const titleText = pageTitle.textContent.toLowerCase();
    if (!(titleText.includes("giriş") || titleText.includes("kayıt"))) return;

    // ===== CANVAS OLUŞTUR =====
    const canvas = document.createElement("canvas");
    canvas.id = "dreamDustCanvas";
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

    // ===== DREAM DUST =====
    let dust = [];
    const COUNT = 50;

    function createDust() {
        for (let i = 0; i < COUNT; i++) {
            dust.push({
                x: Math.random() * canvas.width,
                y: Math.random() * canvas.height,
                r: Math.random() * 2.2 + 0.6,
                s: Math.random() * 0.7 + 0.2,
                a: Math.random() * 0.4 + 0.2
            });
        }
    }
    createDust();

    // ===== DREAM GLOW PULSE =====
    function applyGlow() {
        document.querySelector(".container").style.boxShadow =
            `0 0 18px rgba(103,249,255,0.35),
             0 0 25px rgba(192,155,255,0.18),
             0 0 35px rgba(255,124,181,0.12)`;

        document.querySelector(".container").animate([
            { boxShadow: "0 0 15px rgba(103,249,255,0.18)" },
            { boxShadow: "0 0 30px rgba(255,124,181,0.25)" },
            { boxShadow: "0 0 18px rgba(103,249,255,0.35)" }
        ], {
            duration: 5000,
            iterations: Infinity
        });
    }
    applyGlow();

    // ===== DRAW =====
    function draw() {
        ctx.clearRect(0, 0, canvas.width, canvas.height);

        dust.forEach(d => {
            ctx.beginPath();
            const g = ctx.createRadialGradient(d.x, d.y, 0, d.x, d.y, d.r * 3);
            g.addColorStop(0, `rgba(103,249,255,${d.a})`);
            g.addColorStop(0.5, `rgba(192,155,255,${d.a * 0.5})`);
            g.addColorStop(1, "rgba(255,124,181,0)");
            ctx.fillStyle = g;
            ctx.arc(d.x, d.y, d.r * 3, 0, Math.PI * 2);
            ctx.fill();

            d.y -= d.s * 0.8;
            if (d.y < 0) d.y = canvas.height + 10;
        });

        requestAnimationFrame(draw);
    }

    draw();
});

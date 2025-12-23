fetch("/api/data")
  .then(res => res.json())
  .then(data => {
    if (!data || data.length === 0) return;

    const labels = data.map(r => r[0]);        // date
    const durations = data.map(r => r[4]);     // sleep_minutes
    const predicted = data.map(r => r[5]);     // predicted
    const target = data.map(r => r[6]);        // target
    const o2 = data.map(r => r[10]);
    const noise = data.map(r => r[11]);
    const temp = data.map(r => r[12]);
    const light = data.map(r => r[13]);

    const ctx1 = document.getElementById("sleepDurationChart");
    new Chart(ctx1, {
      type: "line",
      data: {
        labels,
        datasets: [{
          label: "Uyku süresi (dk)",
          data: durations,
          borderColor: "#4bfdf6",
          backgroundColor: "rgba(75,253,246,0.2)",
          borderWidth: 3,
          tension: 0.4,
          pointRadius: 3
        }]
      },
      options: { responsive: true }
    });

    const ctx2 = document.getElementById("scoreChart");
    new Chart(ctx2, {
      type: "line",
      data: {
        labels,
        datasets: [
          {
            label: "Model tahmini",
            data: predicted,
            borderColor: "#ffca3a",
            backgroundColor: "rgba(255,202,58,0.2)",
            borderWidth: 3,
            tension: 0.4
          },
          {
            label: "Kullanıcı hissi",
            data: target,
            borderColor: "#ff595e",
            backgroundColor: "rgba(255,89,94,0.2)",
            borderWidth: 3,
            tension: 0.4
          }
        ]
      },
      options: { responsive: true }
    });

      });

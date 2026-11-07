function renderMonthlyChart(elementId, rows) {
  const canvas = document.getElementById(elementId);
  if (!canvas || !rows.length) return;
  new Chart(canvas, {
    type: 'bar',
    data: {
      labels: rows.map(row => row.month_label),
      datasets: [
        { label: 'Income', data: rows.map(row => row.income), backgroundColor: '#2eaa83', borderRadius: 5 },
        { label: 'Expenses', data: rows.map(row => row.expenses), backgroundColor: '#6682e8', borderRadius: 5 }
      ]
    },
    options: { responsive: true, maintainAspectRatio: false,
      plugins: { legend: { position: 'bottom' } },
      scales: { y: { beginAtZero: true, ticks: { callback: value => '₹' + value.toLocaleString('en-IN') } } }
    }
  });
}
function renderCategoryChart(elementId, rows) {
  const canvas = document.getElementById(elementId);
  if (!canvas || !rows.length) return;
  new Chart(canvas, {
    type: 'doughnut',
    data: {
      labels: rows.map(row => row.category),
      datasets: [{ data: rows.map(row => row.amount),
        backgroundColor: ['#3659d9','#2eaa83','#f2a541','#d96b79','#7b69c7','#55a9bd','#9aa8b8','#d38ab2'] }]
    },
    options: { responsive: true, maintainAspectRatio: false, plugins: { legend: { position: 'bottom' } } }
  });
}

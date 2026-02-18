// Load data
const user = JSON.parse(localStorage.getItem("user"));
const transactions = JSON.parse(localStorage.getItem("transactions")) || [];
const budgets = JSON.parse(localStorage.getItem("budgets")) || [];
const categories = JSON.parse(localStorage.getItem("categories")) || [];

// User name
if (user) {
  document.getElementById("userName").textContent = "👤 " + user.name;
}

// Totals
let income = 0;
let expenses = 0;

transactions.forEach(t => {
  if (t.type === "income") income += t.amount;
  if (t.type === "expense") expenses += t.amount;
});

const balance = income - expenses;

// Update cards
document.getElementById("totalIncome").textContent = "PKR " + income;
document.getElementById("totalExpenses").textContent = "PKR " + expenses;
document.getElementById("balance").textContent = "PKR " + balance;

// Recent transactions (last 5)
const recent = transactions.slice(-5).reverse();
const tbody = document.getElementById("recentTransactions");

recent.forEach(t => {
  const cat = categories.find(c => c.id === t.category_id);
  const row = `
    <tr>
      <td>${t.date}</td>
      <td>${cat ? cat.name : ""}</td>
      <td>${t.type}</td>
      <td>${t.amount}</td>
    </tr>`;
  tbody.innerHTML += row;
});

// Category totals for chart
const categoryTotals = {};

transactions.forEach(t => {
  if (t.type === "expense") {
    categoryTotals[t.category_id] =
      (categoryTotals[t.category_id] || 0) + t.amount;
  }
});

const labels = [];
const data = [];

for (let id in categoryTotals) {
  const cat = categories.find(c => c.id === id);
  labels.push(cat ? cat.name : "Other");
  data.push(categoryTotals[id]);
}

// Chart
const ctx = document.getElementById("pieChart");

new Chart(ctx, {
  type: "pie",
  data: {
    labels: labels,
    datasets: [{ data: data }]
  }
});

// Budget
const currentMonth = new Date().toISOString().slice(0,7);
const monthBudget = budgets.find(b => b.month === currentMonth && !b.category_id);

if (monthBudget) {
  const limit = monthBudget.limit_amount;
  const percent = Math.min((expenses / limit) * 100, 100);

  document.getElementById("budgetText").textContent =
    `PKR ${expenses} / ${limit}`;

  document.getElementById("budgetBar").style.width = percent + "%";
}
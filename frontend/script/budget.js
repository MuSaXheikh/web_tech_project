const form = document.getElementById("budgetForm");
const table = document.getElementById("budgetTable");

let budgets = JSON.parse(localStorage.getItem("budgets")) || [];
const user = JSON.parse(localStorage.getItem("user"));

// Render budgets
function renderBudgets() {
  table.innerHTML = "";

  budgets.forEach((b, index) => {
    const row = `
      <tr>
        <td>${b.month}</td>
        <td>${b.limit_amount}</td>
        <td><span class="delete-btn" onclick="deleteBudget(${index})">Delete</span></td>
      </tr>
    `;
    table.innerHTML += row;
  });
}

// Save
form.addEventListener("submit", e => {
  e.preventDefault();

  const month = document.getElementById("month").value;
  const amount = Number(document.getElementById("amount").value);

  // Update if exists
  const existing = budgets.find(b => b.month === month && !b.category_id);

  if (existing) {
    existing.limit_amount = amount;
  } else {
    budgets.push({
      id: "b" + Date.now(),
      user_id: user ? user.id : "u1",
      month: month,
      category_id: null,
      limit_amount: amount,
      created_at: new Date().toISOString()
    });
  }

  localStorage.setItem("budgets", JSON.stringify(budgets));
  form.reset();
  renderBudgets();
});

// Delete
function deleteBudget(index) {
  if (!confirm("Delete this budget?")) return;

  budgets.splice(index, 1);
  localStorage.setItem("budgets", JSON.stringify(budgets));
  renderBudgets();
}

renderBudgets();
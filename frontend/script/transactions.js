const transactions = JSON.parse(localStorage.getItem("transactions")) || [];
const categories = JSON.parse(localStorage.getItem("categories")) || [];

const table = document.getElementById("transactionTable");

// Render transactions
function renderTransactions() {
  table.innerHTML = "";

  transactions.forEach((t, index) => {
    const cat = categories.find(c => c.id === t.category_id);

    const row = `
      <tr>
        <td>${t.date}</td>
        <td>${cat ? cat.name : ""}</td>
        <td>${t.type}</td>
        <td>${t.account}</td>
        <td>${t.amount}</td>
        <td><span class="delete-btn" onclick="deleteTransaction(${index})">Delete</span></td>
      </tr>
    `;

    table.innerHTML += row;
  });
}

// Delete
function deleteTransaction(index) {
  if (!confirm("Delete this transaction?")) return;

  transactions.splice(index, 1);
  localStorage.setItem("transactions", JSON.stringify(transactions));
  renderTransactions();
}

renderTransactions();
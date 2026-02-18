const form = document.getElementById("transactionForm");

const categories = JSON.parse(localStorage.getItem("categories")) || [];
const transactions = JSON.parse(localStorage.getItem("transactions")) || [];
const user = JSON.parse(localStorage.getItem("user"));

const categorySelect = document.getElementById("category");

// Populate categories
categories.forEach(c => {
  const option = document.createElement("option");
  option.value = c.id;
  option.textContent = c.name;
  categorySelect.appendChild(option);
});

// Submit
form.addEventListener("submit", e => {
  e.preventDefault();

  const newTransaction = {
    id: "t" + Date.now(),
    user_id: user ? user.id : "u1",
    amount: Number(document.getElementById("amount").value),
    type: document.getElementById("type").value,
    category_id: document.getElementById("category").value,
    account: document.getElementById("account").value,
    date: document.getElementById("date").value,
    description: document.getElementById("description").value,
    created_at: new Date().toISOString(),
    updated_at: new Date().toISOString()
  };

  transactions.push(newTransaction);
  localStorage.setItem("transactions", JSON.stringify(transactions));

  window.location.href = "transactions.html";
});
const express = require("express");
const path = require("path");
const app = express();

app.use(express.json());

// Load static JSON
const deal1000 = require("./data/json1.json");
const deal2000 = require("./data/json2.json");
const deal3000 = require("./data/json3.json");

// Map customer_id to deal data
// customer_id 1 → json1.json (CompanyABC)
// customer_id 2 → json2.json (TechCorp Solutions)
// customer_id 3 → json3.json (Global Logistics Inc)
const customerToDealMap = {
  1: deal1000,
  2: deal2000,
  3: deal3000
};

// ✅ Main endpoint: Get deal by customer ID
app.get("/api/getdeal/customer/:customer_id", (req, res) => {
  const customerId = parseInt(req.params.customer_id);
  
  if (isNaN(customerId)) {
    return res.status(400).json({ error: "Invalid customer_id. Must be a number." });
  }
  
  const deal = customerToDealMap[customerId];
  
  if (!deal) {
    return res.status(404).json({ 
      error: `No deal found for customer_id: ${customerId}`,
      available_customer_ids: Object.keys(customerToDealMap).map(Number)
    });
  }
  
  res.json(deal);
});

// ✅ Legacy endpoints (kept for backward compatibility)
app.get("/api/getdeal/1000", (req, res) => {
  res.json(deal1000);
});

app.get("/api/getdeal/2000", (req, res) => {
  res.json(deal2000);
});

app.get("/api/getdeal/3000", (req, res) => {
  res.json(deal3000);
});

// 404 fallback
app.use((req, res) => {
  res.status(404).json({ error: "Route not found" });
});

const PORT = 3000;

app.listen(PORT, () => {
  console.log(`Mock API running on port ${PORT}`);
});
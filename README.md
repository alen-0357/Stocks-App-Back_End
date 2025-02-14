# Stock Backend API

### Repository Description:
A robust backend service built with Flask to manage and analyze stock transactions. It provides APIs for fetching full transaction reports, profit/loss summaries, and user-specific stock insights.

### README Content:
## 📊 Stock Backend API
A backend service for managing and analyzing stock transactions, offering detailed reports and profit/loss summaries.

### 🚀 Features:
- **Transaction Reports:** View aggregated buy/sell transactions by date.
- **Profit/Loss Analysis:** Retrieve daily profit or loss percentages.
- **User Authentication:** Secure endpoints with user-based access.

### 🛠️ Tech Stack:
- **Backend:** Flask, Python
- **Database:** Firebase Firestore
- **Tools:** Axios, date-fns

### 📥 Installation:
```bash
# Clone repository
git clone https://github.com/username/stock-backend.git
cd stock-backend

# Install dependencies
pip install -r requirements.txt
```

### 🏃 Usage:
```bash
# Run server
python app.py
```

### 📑 Example API Endpoint:
- `/fullstockstransactionsreport?stock_id=<id>` – Get aggregated transactions.
- `/getprofitperdayreport?stock_id=<id>` – Retrieve daily profit/loss.

### 📝 Contribution:
Contributions are welcome! Feel free to open issues or pull requests.

### 📄 License:
This project is licensed under the MIT License.



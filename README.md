# Stocks Backend API - README

## Introduction
This backend API provides endpoints to retrieve and analyze stock transaction reports, including profit/loss calculations and aggregated transactions data. The backend is built with Flask and integrates with a database to store and manage stock records.

## Features
- Fetch full stock transactions report (buy/sell records).
- Retrieve daily profit/loss percentages.
- Aggregate transactions by date.
- Secure authentication using user-specific headers.

## Requirements
- Python 3.10+
- Flask
- Flask-CORS
- Date-fns (for date formatting on frontend)
- Axios (for frontend API requests)

## Installation
1. Clone the repository:
   ```bash
   git clone https://github.com/yourusername/stocks-backend.git
   ```
2. Navigate to the project directory:
   ```bash
   cd stocks-backend
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Running the Server
```bash
python app.py
```
The server will run at `http://127.0.0.1:5000` by default.

## API Endpoints
### 1. Full Stock Transactions Report
**Endpoint:** `/fullstockstransactionsreport`  
**Method:** `GET`  
**Parameters:**  
- `stock_id` (query parameter, required)
**Headers:**  
- `Authorization` (user-specific ID)

### 2. Daily Profit/Loss Report
**Endpoint:** `/getprofitperdayreport`  
**Method:** `GET`  
**Parameters:**  
- `stock_id` (query parameter, required)
**Headers:**  
- `Authorization` (user-specific ID)

## Response Format Example
```json
{
  "2024-04-12": {
    "profit_loss_percentage": 50,
    "total_cost_buy": 3000,
    "total_cost_sell": 4500
  }
}
```

## Error Handling
- `400 Bad Request`: Missing parameters or headers.
- `401 Unauthorized`: Invalid user ID.
- `500 Internal Server Error`: Backend issues.

## Contribution
- Fork the repository.
- Create a new branch (`git checkout -b feature-branch`).
- Commit your changes (`git commit -am 'Add new feature'`).
- Push to the branch (`git push origin feature-branch`).
- Create a Pull Request.

## License
This project is licensed under the MIT License.




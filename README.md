
# 🍎 Nutrition Analyzer MCP Server

A **stateless MCP (Model Context Protocol) server** that analyzes food items and provides **detailed nutrition facts** using the [Nutritionix API](https://developer.nutritionix.com/).  
Built with **FastMCP**, **asyncio**, and **httpx**, this server can be integrated into AI assistants, chatbots, or automation workflows.

---

## ✨ Features

- 🔐 **Secure Access** with Bearer Token authentication
- ⚡ **Stateless HTTP Mode** for easy integration and scalability
- 🥗 **Accurate Nutrition Data** from Nutritionix API
- 📦 Returns **calories, macronutrients, micronutrients, and serving size**
- ⏳ **Fast Async HTTP Requests** for low-latency responses

---

## 🛠 Tech Stack

- **Python 3.10+**
- [FastMCP](https://pypi.org/project/fastmcp/) – MCP server framework
- [httpx](https://www.python-httpx.org/) – Async HTTP client
- [Nutritionix API](https://developer.nutritionix.com/) – Food & nutrition database
- [dotenv](https://pypi.org/project/python-dotenv/) – Environment variable management

---

## 📂 Project Structure
- Nutrition_wisdom/
- │
- ├── server.py # Main MCP server code
- ├── .env # Environment variables (not committed to GitHub)
- ├── requirements.txt # Python dependencies
- └── README.md # Project documentation


---

## ⚙️ Installation & Setup

### 2️⃣ Create and activate a virtual environment

```bash
# Create virtual environment
python -m venv venv

# Activate on Windows
venv\Scripts\activate 
```
### 2 Install dependencies
```bash
- pip install -r requirements.txt
```

### 3  Set up environment variables
- Create a .env file in the root directory:

# Authentication token for MCP server
- AUTH_TOKEN=your_auth_token_here

# To validate the tool
- MY_NUMBER=your_number_here

# Nutritionix API credentials
- NUTRITIONIX_APP_ID=your_app_id_here
- NUTRITIONIX_APP_KEY=your_app_key_here

### 4  Running the Server
- python main.py

# Example Request & Response
Request:

{
  "tool": "analyze_nutrition",
  "params": {
    "food_query": "2 boiled eggs"
  }
}

Response:
{
  "food": "egg",
  "serving": {
    "quantity": 2,
    "unit": "large",
    "weight_grams": 100
  },
  "calories": 155,
  "macronutrients": {
    "protein_g": 13,
    "fat_g": 11,
    "carbs_g": 1.1,
    "fiber_g": 0,
    "sugars_g": 1.1
  },
  "micronutrients": {
    "sodium_mg": 124,
    "cholesterol_mg": 373,
    "potassium_mg": 126
  },
  "source": "Nutritionix API"
}


# 🧪 Testing
- You can test the MCP server using: Postman

curl -X POST "http://localhost:8086/tools/analyze_nutrition" \
     -H "Authorization: Bearer your_auth_token_here" \
     -H "Content-Type: application/json" \
     -d '{"food_query": "1 avocado"}'

import asyncio
import os
from typing import Annotated
from dotenv import load_dotenv
from fastmcp import FastMCP


try:
    from fastmcp.auth.providers.bearer import BearerAuthProvider, RSAKeyPair
except ImportError:
    from fastmcp.server.auth.providers.bearer import BearerAuthProvider, RSAKeyPair


try:
    from fastmcp import ErrorData, McpError
    from fastmcp.types import INVALID_PARAMS, INTERNAL_ERROR
except ImportError:
    from mcp import ErrorData, McpError
    from mcp.types import INVALID_PARAMS, INTERNAL_ERROR

from mcp.server.auth.provider import AccessToken
from pydantic import Field
import httpx
from urllib.parse import quote_plus

load_dotenv()


TOKEN = os.environ.get("AUTH_TOKEN")
MY_NUMBER = os.environ.get("MY_NUMBER")
NUTRITIONIX_APP_ID = os.environ.get("NUTRITIONIX_APP_ID")  
NUTRITIONIX_APP_KEY = os.environ.get("NUTRITIONIX_APP_KEY")  

assert TOKEN is not None, "Please set AUTH_TOKEN in your .env file"
assert MY_NUMBER is not None, "Please set MY_NUMBER in your .env file"
assert NUTRITIONIX_APP_ID is not None, "Please set NUTRITIONIX_APP_ID in your .env file"
assert NUTRITIONIX_APP_KEY is not None, "Please set NUTRITIONIX_APP_KEY in your .env file"

class SimpleBearerAuthProvider(BearerAuthProvider):
    def __init__(self, token: str):
        k = RSAKeyPair.generate()
        super().__init__(public_key=k.public_key, jwks_uri=None, issuer=None, audience=None)
        self.token = token

    async def load_access_token(self, token: str) -> AccessToken | None:
        if token == self.token:
            return AccessToken(
                token=token,
                client_id="puch-client",
                scopes=["*"],
                expires_at=None,
            )
        return None


mcp = FastMCP(
    "Nutrition Analyzer MCP Server",
    auth=SimpleBearerAuthProvider(TOKEN),
    stateless_http=True
)

@mcp.tool
async def about() -> dict:
    return {"name": "NutritiWisdom", "description": "A MCP server which gives you nutritional information of various food items"}

@mcp.tool
async def validate() -> str:
    return MY_NUMBER


async def fetch_nutrition_data(query: str) -> dict:
 
    url = "https://trackapi.nutritionix.com/v2/natural/nutrients"
    headers = {
        "x-app-id": NUTRITIONIX_APP_ID,
        "x-app-key": NUTRITIONIX_APP_KEY,
        "Content-Type": "application/json"
    }
    
    async with httpx.AsyncClient() as client:
        try:
            response = await client.post(
                url,
                headers=headers,
                json={"query": query},
                timeout=10.0
            )
            response.raise_for_status()
            data = response.json()
            
            if not data.get("foods"):
                raise McpError(ErrorData(
                    code=INVALID_PARAMS,
                    message="No nutrition data found for this query"
                ))
                
            return data["foods"][0]  
            
        except httpx.HTTPStatusError as e:
            error_msg = f"Nutritionix API error: {e.response.text}"
            raise McpError(ErrorData(code=INTERNAL_ERROR, message=error_msg))
        except Exception as e:
            raise McpError(ErrorData(
                code=INTERNAL_ERROR,
                message=f"Nutrition data fetch failed: {str(e)}"
            ))


NutritionAnalyzerDescription = {
    "description": "Get detailed nutrition facts for food items.",
    "use_when": "User asks about calories or nutrients in food.",
    "side_effects": "Calls Nutritionix API for accurate data."
}

@mcp.tool(description=NutritionAnalyzerDescription["description"])
async def analyze_nutrition(
    food_query: Annotated[str, Field(description="Food item and quantity (e.g. '1 banana', '100g chicken breast')")]
) -> dict:
    """
    Returns detailed nutrition information for the specified food item.
    Example queries: "1 avocado", "200g cooked pasta", "2 slices of pizza"
    """
    if not food_query.strip():
        raise McpError(ErrorData(
            code=INVALID_PARAMS,
            message="Food query cannot be empty"
        ))
    
    try:
        nutrition_data = await fetch_nutrition_data(food_query)
        
      
        return {
            "food": nutrition_data.get("food_name", "Unknown"),
            "serving": {
                "quantity": nutrition_data.get("serving_qty", 1),
                "unit": nutrition_data.get("serving_unit", "serving"),
                "weight_grams": nutrition_data.get("serving_weight_grams", 0)
            },
            "calories": nutrition_data.get("nf_calories", 0),
            "macronutrients": {
                "protein_g": nutrition_data.get("nf_protein", 0),
                "fat_g": nutrition_data.get("nf_total_fat", 0),
                "carbs_g": nutrition_data.get("nf_total_carbohydrate", 0),
                "fiber_g": nutrition_data.get("nf_dietary_fiber", 0),
                "sugars_g": nutrition_data.get("nf_sugars", 0)
            },
            "micronutrients": {
                "sodium_mg": nutrition_data.get("nf_sodium", 0),
                "cholesterol_mg": nutrition_data.get("nf_cholesterol", 0),
                "potassium_mg": nutrition_data.get("nf_potassium", 0)
            },
            "source": "Nutritionix API"
        }
        
    except Exception as e:
        raise McpError(ErrorData(
            code=INTERNAL_ERROR,
            message=f"Failed to analyze nutrition: {str(e)}"
        ))

async def main():
    print("🚀 Starting Nutrition Analyzer MCP server in STATELESS mode on http://0.0.0.0:8086")
    await mcp.run_async("streamable-http", host="0.0.0.0", port=8086)

if __name__ == "__main__":
    asyncio.run(main())

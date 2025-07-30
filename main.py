import json
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from dotenv import load_dotenv
from square import Square, environment
import os

load_dotenv()

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

client = Square(
    token=os.getenv("SQUARE_ACCESS_TOKEN"),
    environment=environment.SquareEnvironment.PRODUCTION
)

@app.get("/")
async def get_products():
    try:
        image_urls = {}
        result = client.catalog.list(types='IMAGE')
        items = result.items
        for item in items:
            image_urls[item.id] = item.image_data.url

        result = client.catalog.list(types='ITEM')
        items = result.items
        products = []

        for item in items:
            data = item.item_data
            name = data.name

            description = data.description_plaintext or data.description or ""
            image_url = data.ecom_image_uris[0] if data.ecom_image_uris else None
            variations = data.variations or []

            for var in variations:
                var_data = var.item_variation_data
                price_cents = var_data.price_money.amount if var_data.price_money else 0
                price = price_cents / 100
                currency = var_data.price_money.currency if var_data.price_money else "USD"

                stock = var.item_variation_data.location_overrides[0].sold_out
                in_stock = False if stock else True

                image_id = data.image_ids[0]
                image_url = image_urls[image_id]

                products.append({
                    "id": var.id,
                    "name": name,
                    "description": description,
                    "price": price,
                    "currency": currency,
                    "image_url": image_url,
                    "in-stock": in_stock
                })

        return {"products": products}

    except Exception as e:
        print("❌ Error:", e)
        return {"error": "Unable to fetch products"} # 5FRXN25JIXBLYZBZ44L3V45S # image_ids=['5FRXN25JIXBLYZBZ44L3V45S']

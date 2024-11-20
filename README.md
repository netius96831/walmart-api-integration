# Walmart API Integration Test

A simple Python script to test 5 Walmart Marketplace APIs using a sample book product.

## APIs Tested

1. Add New products (batch listing)
2. Update quantity
3. Get order
4. Fulfil Order
5. Update Tracking Info

## Sample Product

- Title: The Lightlark Saga Book, 3 Books Collection Set
- ISBN: 9781637996478
- SKU: LGHTRK-SET-3
- Publisher: generic

## Setup

1. Copy environment template:
```bash
cp .env.template .env
```

2. Install requirements:
```bash
pip install -r requirements.txt
```

## Running the Test

Run the script:
```bash
python main.py
```

The script will:
1. Add the sample book product
2. Update its quantity to 100
3. Check for any orders
4. If orders exist, test fulfillment and tracking updates

## API Responses

The script will print responses from each API call to help verify the operations.
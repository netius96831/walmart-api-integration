# Walmart Marketplace API Integration

This project implements a Python script to interact with Walmart Marketplace APIs for managing products and orders. It provides functionality for the following operations:

1. Add New Products (Batch Listing)
2. Update Product Quantity
3. Get Orders
4. Fulfill Orders
5. Update Tracking Information

## Prerequisites
- Python 3.8 or higher
- Walmart Marketplace API credentials (Client ID and Secret Key)
- Internet connection

## Setup Instructions

1. Clone or download this repository
2. Install the required dependencies:
```bash
pip install -r requirements.txt
```

3. Create a `.env` file in the project root with your Walmart API credentials:
```
WALMART_CLIENT_ID=your_client_id_here
WALMART_CLIENT_SECRET=your_client_secret_here
```

## Usage

The script is configured to work with a sample book product:
- Title: The Lightlark Saga Book, 3 Books Collection Set
- ISBN: 9781637996478
- Publisher: generic

To run the script:
```bash
python main.py
```

The script will:
1. Add the sample book product to Walmart Marketplace
2. Update its quantity to 100 units
3. Retrieve recent orders
4. If orders exist, fulfill a sample order and update tracking information

## Error Handling
The script includes comprehensive error handling and will display clear error messages if any API calls fail.

## Notes
- Make sure to replace the sample book's image URL with a valid image URL before running in production
- The script uses the Walmart Marketplace API v3
- All API responses are logged to the console for debugging purposes

## Security
- Never commit your `.env` file or expose your API credentials
- Always use environment variables for sensitive information

## Support
For any questions or issues, please refer to the [Walmart Marketplace API Documentation](https://developer.walmart.com/api/us/mp/orders)
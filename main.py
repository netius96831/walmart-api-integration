import os
import json
from dotenv import load_dotenv
import requests
from datetime import datetime

# Load environment variables
load_dotenv()

class WalmartAPI:
    def __init__(self):
        self.client_id = os.getenv('WALMART_CLIENT_ID')
        self.client_secret = os.getenv('WALMART_CLIENT_SECRET')
        self.base_url = 'https://marketplace.walmartapis.com/v3'
        self.token = None
        
    def get_token(self):
        """Get access token from Walmart API"""
        auth_url = f"{self.base_url}/token"
        headers = {
            'WM_SVC.NAME': 'Walmart Marketplace',
            'WM_QOS.CORRELATION_ID': datetime.now().strftime('%Y-%m-%d.%H:%M:%S'),
            'Content-Type': 'application/x-www-form-urlencoded',
        }
        data = {
            'grant_type': 'client_credentials'
        }
        response = requests.post(
            auth_url,
            headers=headers,
            auth=(self.client_id, self.client_secret),
            data=data
        )
        if response.status_code == 200:
            self.token = response.json()['access_token']
            return self.token
        raise Exception(f"Failed to get token: {response.text}")

    def get_headers(self):
        """Get common headers for API requests"""
        if not self.token:
            self.get_token()
        return {
            'WM_SEC.ACCESS_TOKEN': self.token,
            'WM_SVC.NAME': 'Walmart Marketplace',
            'WM_QOS.CORRELATION_ID': datetime.now().strftime('%Y-%m-%d.%H:%M:%S'),
            'Content-Type': 'application/json',
            'Accept': 'application/json'
        }

    def add_product(self, product_data):
        """Add new product (batch listing)"""
        url = f"{self.base_url}/items"
        headers = self.get_headers()
        response = requests.post(url, headers=headers, json=product_data)
        if response.status_code in [200, 201]:
            return response.json()
        raise Exception(f"Failed to add product: {response.text}")

    def update_quantity(self, sku, quantity):
        """Update product quantity"""
        url = f"{self.base_url}/inventory"
        headers = self.get_headers()
        inventory_data = {
            "sku": sku,
            "quantity": {
                "unit": "EACH",
                "amount": quantity
            }
        }
        response = requests.put(url, headers=headers, json=inventory_data)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to update quantity: {response.text}")

    def get_orders(self, created_after=None):
        """Get orders"""
        url = f"{self.base_url}/orders"
        headers = self.get_headers()
        params = {}
        if created_after:
            params['createdStartDate'] = created_after
        
        response = requests.get(url, headers=headers, params=params)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to get orders: {response.text}")

    def fulfill_order(self, purchase_order_id, tracking_info):
        """Fulfill order"""
        url = f"{self.base_url}/orders/{purchase_order_id}/shipping"
        headers = self.get_headers()
        response = requests.post(url, headers=headers, json=tracking_info)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to fulfill order: {response.text}")

    def update_tracking(self, purchase_order_id, tracking_info):
        """Update tracking information"""
        url = f"{self.base_url}/orders/{purchase_order_id}/tracking"
        headers = self.get_headers()
        response = requests.post(url, headers=headers, json=tracking_info)
        if response.status_code == 200:
            return response.json()
        raise Exception(f"Failed to update tracking: {response.text}")

def main():
    # Sample book data
    sample_book = {
        "sku": "LGHTRK-SET-3",
        "productName": "The Lightlark Saga Book, 3 Books Collection Set",
        "productType": "BOOK",
        "price": 29.99,
        "brand": "Alex Aster",
        "shortDescription": "The Lightlark Saga Book, 3 Books Collection Set, Lightlark, Nightbane, Skyshade, by Alex Aster",
        "mainImageUrl": "https://example.com/book-image.jpg",
        "productIdentifiers": {
            "isbn": "9781637996478"
        },
        "publisher": "generic",
        "language": "English",
        "bookFormat": "Paperback"
    }

    try:
        # Initialize API client
        walmart = WalmartAPI()

        # 1. Add new product
        print("Adding new product...")
        add_result = walmart.add_product(sample_book)
        print(f"Product added: {add_result}")

        # 2. Update quantity
        print("\nUpdating quantity...")
        quantity_result = walmart.update_quantity("LGHTRK-SET-3", 100)
        print(f"Quantity updated: {quantity_result}")

        # 3. Get orders
        print("\nGetting recent orders...")
        orders = walmart.get_orders()
        print(f"Orders retrieved: {orders}")

        # 4. Fulfill sample order (if any orders exist)
        if orders.get('elements'):
            order = orders['elements'][0]
            tracking_info = {
                "carrier": "UPS",
                "trackingNumber": "1Z999999999999999",
                "shipDateTime": datetime.now().isoformat()
            }
            
            print("\nFulfilling order...")
            fulfill_result = walmart.fulfill_order(order['purchaseOrderId'], tracking_info)
            print(f"Order fulfilled: {fulfill_result}")

            # 5. Update tracking
            print("\nUpdating tracking info...")
            tracking_result = walmart.update_tracking(order['purchaseOrderId'], tracking_info)
            print(f"Tracking updated: {tracking_result}")

    except Exception as e:
        print(f"Error occurred: {str(e)}")

if __name__ == "__main__":
    main()
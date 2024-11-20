import os
import json
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_token():
    """Get access token from Walmart API"""
    auth_url = os.getenv('WALMART_AUTH_URL')
    client_id = os.getenv('WALMART_CLIENT_ID')
    client_secret = os.getenv('WALMART_CLIENT_SECRET')
    
    headers = {
        'WM_SVC.NAME': 'Walmart Marketplace',
        'WM_QOS.CORRELATION_ID': datetime.now().strftime('%Y-%m-%d.%H:%M:%S'),
        'Content-Type': 'application/x-www-form-urlencoded',
        'Accept': 'application/json'
    }
    data = 'grant_type=client_credentials'
    
    try:
        response = requests.post(
            auth_url,
            headers=headers,
            auth=(client_id, client_secret),
            data=data,
            verify=True
        )
        
        print(f"Token Request Status Code: {response.status_code}")
        print(f"Token Request Headers: {response.headers}")
        print(f"Token Request Response: {response.text}")
        
        if response.status_code != 200:
            print(f"Error getting token. Status code: {response.status_code}")
            print(f"Response: {response.text}")
            return None
            
        try:
            token_data = response.json()
            return token_data.get('access_token')
        except json.JSONDecodeError as e:
            print(f"Failed to decode JSON response: {e}")
            print(f"Response content: {response.text}")
            return None
            
    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def get_headers(token):
    """Get common headers for API requests"""
    if not token:
        raise ValueError("No valid token provided")
        
    return {
        'Authorization': f'Bearer {token}',
        'WM_SEC.ACCESS_TOKEN': token,
        'WM_SVC.NAME': 'Walmart Marketplace',
        'WM_QOS.CORRELATION_ID': datetime.now().strftime('%Y-%m-%d.%H:%M:%S'),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def add_product(token, book_data):
    """Test API 1: Add new product (batch listing)"""
    if not token:
        print("No valid token available")
        return False
        
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/feeds?feedType=item"
    
    feed_data = {
        "feedVersion": "2.2",
        "requestId": datetime.now().strftime('%Y%m%d%H%M%S'),
        "requestBatchId": datetime.now().strftime('%Y%m%d%H%M%S'),
        "items": [{
            "mart": "WALMART_US",
            "sku": book_data["sku"],
            "wpid": book_data["sku"],
            "productIdentifiers": [{
                "productIdType": "ISBN",
                "productId": book_data["isbn"]
            }],
            "productName": book_data["title"],
            "brand": "Alex Aster",
            "price": book_data["price"],
            "shortDescription": book_data["description"],
            "mainImageUrl": book_data["image_url"],
            "productType": "BOOK",
            "categoryPath": "Books/Fiction Books",
            "publisherInfo": {
                "publisher": book_data["publisher"],
                "language": "English",
                "format": "Paperback"
            },
            "shippingWeight": {
                "value": 1.0,
                "unit": "POUND"
            }
        }]
    }
    
    try:
        response = requests.post(url, headers=get_headers(token), json=feed_data)
        print("\n1. Add Product Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code in [200, 201]
    except requests.exceptions.RequestException as e:
        print(f"Failed to add product: {e}")
        return False

def update_quantity(token, sku, quantity):
    """Test API 2: Update quantity"""
    if not token:
        print("No valid token available")
        return False
        
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/feeds?feedType=inventory"
    
    inventory_data = {
        "feedVersion": "1.4",
        "requestId": datetime.now().strftime('%Y%m%d%H%M%S'),
        "requestBatchId": datetime.now().strftime('%Y%m%d%H%M%S'),
        "inventoryItems": [{
            "sku": sku,
            "quantity": {
                "unit": "EACH",
                "amount": quantity
            }
        }]
    }
    
    try:
        response = requests.post(url, headers=get_headers(token), json=inventory_data)
        print("\n2. Update Quantity Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Failed to update quantity: {e}")
        return False

def get_orders(token):
    """Test API 3: Get orders"""
    if not token:
        print("No valid token available")
        return None
        
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/orders/released"
    params = {
        'limit': 10,
        'createdStartDate': (datetime.now().replace(day=1)).strftime('%Y-%m-%d')
    }
    
    try:
        response = requests.get(url, headers=get_headers(token), params=params)
        print("\n3. Get Orders Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.json() if response.status_code == 200 else None
    except requests.exceptions.RequestException as e:
        print(f"Failed to get orders: {e}")
        return None

def fulfill_order(token, purchase_order_id):
    """Test API 4: Fulfill order"""
    if not token:
        print("No valid token available")
        return False
        
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/orders/{purchase_order_id}/shipping"
    
    shipping_data = {
        "orderLines": [{
            "lineNumber": "1",
            "orderLineStatuses": {
                "orderLineStatus": [{
                    "status": "Shipped",
                    "statusQuantity": {
                        "unitOfMeasurement": "EACH",
                        "amount": "1"
                    },
                    "trackingInfo": {
                        "shipDateTime": datetime.now().isoformat(),
                        "carrierName": {
                            "carrier": "UPS"
                        },
                        "methodCode": "Standard",
                        "trackingNumber": "1Z999999999999999"
                    }
                }]
            }
        }]
    }
    
    try:
        response = requests.post(url, headers=get_headers(token), json=shipping_data)
        print("\n4. Fulfill Order Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Failed to fulfill order: {e}")
        return False

def update_tracking(token, purchase_order_id):
    """Test API 5: Update tracking information"""
    if not token:
        print("No valid token available")
        return False
        
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/orders/{purchase_order_id}/tracking"
    
    tracking_data = {
        "orderLines": [{
            "lineNumber": "1",
            "trackingInfo": {
                "shipDateTime": datetime.now().isoformat(),
                "carrierName": {
                    "carrier": "UPS"
                },
                "methodCode": "Standard",
                "trackingNumber": "1Z999999999999999"
            }
        }]
    }
    
    try:
        response = requests.post(url, headers=get_headers(token), json=tracking_data)
        print("\n5. Update Tracking Response:")
        print(f"Status Code: {response.status_code}")
        print(f"Response: {response.text}")
        return response.status_code == 200
    except requests.exceptions.RequestException as e:
        print(f"Failed to update tracking: {e}")
        return False

def main():
    # Get authentication token
    print("Getting authentication token...")
    token = get_token()
    if not token:
        print("Failed to get authentication token. Exiting...")
        return

    # Sample book data from the requirement
    book_data = {
        "sku": "LGHTRK-SET-3",
        "title": "The Lightlark Saga Book, 3 Books Collection Set, Lightlark, Nightbane, Skyshade, by Alex Aster",
        "isbn": "9781637996478",
        "price": 29.99,
        "description": "The Lightlark Saga Book, 3 Books Collection Set, Lightlark, Nightbane, Skyshade, by Alex Aster",
        "publisher": "generic",
        "image_url": "https://m.media-amazon.com/images/I/71jxhw9YPWL._SL1500_.jpg"
    }

    # Test API 1: Add new product
    print("\nTesting API 1: Add new product...")
    if add_product(token, book_data):
        # Test API 2: Update quantity
        print("\nTesting API 2: Update quantity...")
        update_quantity(token, book_data["sku"], 100)

        # Test API 3: Get orders
        print("\nTesting API 3: Get orders...")
        orders = get_orders(token)

        if orders and orders.get('list', {}).get('elements', {}).get('order', []):
            # Get the first order from the list
            order = orders['list']['elements']['order'][0]
            purchase_order_id = order['purchaseOrderId']

            # Test API 4: Fulfill order
            print("\nTesting API 4: Fulfill order...")
            if fulfill_order(token, purchase_order_id):
                # Test API 5: Update tracking
                print("\nTesting API 5: Update tracking...")
                update_tracking(token, purchase_order_id)
            else:
                print("\nFailed to fulfill order. Skipping tracking update.")
        else:
            print("\nNo orders found to test fulfillment and tracking APIs")
    else:
        print("\nFailed to add product. Skipping remaining tests.")

if __name__ == "__main__":
    main()
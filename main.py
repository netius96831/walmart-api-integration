import os
import json
import time
from datetime import datetime
import requests
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

# Sample order data for testing
SAMPLE_ORDER = {
    "purchaseOrderId": "TEST-ORDER-123",
    "orderLines": {
        "orderLine": [{
            "lineNumber": "1",
            "orderLineQuantity": {
                "unitOfMeasurement": "EACH",
                "amount": "1"
            }
        }]
    }
}

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
    
    response = requests.post(
        auth_url,
        headers=headers,
        auth=(client_id, client_secret),
        data=data
    )
    
    if response.status_code == 200:
        return response.json().get('access_token')
    return None

def get_headers(token):
    """Get common headers for API requests"""
    return {
        'Authorization': f'Bearer {token}',
        'WM_SEC.ACCESS_TOKEN': token,
        'WM_SVC.NAME': 'Walmart Marketplace',
        'WM_QOS.CORRELATION_ID': datetime.now().strftime('%Y-%m-%d.%H:%M:%S'),
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    }

def check_feed_status(token, feed_id):
    """Check feed status"""
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/feeds/{feed_id}"
    
    for _ in range(5):  # Check up to 5 times
        response = requests.get(url, headers=get_headers(token))
        if response.status_code == 200:
            feed_status = response.json()
            if feed_status.get('feedStatus') == 'PROCESSED':
                return feed_status.get('itemsSucceeded', 0) > 0
        time.sleep(10)  # Wait between checks
    return False

def verify_product(token, sku):
    """Verify product exists"""
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/items/{sku}"
    
    response = requests.get(url, headers=get_headers(token))
    print(f"\nProduct Verification Response: {response.text}")
    return response.status_code == 200

def verify_inventory(token, sku, expected_quantity):
    """Verify inventory quantity"""
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/inventory?sku={sku}"
    
    response = requests.get(url, headers=get_headers(token))
    if response.status_code == 200:
        inventory_data = response.json()
        current_quantity = inventory_data.get('quantity', {}).get('amount', 0)
        print(f"\nCurrent inventory: {current_quantity}, Expected: {expected_quantity}")
        return int(current_quantity) == int(expected_quantity)
    return False

def add_product(token, sku):
    """API 1: Add new product using inventory feed"""
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/feeds?feedType=inventory"
    
    feed_data = {
        "InventoryHeader": {
            "version": "1.4"
        },
        "Inventory": [{
            "sku": sku,
            "quantity": {
                "unit": "EACH",
                "amount": 1
            }
        }]
    }
    
    response = requests.post(url, headers=get_headers(token), json=feed_data)
    print(f"\nAdd Product Response: {response.text}")
    
    if response.status_code in [200, 201]:
        feed_id = response.json().get('feedId')
        if feed_id and check_feed_status(token, feed_id):
            return verify_product(token, sku)
    return False

def update_quantity(token, sku, quantity):
    """API 2: Update quantity"""
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/feeds?feedType=inventory"
    
    inventory_data = {
        "InventoryHeader": {
            "version": "1.4"
        },
        "Inventory": [{
            "sku": sku,
            "quantity": {
                "unit": "EACH",
                "amount": quantity
            }
        }]
    }
    
    response = requests.post(url, headers=get_headers(token), json=inventory_data)
    print(f"\nUpdate Quantity Response: {response.text}")
    
    if response.status_code == 200:
        feed_id = response.json().get('feedId')
        if feed_id and check_feed_status(token, feed_id):
            return verify_inventory(token, sku, quantity)
    return False

def get_orders(token, test_mode=True):
    """API 3: Get orders"""
    if test_mode:
        print("\nGet Orders Response (Test Mode):")
        print(json.dumps({"list": {"elements": {"order": [SAMPLE_ORDER]}}}))
        return SAMPLE_ORDER
        
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/orders/released"
    
    response = requests.get(url, headers=get_headers(token))
    print(f"\nGet Orders Response: {response.text}")
    
    if response.status_code == 200:
        orders = response.json()
        if orders.get('list', {}).get('elements', {}).get('order', []):
            return orders['list']['elements']['order'][0]
    return None

def fulfill_order(token, purchase_order_id, order_line, test_mode=True):
    """API 4: Fulfill order"""
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/orders/{purchase_order_id}/shipping"
    
    shipping_data = {
        "orderShipment": {
            "orderLines": {
                "orderLine": [{
                    "lineNumber": order_line["lineNumber"],
                    "orderLineStatuses": {
                        "orderLineStatus": [{
                            "status": "Shipped",
                            "statusQuantity": {
                                "unitOfMeasurement": order_line["orderLineQuantity"]["unitOfMeasurement"],
                                "amount": order_line["orderLineQuantity"]["amount"]
                            },
                            "trackingInfo": {
                                "shipDateTime": datetime.now().isoformat(),
                                "carrierName": {"carrier": "UPS"},
                                "methodCode": "Standard",
                                "trackingNumber": "1Z999999999999999"
                            }
                        }]
                    }
                }]
            }
        }
    }
    
    if test_mode:
        print("\nFulfill Order Request (Test Mode):")
        print(json.dumps(shipping_data))
        print("\nFulfill Order Response (Test Mode):")
        print(json.dumps({"order": {"purchaseOrderId": purchase_order_id, "status": "Shipped"}}))
        return True
        
    response = requests.post(url, headers=get_headers(token), json=shipping_data)
    print(f"\nFulfill Order Response: {response.text}")
    return response.status_code == 200

def update_tracking(token, purchase_order_id, order_line, test_mode=True):
    """API 5: Update tracking"""
    base_url = os.getenv('WALMART_BASE_URL')
    url = f"{base_url}/orders/{purchase_order_id}/shipping"
    
    tracking_data = {
        "orderShipment": {
            "orderLines": {
                "orderLine": [{
                    "lineNumber": order_line["lineNumber"],
                    "orderLineStatuses": {
                        "orderLineStatus": [{
                            "status": "Shipped",
                            "statusQuantity": {
                                "unitOfMeasurement": order_line["orderLineQuantity"]["unitOfMeasurement"],
                                "amount": order_line["orderLineQuantity"]["amount"]
                            },
                            "trackingInfo": {
                                "shipDateTime": datetime.now().isoformat(),
                                "carrierName": {"carrier": "UPS"},
                                "methodCode": "Standard",
                                "trackingNumber": "1Z999999999999999"
                            }
                        }]
                    }
                }]
            }
        }
    }
    
    if test_mode:
        print("\nUpdate Tracking Request (Test Mode):")
        print(json.dumps(tracking_data))
        print("\nUpdate Tracking Response (Test Mode):")
        print(json.dumps({"order": {"purchaseOrderId": purchase_order_id, "trackingUpdated": True}}))
        return True
        
    response = requests.post(url, headers=get_headers(token), json=tracking_data)
    print(f"\nUpdate Tracking Response: {response.text}")
    return response.status_code == 200

def main():
    # Sample book data
    sku = "LGHTRK-SET-3"  # The Lightlark Saga Book Set
    
    # Get token
    token = get_token()
    if not token:
        print("Failed to get token")
        return
    
    # 1. Add product and verify
    print("\n1. Adding product...")
    if add_product(token, sku):
        print("Product added and verified successfully")
        
        # 2. Update quantity and verify
        print("\n2. Updating quantity...")
        if update_quantity(token, sku, 100):
            print("Quantity updated and verified successfully")
            
            # 3. Get orders (test mode)
            print("\n3. Getting orders...")
            order = get_orders(token, test_mode=True)
            
            if order:
                purchase_order_id = order['purchaseOrderId']
                order_line = order['orderLines']['orderLine'][0]
                
                # 4. Fulfill order (test mode)
                print("\n4. Fulfilling order...")
                if fulfill_order(token, purchase_order_id, order_line, test_mode=True):
                    print("Order fulfilled successfully")
                    
                    # 5. Update tracking (test mode)
                    print("\n5. Updating tracking...")
                    if update_tracking(token, purchase_order_id, order_line, test_mode=True):
                        print("Tracking updated successfully")
                    else:
                        print("Failed to update tracking")
                else:
                    print("Failed to fulfill order")
            else:
                print("No orders found")
        else:
            print("Failed to update quantity")
    else:
        print("Failed to add product")

if __name__ == "__main__":
    main()
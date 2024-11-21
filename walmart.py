import requests
import json
import base64
import uuid
from datetime import datetime

# Walmart API credentials
CLIENT_ID = '126e935e-a51c-4c7a-86e6-4b2c234fea34'
CLIENT_SECRET = 'APOTj6Zpz9BCFvQ3zgDSP_ui6fC1ODHyySC7Szgb1McjW8Pan1LPlEHcm6-EjBi35Zk3X7Zsm5g8EtPwae_VtM4'
BASE_URL = 'https://marketplace.walmartapis.com/v3'
AUTH_URL = 'https://marketplace.walmartapis.com/v3/token'

# Function to get the OAuth token
def get_oauth_token():
    try:
        credentials = f"{CLIENT_ID}:{CLIENT_SECRET}"
        b64_credentials = base64.b64encode(credentials.encode()).decode()
        headers = {
            'Authorization': f'Basic {b64_credentials}',
            'Content-Type': 'application/x-www-form-urlencoded',
            'Accept': 'application/json',
            'WM_PARTNER.ID': CLIENT_ID,
            'WM_CONSUMER.CHANNEL.TYPE': str(uuid.uuid4()),
            'WM_QOS.CORRELATION_ID': str(uuid.uuid4()),
            'WM_SVC.NAME': 'WalmartMarketplace',
        }
        response = requests.post(AUTH_URL, headers=headers, data={"grant_type": "client_credentials", "code": "65CA5DA313A549D49D15D3119D9AD85D", "refresh_token": "APXcIoTpKMH9OQN.....", "redirect_uri": "https://example-client-app.com"})
        response.raise_for_status()
        return response.json()['access_token']
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while obtaining token: {err}")
        raise
    except Exception as e:
        print(f"An error occurred while obtaining token: {e}")
        raise

def create_headers(access_token):
    return {
        'WM_SVC.NAME': 'WalmartMarketplace',
        'WM_QOS.CORRELATION_ID': str(uuid.uuid4()),
        'WM_CONSUMER.CHANNEL.TYPE': '7',
        'WM_SEC.ACCESS_TOKEN': access_token,
        'WM_PARTNER.ID': CLIENT_ID,
        'Authorization': f"Bearer {access_token}",
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }

# Function to batch listing products
def batch_listing(token):
    url = f"{BASE_URL}/feeds?feedType=inventory"
    headers = create_headers(token)
    # Sample product data
    product_data = {
        "MPItemFeedHeader": {
            "sellingChannel": "marketplace",
            "processMode": "REPLACE",
            "subset": "EXTERNAL",
            "locale": "en",
            "version": "4.8",
            "subCategory": "home_other"
        },
        "MPItem": [
            {
                "Orderable": {
                    "sku": "lightlark-saga-collection",
                    "productIdentifiers": {
                        "productIdType": "ISBN",
                        "productId": "9781637996478"
                    },
                    "productName": "The Lightlark Saga Book, 3 Books Collection Set, Lightlark, Nightbane, Skyshade, by Alex Aster",
                    "brand": "Generic",
                    "price": 15.99,
                    "ShippingWeight": 1.2,
                    "MustShipAlone": "No"
                },
                "Visible": {
                    "Home Decor, Kitchen, & Other": {
                        "shortDescription": "3 Books Collection Set: Lightlark, Nightbane, Skyshade by Alex Aster.",
                        "mainImageUrl": "https://m.media-amazon.com/images/I/71kkYQ8qINL._SY466_.jpg",
                        "keyFeatures": [
                            "Includes Lightlark, Nightbane, and Skyshade",
                            "Written by Alex Aster",
                            "Perfect for fantasy book lovers"
                        ]
                    }
                }
            }
        ]
    }
    try:
        response = requests.post(url, headers=headers, json=product_data)
        response.raise_for_status()
        print(response.json())
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred during batch listing: {err}")
        return None
    except Exception as e:
        print(f"An error occurred during batch listing: {e}")
        return None

# Function to update product quantity
def update_quantity(token, sku, quantity):
    url = f"{BASE_URL}/feeds?feedType=inventory"
    headers = create_headers(token)
    data = {
      "InventoryHeader": {
        "version": "1.4"
      },
      "Inventory": [
        {
          "sku": sku,
          "quantity": {
            "unit": "EACH",
            "amount": quantity
          },
          "inventoryAvailableDate": "2024-11-20"
        }
      ]
    }
    try:
        response = requests.post(url, headers=headers, json=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while updating quantity: {err}")
        return None
    except Exception as e:
        print(f"An error occurred while updating quantity: {e}")
        return None

# Function to get orders
def get_orders(token):
    url = f"{BASE_URL}/orders"
    headers = create_headers(token)
    try:
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while getting orders: {err}")
        return None
    except Exception as e:
        print(f"An error occurred while getting orders: {e}")
        return None

# Function to fulfill an order
def fulfill_order(token, order):
    url = f"{BASE_URL}/orders/{order['purchaseOrderId']}/shipping"
    headers = create_headers(token)

    # Prepare shipment payload
    payload = {
        "orderShipment": {
        "orderLines": {
          "orderLine": [
            {
              "lineNumber": "1",
              "intentToCancelOverride": 'false',
              "sellerOrderId": "92344",
              "orderLineStatuses": {
                "orderLineStatus": [
                  {
                    "status": "Shipped",
                    "statusQuantity": {
                      "unitOfMeasurement": "EACH",
                      "amount": "1"
                    },
                    "trackingInfo": {
                      "shipDateTime": 1729386000000,
                      "carrierName": {
                        "carrier": "UPS"
                      },
                      "methodCode": "Standard",
                      "trackingNumber": "22344",
                      "trackingURL": "http://walmart/tracking/ups?&type=MP&seller_id=12345&promise_date=03/02/2020&dzip=92840&tracking_numbers=92345"
                    },
                    "returnCenterAddress": {
                      "name": "walmart",
                      "address1": "walmart store 2",
                      "city": "Huntsville",
                      "state": "AL",
                      "postalCode": "35805",
                      "country": "USA",
                      "dayPhone": "12344",
                      "emailId": "walmart@walmart.com"
                    }
                  }
                ]
              }
            }
          ]
        }
      }
    }

    try:
        # Send the shipment update request
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        print(f"Order {order['purchaseOrderId']} fulfilled successfully!")
        return response.json()
    except requests.exceptions.RequestException as e:
        print(f"Error fulfilling order: {e}")
        if e.response:
            print(f"Response: {e.response.json()}")
        raise

# Function to update tracking information
def update_tracking(token, order):
    url = f"{BASE_URL}/orders/{order['purchaseOrderId']}/shipping"
    headers = create_headers(token)
    payload = {
        "orderShipment": {
            "shipments": [
                {
                    "carrierName": {
                        "carrier": 'carrier_name'
                    },
                    "shipmentTrackingNumber": 'tracking_number',
                    "shipmentDates": {
                        "shipDate": 'ship_date'
                    },
                    "lineItems": [
                        {
                            "lineNumber": "1",
                            "quantity": {
                                "unit": "EACH",
                                "amount": 1
                            }
                        }
                    ]
                }
            ]
        }
    }
    try:
        response = requests.post(url, headers=headers, json=payload)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.HTTPError as err:
        print(f"HTTP error occurred while updating tracking information: {err}")
        return None
    except Exception as e:
        print(f"An error occurred while updating tracking information: {e}")
        return None

# Main execution
if __name__ == "__main__":
    try:
        # Get the access token
        token = get_oauth_token()
        print("Access Token obtained successfully.")
        # Batch listing the product
        listing_response = batch_listing(token)
        print("Batch Listing Response: %s", json.dumps(listing_response, indent=2))

        # Update quantity for the product
        update_response = update_quantity(token, "lightlark-saga-collection", 150)
        print("Update Quantity Response: %s", json.dumps(update_response, indent=2))

        # Get orders
        orders_response = get_orders(token)
        # print("Orders Response: %s", json.dumps(orders_response, indent=2))
        print(json.dumps(orders_response['list']['elements']['order'][0], indent=2))

        #fulfil order
        fulfill_response = fulfill_order(token, orders_response['list']['elements']['order'][0])
        print("Fulfill Order Response: %s", json.dumps(fulfill_response, indent=2))

        # Update tracking information (replace 'ORDER_ID' with actual order ID)
        tracking_response = update_tracking(token, orders_response['list']['elements']['order'][0])
        print("Update Tracking Response: %s", json.dumps(tracking_response, indent=2))

    except Exception as e:
        print("An unexpected error occurred: %s", str(e))
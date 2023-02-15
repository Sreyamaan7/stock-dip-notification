import os
import boto3
import requests
import json

def lambda_handler(event, context):
    
    # Alpha Vantage API URL
    url = "https://www.alphavantage.co/query"
    
    # Alpha Vantage API Key
    api_key = os.environ['API_KEY']
    
    # FAANG stock symbols
    symbols = ["FB", "AAPL", "AMZN", "NFLX", "GOOGL"]
    
    # Iterate over each symbol
    for symbol in symbols:
        
        # Build the API query parameters
        params = {
            "function": "GLOBAL_QUOTE",
            "symbol": symbol,
            "apikey": api_key
        }
        
        # Call the Alpha Vantage API
        response = requests.get(url, params=params)
        
        # Parse the response JSON
        data = json.loads(response.text)
        
        # Extract the current price
        current_price = float(data["Global Quote"]["05. price"])
        
        # Retrieve the previous price from the DynamoDB table (optional)
        dynamodb = boto3.resource('dynamodb')
        table = dynamodb.Table('FAANG_Stock_Prices')
        response = table.get_item(
            Key={'symbol': symbol}
        )
        previous_price = response.get('Item', {}).get('price', None)
        
        # Calculate the price difference
        if previous_price is not None:
            price_diff = previous_price - current_price
            percent_diff = price_diff / previous_price * 100
            
            # Check if the price difference exceeds a threshold (e.g., 5%)
            if percent_diff > 5:
                
                # Send an SNS notification
                sns = boto3.client('sns')
                message = f"{symbol} has dropped {percent_diff:.2f}% from {previous_price:.2f} to {current_price:.2f}"
                response = sns.publish(
                    TopicArn=os.environ['SNS_TOPIC_ARN'],
                    Message=message
                )
        
        # Save the current price to the DynamoDB table (optional)
        table.put

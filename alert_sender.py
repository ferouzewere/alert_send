import requests
import json
import time

def send_alert(title, message, severity="info", sender="Infotrace Analytics", image_url=None):
    """
    Send an alert directly to Teams webhook endpoint
    severity can be: "high", "medium", or "info"
    """
    # Using the direct Teams webhook URL from .env
    webhook_url = "https://onfonmobile.webhook.office.com/webhookb2/f585348e-4c12-46ec-bf0f-320a151b31f8@01ddb3f3-913b-4413-9d55-74ba2ecb0204/IncomingWebhook/244eb3c8e0a14375b150993bb36f8057/d9e0f7b0-90ca-469f-bcbd-64b370106879/V2e6pRA6WMXL-VeFcA-gRx9FFNuxOjSdlvjHDYm6GXe-w1"
    
    # Add sender to the message
    formatted_message = f"From: {sender}\n\n{message}"
    
    severity_icon = {
        "high": "🚨",
        "medium": "⚠️",
        "info": "ℹ️"
    }.get(severity.lower(), "🔔")
    
    title = f"{severity_icon} {title}"
    
    # Create Teams message card format
    teams_payload = {
        "@type": "MessageCard",
        "@context": "http://schema.org/extensions",
        "summary": title,
        "themeColor": "FF0000" if severity == "high" else "FFA500" if severity == "medium" else "0076D7",
        "title": title,
        "text": formatted_message,
        "hideOriginalBody": True,
        "sections": [
            {
                "activityTitle": f"Alert Severity: {severity.capitalize()}",
                "activitySubtitle": f"Sent by: {sender}",
                "facts": [
                    {"name": "Message", "value": message},
                    {"name": "Timestamp", "value": time.strftime("%Y-%m-%d %H:%M:%S UTC")}
                ]
            }
        ],
        "potentialAction": [
            {
                "@type": "OpenUri",
                "name": "View Details",
                "targets": [
                    {"os": "default", "uri": "https://your-dashboard-url.com"}
                ]
            }
        ]
    }
    
    # If an image URL is provided, add it to the card
    if image_url:
        teams_payload["images"] = [
            {
                "image": {
                    "url": image_url
                }
            }
        ]
    
    headers = {
        "Content-Type": "application/json"
    }
    
    try:
        response = requests.post(webhook_url, json=teams_payload, headers=headers)
        response.raise_for_status()
        print(f"Alert sent successfully! Status code: {response.status_code}")
        print(f"Response: {response.text}")
        return True
    except requests.exceptions.RequestException as e:
        print(f"Error sending alert: {e}")
        return False

def process_alerts_from_file(json_file_path, delay_seconds=2):
    """
    Read alerts from JSON file and send them sequentially
    """
    try:
        with open(json_file_path, 'r') as file:
            data = json.load(file)
            
        alerts = data.get('alerts', [])
        total_alerts = len(alerts)
        successful_alerts = 0
        
        print(f"Found {total_alerts} alerts to process")
        
        for i, alert in enumerate(alerts, 1):
            print(f"\nProcessing alert {i}/{total_alerts}")
            image_url = alert.get("image_url", None)  # Add image URL if present in alert data
            if send_alert(
                title=alert.get('title'),
                message=alert.get('message'),
                severity=alert.get('severity', 'info'),
                sender=alert.get('sender'),
                image_url=image_url
            ):
                successful_alerts += 1
            
            # Wait between alerts to avoid overwhelming the server
            if i < total_alerts:  # Don't wait after the last alert
                time.sleep(delay_seconds)
        
        print(f"\nAlert processing complete. {successful_alerts}/{total_alerts} alerts sent successfully.")
    
    except FileNotFoundError:
        print(f"Error: Could not find file {json_file_path}")
    except json.JSONDecodeError:
        print("Error: Invalid JSON format in the alerts file")
    except Exception as e:
        print(f"Unexpected error: {e}")

if __name__ == "__main__":
    # Process alerts from the JSON file
    process_alerts_from_file('alerts.json')

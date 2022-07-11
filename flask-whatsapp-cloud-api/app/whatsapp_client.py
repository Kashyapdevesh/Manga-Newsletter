import requests

import json



class WhatsAppWrapper:

    API_URL = "https://graph.facebook.com/v13.0/"
    API_TOKEN = "EAALF2ZCOnhccBALhVYP3pU4DMchS097EtI0qUs62FNZCT30oURAxjvyu0aV330fXtJvB8E6PZBgjbbpC8e0SZAHr7mGkoP1hchAJkd0ZBmVklcPK1fBzBZCZBPIsuZBORmH0GZC0KPqwX2RcgmNBhWYxZAS2OGKz1iMbQAZACHy3YBu2gbuZBT6IHYraYMiXcHpQyzTd8ZABVLSto4HykPvvPv5yU"
    NUMBER_ID = "105260688923565"
    
    
    def __init__(self):
        self.headers = {
            "Authorization": f"Bearer {self.API_TOKEN}",
            "Content-Type": "application/json",
        }
        self.API_URL = self.API_URL + self.NUMBER_ID

    def send_template_message(self, template_name, language_code, phone_number):

        payload = json.dumps({
            "messaging_product": "whatsapp",
            "to": phone_number,
            "type": "template",
            "template": {
                "name": template_name,
                "language": {
                    "code": language_code
                }
            }
        })

        response = requests.request("POST", f"{self.API_URL}/messages", headers=self.headers, data=payload)

        assert response.status_code == 200, "Error sending message"

        return response.status_code

    def process_webhook_notification(self, data):
        """_summary_: Process webhook notification
        For the moment, this will return the type of notification
        """

        response = []

        for entry in data["entry"]:

            for change in entry["changes"]:
                response.append(
                    {
                        "type": change["field"],
                        "from": change["value"]["metadata"]["display_phone_number"],
                    }
                )

        return response

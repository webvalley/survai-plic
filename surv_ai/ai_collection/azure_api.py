import requests

subscription_key = "39e34da1cca34fa1a7b123c127993502"
text_analytics_base_url = "https://westcentralus.api.cognitive.microsoft.com/text/analytics/v2.1/"
keyphrase_url = text_analytics_base_url + "keyPhrases"

def get_azurekeys(doc):
    documents = {"documents": [
        {"id": "1", "language": "en", "text": doc},
    ]}
    headers = {"Ocp-Apim-Subscription-Key": '39e34da1cca34fa1a7b123c127993502'}  # subscription_key
    response = requests.post(keyphrase_url, headers=headers, json=documents)
    key_phrases = response.json()
    api_phrases = key_phrases['documents'][0]['keyPhrases']
    print(api_phrases)
    return api_phrases
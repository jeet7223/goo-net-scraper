import requests
def translate(text):
    url = "https://s2bu4naau4.execute-api.us-east-1.amazonaws.com/dokolink/translate?text={}&target_lang=en&source_lang=ja".format(text)
    try:
        resp = requests.get(url).json()

        result = resp['translatedText']
        return result
    except:
        print("There is error in translation")
        return text


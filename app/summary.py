import google.generativeai as genai
from flask import current_app


def summarize(articles: list):
    for x in articles:
        print(x)
    if 'GEMINI_API' not in current_app.config or \
            not current_app.config['GEMINI_API']:
        return 'Error: the translation service is not configured.'
    genai.configure(api_key=current_app.config['GEMINI_API'])
    model = genai.GenerativeModel("gemini-1.5-flash")
    proompt = "Kun je een samenvatting maken van twee of drie paragrafen van de volgende lijst van nieuwsberichten. Met nadruk op themas en onderwerpen die vaak terug komen.\n"
    for item in articles:
        proompt += f"* {item}\n"
    proompt += 'Elk thema moet worden benadrukt door er <b> voor en </b> achter te zetten. Elk thema moet op een nieuwe lijn worden begonnen door er <br><br> voor te zetten.'
    response = model.generate_content(proompt)
    print(response.text)
    return response.text

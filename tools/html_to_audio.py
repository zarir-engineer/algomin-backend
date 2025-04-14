# tools/html_to_audio.py
from bs4 import BeautifulSoup
from gtts import gTTS

def extract_selected_text_from_html(html_content, selectors):
    soup = BeautifulSoup(html_content, 'html.parser')
    selected = []
    for selector in selectors:
        for el in soup.select(selector):
            selected.append(el.get_text(strip=True))
    return '\n'.join(selected)

def text_to_audio(text, output_file='output.mp3'):
    tts = gTTS(text=text, lang='en')
    tts.save(output_file)
    return output_file

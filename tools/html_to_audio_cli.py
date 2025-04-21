import argparse
import requests
from bs4 import BeautifulSoup
import yaml
from pathlib import Path
from gtts import gTTS
import os

class InnerworthScraper:
    def __init__(self, config_path="strategies.yml", target_module=None):
        self.base_url = "https://zerodha.com/varsity/module/"
        self.strategy_map = {
            "parse_with_paragraphs_only": self.parse_with_paragraphs_only,
            "parse_with_heading_and_paragraphs": self.parse_with_heading_and_paragraphs
        }
        self.link_strategies = self.load_strategies(config_path, target_module)

    def load_strategies(self, path, target_module):
        with open(path, 'r') as f:
            config = yaml.safe_load(f)

        strategies = []
        for entry in config['link_strategies']:
            module = entry['module']
            if target_module and module != target_module:
                continue
            selector = entry['selector']
            strategy_name = entry.get('strategy', 'parse_with_paragraphs_only')
            strategy_func = self.strategy_map.get(strategy_name, self.parse_with_paragraphs_only)
            full_url = self.base_url + module + "/"
            strategies.append((full_url, selector, strategy_func))
        return strategies

    def fetch_module_page(self, url):
        response = requests.get(url)
        response.raise_for_status()
        return BeautifulSoup(response.text, 'html.parser')

    def extract_links_and_strategies(self):
        links_and_parsers = []

        for base_url, selector, parser_func in self.link_strategies:
            soup = self.fetch_module_page(base_url)
            for a in soup.select(selector):
                href = a.get('href')
                if href:
                    full_url = href if href.startswith("http") else base_url + href
                    links_and_parsers.append((full_url, parser_func))

        return links_and_parsers

    def parse_with_heading_and_paragraphs(self, soup):
        post = soup.select_one('section.chapter-body div.post')
        if not post:
            return ""
        h2 = post.select_one('h2 strong')
        paragraphs = post.select('p span')
        text = []
        if h2:
            text.append(h2.get_text(strip=True))
        text.extend([p.get_text(strip=True) for p in paragraphs])
        return "\n\n".join(text)

    def parse_with_paragraphs_only(self, soup):
        post = soup.select_one('section.chapter-body div.post')
        if not post:
            return ""
        paragraphs = post.select('p')
        return "\n\n".join([p.get_text(strip=True) for p in paragraphs])

    def extract_text_from_chapter(self, url, parser_func):
        response = requests.get(url)
        response.raise_for_status()
        soup = BeautifulSoup(response.text, 'html.parser')
        return parser_func(soup)

    def text_to_audio(self, text, output_path):
        tts = gTTS(text=text, lang='en', slow=False)
        tts.save(output_path)

    def scrape_all(self, audio_output_dir=None):
        links_and_strategies = self.extract_links_and_strategies()
        full_text = []
        audio_files = []

        # Create audio output directory if it doesn't exist
        if audio_output_dir:
            os.makedirs(audio_output_dir, exist_ok=True)

        for i, (url, parser_func) in enumerate(links_and_strategies):
            try:
                print(f"Scraping: {url}")
                chapter_text = self.extract_text_from_chapter(url, parser_func)
                full_text.append(chapter_text)

                # Convert to audio if output directory is specified
                if audio_output_dir:
                    audio_path = os.path.join(audio_output_dir, f"chapter_{i+1}.mp3")
                    self.text_to_audio(chapter_text, audio_path)
                    audio_files.append(audio_path)
                    print(f"Saved audio to {audio_path}")

            except Exception as e:
                print(f"Failed to fetch {url}: {e}")

        return "\n\n---\n\n".join(full_text), audio_files

def main(output_file=None, module=None, audio_output_dir=None):
    scraper = InnerworthScraper(target_module=module)
    extracted_text, audio_files = scraper.scrape_all(audio_output_dir)

    if output_file:
        with open(output_file, 'w', encoding='utf-8') as f:
            f.write(extracted_text)
        print(f"Saved text output to {output_file}")

    if audio_output_dir:
        print(f"Saved {len(audio_files)} audio files to {audio_output_dir}")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Scrape Innerworth or other Varsity modules and extract insights.")
    parser.add_argument("-o", "--output", required=True, help="Output file to save extracted text.")
    parser.add_argument("-m", "--module", required=True, help="Target module to scrape (e.g., innerworth, social-stock-exchanges-sses).")
    parser.add_argument("-a", "--audio", required=True, help="Directory to save audio files. If specified, text will be converted to audio.")
    args = parser.parse_args()
    main(args.output, args.module, args.audio)
import argparse
import requests
from bs4 import BeautifulSoup
import yaml
import os
import pyttsx3
from urllib.parse import urljoin

class InnerworthScraper:
    def __init__(self, config_path="strategies.yml", target_module=None):
        self.base_url = "https://zerodha.com/varsity/module/"
        self.target_module = target_module

        # Define parsing methods first
        self.parse_methods = {
            "parse_with_paragraphs_only": self.parse_with_paragraphs_only,
            "parse_with_heading_and_paragraphs": self.parse_with_heading_and_paragraphs
        }

        self.link_strategies = self.load_strategies(config_path, target_module)

    def parse_with_heading_and_paragraphs(self, soup):
        """Improved parsing with better error handling"""
        try:
            content = soup.find('div', {'class': 'content'}) or soup.find('article') or soup.find('div', {'class': 'post'})
            if not content:
                return ""

            text_parts = []
            for element in content.find_all(['h1', 'h2', 'h3', 'p']):
                if element.name.startswith('h'):
                    text_parts.append(f"\n\n{element.get_text(strip=True).upper()}\n")
                else:
                    text_parts.append(element.get_text(strip=True))

            return "\n".join(text_parts).strip()
        except Exception as e:
            print(f"Parsing error: {e}")
            return ""

    def parse_with_paragraphs_only(self, soup):
        """More robust paragraph extraction"""
        try:
            paragraphs = soup.find_all('p')
            return "\n\n".join(p.get_text(strip=True) for p in paragraphs if p.get_text(strip=True))
        except Exception as e:
            print(f"Paragraph extraction error: {e}")
            return ""

    def load_strategies(self, path, target_module):
        """Enhanced strategy loading with validation"""
        try:
            with open(path, 'r') as f:
                config = yaml.safe_load(f) or {'link_strategies': []}

            strategies = []
            for entry in config.get('link_strategies', []):
                if target_module and entry.get('module') != target_module:
                    continue

                strategy_name = entry.get('strategy', 'parse_with_paragraphs_only')
                strategy_func = self.parse_methods.get(strategy_name, self.parse_with_paragraphs_only)

                full_url = urljoin(self.base_url, entry['module'] + "/")
                strategies.append((
                    full_url,
                    entry['selector'],
                    strategy_func
                ))

            return strategies

        except Exception as e:
            print(f"Config loading error: {e}")
            return []

    def fetch_page(self, url):
        """More resilient page fetching"""
        try:
            headers = {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
            }
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()
            return BeautifulSoup(response.text, 'html.parser')
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")
            return None

    def scrape_all(self, audio_output_dir=None):
        """Improved scraping with better progress tracking"""
        results = []
        audio_files = []
        print('+_++ audio_output_dir ', audio_output_dir)
        if audio_output_dir:
            os.makedirs(audio_output_dir, exist_ok=True)

        for i, (base_url, selector, parse_func) in enumerate(self.link_strategies):
            print(f"\nProcessing strategy {i+1}/{len(self.link_strategies)}")
            print(f"Base URL: {base_url}")
            print(f"Selector: {selector}")

            soup = self.fetch_page(base_url)
            if not soup:
                continue

            links = [urljoin(base_url, a['href']) for a in soup.select(selector) if a.get('href')]
            print(f"Found {len(links)} links")

            for j, url in enumerate(links, 1):
                print(f"\n  Processing link {j}/{len(links)}: {url}")
                chapter_soup = self.fetch_page(url)
                if not chapter_soup:
                    continue

                content = parse_func(chapter_soup)
                if not content.strip():
                    print("  No content found")
                    continue

                results.append(content)
                print(f"  Content length: {len(content)} characters")

                if audio_output_dir:
                    audio_path = os.path.join(audio_output_dir, f"module_{i+1}_chapter_{j}.wav")
                    if self.text_to_audio(content, audio_path):
                        audio_files.append(audio_path)
                        print(f"  Audio saved to {audio_path}")

        return "\n\n---\n\n".join(results), audio_files

    def text_to_audio(self, text, output_path):
        """More reliable audio generation"""
        try:
            if not text.strip():
                return False

            engine = pyttsx3.init()

            # Configure voice
            voices = engine.getProperty('voices')
            if len(voices) > 1:
                engine.setProperty('voice', voices[1].id)  # Female voice if available

            engine.setProperty('rate', 175)  # Optimal speaking rate
            engine.setProperty('volume', 0.9)  # Slightly reduced volume

            # Ensure output directory exists
            os.makedirs(os.path.dirname(output_path), exist_ok=True)

            # Save as WAV
            if not output_path.lower().endswith('.wav'):
                output_path = os.path.splitext(output_path)[0] + '.wav'

            engine.save_to_file(text, output_path)
            engine.runAndWait()
            return os.path.exists(output_path)

        except Exception as e:
            print(f"Audio generation error: {e}")
            return False

def main(output_file=None, module=None, audio_output_dir=None):
    print("\nStarting scraping process...")
    print(f"Target module: {module}")
    print(f"Text output: {output_file}")
    print(f"Audio output: {audio_output_dir or 'None'}")

    scraper = InnerworthScraper(target_module=module)
    extracted_text, audio_files = scraper.scrape_all(audio_output_dir)
    print('+++ extracted_text, audio_files ', extracted_text, audio_files)
    if output_file:
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                f.write(extracted_text)
            print(f"\nSuccessfully saved text to {output_file}")
            print(f"Total characters: {len(extracted_text)}")
        except Exception as e:
            print(f"\nFailed to save text output: {e}")

    if audio_output_dir:
        print(f"\nSaved {len(audio_files)} audio files to {audio_output_dir}")
        if not audio_files:
            print("Warning: No audio files were generated")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Advanced web scraper with audio conversion")
    parser.add_argument("-o", "--output", required=True, help="Path for text output file")
    parser.add_argument("-m", "--module", required=True, help="Target module to scrape")
    parser.add_argument("-a", "--audio", help="Directory for audio output (optional)")

    args = parser.parse_args()

    # Normalize paths
    args.output = os.path.abspath(args.output)
    if args.audio:
        args.audio = os.path.abspath(args.audio)

    main(args.output, args.module, args.audio)
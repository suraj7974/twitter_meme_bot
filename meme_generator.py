import os
import requests
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

load_dotenv()


class MemeGenerator:
    def __init__(self):
        try:
            print("Initializing MemeGenerator...")
            api_key = os.getenv("GROQ_API_KEY")
            if not api_key:
                raise ValueError(
                    "Error: GROQ_API_KEY environment variable is not set.")
            self.groq_client = Groq(api_key=api_key)

            self.output_dir = "memes"
            self.font_path = "fonts/DejaVuSans-Bold.ttf"

            if not os.path.exists(self.font_path):
                raise FileNotFoundError(
                    f"Error: Font file not found at {self.font_path}. Please ensure the font file exists.")

            os.makedirs(self.output_dir, exist_ok=True)
            print("Initialization complete.")
        except Exception as e:
            print(f"Error during MemeGenerator initialization: {e}")

    def get_meme_template(self):
        try:
            print("Fetching meme template...")
            response = requests.get("https://api.imgflip.com/get_memes")
            response.raise_for_status()
            memes = response.json().get('data', {}).get('memes', [])
            if memes:
                template = random.choice(memes)
                print(
                    f"Template fetched: URL={template['url']}, Width={template['width']}, Height={template['height']}")
                return template['url'], template['width'], template['height']
            else:
                print("Error: No meme templates found.")
                return None, None, None
        except (requests.RequestException, ValueError) as e:
            print(f"Error fetching meme template: {e}")
            return None, None, None

    def generate_meme_text(self, trend, company_theme="Resume Building"):
        try:
            print(
                f"Generating meme text for trend: '{trend}' with theme: '{company_theme}'")
            prompt = f"""
                Generate a hinglish style humorous two-line meme text that relates to the trending topic "{trend}" and 
                incorporates the theme of "{company_theme}". Ensure that the text is witty and relevant to
                job searching or resume building.
                Provide only the text itself—no prefixes, labels, or extra formatting.
            """
            chat_completion = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.7,
                max_tokens=100,
            )
            response_text = chat_completion.choices[0].message.content.strip()
            lines = response_text.split('\n')
            top_text = lines[0] if len(lines) > 0 else ""
            bottom_text = lines[1] if len(lines) > 1 else ""
            print(f"Generated text - Top: {top_text}, Bottom: {bottom_text}")
            return top_text, bottom_text
        except requests.exceptions.RequestException as e:
            print(f"Network error occurred during Groq API call: {e}")
            return "Error generating meme text.", "Try again later."
        except Exception as e:
            print(f"Error generating meme text: {e}")
            return "Error generating meme text.", "Try again later."

    def get_font_size(self, img, text, max_width_ratio=0.9):
        try:
            print("Calculating font size for text fitting...")
            font_size = int(img.height * 0.1)
            font = ImageFont.truetype(self.font_path, font_size)
            text_width = font.getlength(text)

            while text_width > (img.width * max_width_ratio) and font_size > 10:
                font_size -= 1
                font = ImageFont.truetype(self.font_path, font_size)
                text_width = font.getlength(text)

            print(f"Calculated font size: {font_size}")
            return font_size
        except Exception as e:
            print(f"Error calculating font size: {e}")
            return 20

    def load_font(self, font_size):
        """Attempts to load the font and returns a fallback if it fails."""
        try:
            return ImageFont.truetype(self.font_path, font_size)
        except Exception as e:
            print(f"Error loading font: {e}")
            return ImageFont.load_default()

    def wrap_text_dynamically(self, text, font, max_width):
        print("Wrapping text dynamically to fit within max width...")
        words = text.split()
        lines = []
        current_line = []

        try:
            for word in words:
                current_line.append(word)
                line_width = font.getlength(' '.join(current_line))
                if line_width > max_width:
                    if len(current_line) == 1:
                        lines.append(current_line[0])
                        current_line = []
                    else:
                        current_line.pop()
                        lines.append(' '.join(current_line))
                        current_line = [word]

            if current_line:
                lines.append(' '.join(current_line))

            print(f"Wrapped text: {lines}")
            return lines
        except Exception as e:
            print(f"Error wrapping text dynamically: {e}")
            return [text]

    def create_meme(self, trend, company_theme="Resume Building"):
        print("Creating meme...")
        template_url, width, height = self.get_meme_template()
        if not template_url:
            print("Template not found. Cannot create meme.")
            return None

        try:
            response = requests.get(template_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            print("Template image downloaded successfully.")
        except requests.RequestException as e:
            print(f"Error downloading meme template image: {e}")
            return None
        except Exception as e:
            print(f"Error opening image: {e}")
            return None

        try:
            draw = ImageDraw.Draw(img)

            top_text, bottom_text = self.generate_meme_text(
                trend, company_theme)
            longest_text = max(top_text, bottom_text, key=len)
            font_size = self.get_font_size(img, longest_text)
            font = self.load_font(font_size)

            margin = int(img.width * 0.05)
            max_text_width = img.width - (2 * margin)

            top_lines = self.wrap_text_dynamically(
                top_text, font, max_text_width)
            line_height = int(font_size * 1.2)
            y_position = margin

            for line in top_lines:
                text_width = font.getlength(line)
                x_position = (img.width - text_width) // 2
                draw.text(
                    (x_position, y_position),
                    line,
                    font=font,
                    fill="white",
                    stroke_width=3,
                    stroke_fill="black"
                )
                y_position += line_height

            bottom_lines = self.wrap_text_dynamically(
                bottom_text, font, max_text_width)
            bottom_total_height = len(bottom_lines) * line_height
            y_position = img.height - bottom_total_height - margin

            for line in bottom_lines:
                text_width = font.getlength(line)
                x_position = (img.width - text_width) // 2
                draw.text(
                    (x_position, y_position),
                    line,
                    font=font,
                    fill="white",
                    stroke_width=3,
                    stroke_fill="black"
                )
                y_position += line_height

            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/meme_{trend.split()[0].replace(' ', '_')}_{timestamp}.png"
            img.save(filename)
            print(f"Meme saved as {filename}")
            return filename
        except Exception as e:
            print(f"Error creating meme: {e}")
            return None

    def run_demo(self):
        """Runs a demonstration of the entire meme generation process with debug output."""
        print("\nRunning MemeGenerator Demo...")

        template_url, width, height = self.get_meme_template()
        print(
            f"Template URL: {template_url}, Width: {width}, Height: {height}")

        top_text, bottom_text = self.generate_meme_text("AI Trends")
        print(f"Top Text: {top_text}")
        print(f"Bottom Text: {bottom_text}")

        filename = self.create_meme("AI Trends", "Resume Building")
        print(f"Generated Meme File: {filename}")


if __name__ == "__main__":
    generator = MemeGenerator()
    generator.run_demo()

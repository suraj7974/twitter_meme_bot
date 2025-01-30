import os
import requests
from PIL import Image, ImageDraw, ImageFont
import random
from io import BytesIO
from datetime import datetime
from groq import Groq
from dotenv import load_dotenv

class MemeGenerator:
    """
    A class to generate memes using Groq AI models and the Imgflip API.
    
    This class combines AI-generated text with meme templates to create custom memes.
    It supports Hinglish text generation and handles image processing with proper text
    placement and styling.
    """

    def __init__(self):
        """
        Initialize the MemeGenerator with necessary configurations and API clients.
        Sets up directories, fonts, and API connections.
        """
        self._initialize_environment()
        self._setup_directories()
        
    def _initialize_environment(self):
        """Set up API clients and load environment variables."""
        load_dotenv()
        api_key = os.getenv("GROQ_API_KEY")
        if not api_key:
            raise ValueError("GROQ_API_KEY environment variable is not set.")
        
        self.groq_client = Groq(api_key=api_key)
        self.font_path = "fonts/DejaVuSans-Bold.ttf"
        
        if not os.path.exists(self.font_path):
            raise FileNotFoundError(
                f"Font file not found at {self.font_path}. Please ensure the font file exists."
            )

    def _setup_directories(self):
        """Create necessary directories for storing generated memes."""
        self.output_dir = "memes"
        os.makedirs(self.output_dir, exist_ok=True)

    def get_meme_template(self):
        """
        Fetch a random meme template from the Imgflip API.
        
        Returns:
            tuple: (template_url, width, height) or (None, None, None) if failed
        """
        try:
            response = requests.get("https://api.imgflip.com/get_memes")
            response.raise_for_status()
            memes = response.json().get('data', {}).get('memes', [])

            if not memes:
                print("No meme templates found.")
                return None, None, None

            # Keep selecting templates until we find one in landscape orientation
            while True:
                template = random.choice(memes)
                width, height = template['width'], template['height']
                
                # Check for landscape orientation (width significantly larger than height)
                if width >= height:
                    return template['url'], width, height
                
        except requests.RequestException as e:
            print(f"Failed to fetch meme template: {e}")
            return None, None, None

    def generate_meme_text(self, trend, company_theme="Resume Building"):
        """
        Generate two lines of Hinglish meme text using Groq API.
        
        Args:
            trend (str): The trending topic to base the meme on
            company_theme (str): Theme for contextualizing the meme
            
        Returns:
            tuple: (top_text, bottom_text)
        """
        try:
            prompt = f"""
                Generate a hinglish style humorous and very funny two-line meme text that relates to the trending topic "{trend}" and 
                incorporates the theme of "{company_theme}". Ensure that the text is witty and relevant to
                job searching or resume building.
                Provide only the text itself—no prefixes, labels, or extra formatting.
            """
            
            response = self.groq_client.chat.completions.create(
                messages=[{"role": "user", "content": prompt}],
                model="llama-3.1-70b-versatile",
                temperature=0.7,
                max_tokens=100,
            )
            
            text = response.choices[0].message.content.strip()
            return self._process_generated_text(text)
            
        except Exception as e:
            print(f"Error generating meme text: {e}")
            return "Error generating meme text.", "Please try again."

    def _process_generated_text(self, text):
        """
        Process the generated text into two lines.
        
        Args:
            text (str): Raw generated text
            
        Returns:
            tuple: (top_text, bottom_text)
        """
        lines = [line.strip() for line in text.split('\n') if line.strip()]
        
        if len(lines) != 2:
            if len(lines) == 1:
                text = lines[0]
                # Try splitting on punctuation
                for separator in ['. ', '? ', '! ', '| ']:
                    if separator in text:
                        parts = text.split(separator, 1)
                        return parts[0].strip(), parts[1].strip()
                
                # If no punctuation, split at midpoint
                words = text.split()
                mid = len(words) // 2
                return ' '.join(words[:mid]), ' '.join(words[mid:])
        
        return lines[0], lines[1] if len(lines) > 1 else "Please try again"

    def _calculate_font_size(self, img, text, max_width_ratio=0.80):
        """
        Calculate the optimal font size for the given text and image dimensions.
        Sizes are now smaller compared to the original version.
        
        Args:
            img: PIL Image object
            text (str): Text to be rendered
            max_width_ratio (float): Maximum width ratio for text
            
        Returns:
            int: Optimal font size
        """
        # Reduced size percentages for smaller text
        initial_size = int(img.height * 0.12)  # Reduced from 0.15
        min_size = int(img.height * 0.06)      # Reduced from 0.08
        max_size = int(img.height * 0.15)      # Reduced from 0.20
        
        font_size = min(initial_size, max_size)
        
        while font_size > min_size:
            font = ImageFont.truetype(self.font_path, font_size)
            if font.getlength(text) <= (img.width * max_width_ratio):
                break
            font_size -= 2
            
        return font_size

    def _wrap_text(self, text, font, max_width):
        """
        Wrap text to fit within the specified width.
        
        Args:
            text (str): Text to wrap
            font: PIL ImageFont object
            max_width (int): Maximum width in pixels
            
        Returns:
            list: Lines of wrapped text
        """
        words = text.split()
        lines = []
        current_line = []
        
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
            
        return lines

    def _draw_text_with_outline(self, draw, text, x, y, font, stroke_width):
        """
        Draw text with outline effect.
        
        Args:
            draw: PIL ImageDraw object
            text (str): Text to draw
            x, y (int): Coordinates for text placement
            font: PIL ImageFont object
            stroke_width (int): Width of the outline
        """
        # Draw outline with smaller offset for smaller text
        offsets = [(1, 1), (-1, -1), (1, -1), (-1, 1)]  # Reduced from 2 to 1
        for offset_x, offset_y in offsets:
            draw.text(
                (x + offset_x, y + offset_y),
                text,
                font=font,
                fill="black"
            )
        
        # Draw main text
        draw.text(
            (x, y),
            text,
            font=font,
            fill="white",
            stroke_width=stroke_width,
            stroke_fill="black"
        )

    def create_meme(self, trend, company_theme="Resume Building"):
        """
        Create a meme by combining template and generated text.
        
        Args:
            trend (str): Trending topic for the meme
            company_theme (str): Theme for contextualizing the meme
            
        Returns:
            str: Path to the generated meme file, or None if failed
        """
        template_url, width, height = self.get_meme_template()
        if not template_url:
            return None

        try:
            # Load and prepare image
            response = requests.get(template_url)
            response.raise_for_status()
            img = Image.open(BytesIO(response.content))
            
            # Ensure minimum image size
            min_size = 800
            if img.width < min_size or img.height < min_size:
                ratio = max(min_size / img.width, min_size / img.height)
                new_size = (int(img.width * ratio), int(img.height * ratio))
                img = img.resize(new_size, Image.Resampling.LANCZOS)

            # Generate text and prepare drawing
            top_text, bottom_text = self.generate_meme_text(trend, company_theme)
            draw = ImageDraw.Draw(img)
            
            # Calculate text parameters
            longest_text = max(top_text, bottom_text, key=len)
            font_size = self._calculate_font_size(img, longest_text)
            font = ImageFont.truetype(self.font_path, font_size)
            
            # Calculate layout parameters with adjusted margins
            margin = int(img.height * 0.06)  # Increased from 0.05 for better spacing
            max_text_width = img.width - (2 * margin)
            line_height = int(font_size * 1.3)  # Reduced from 1.4 for tighter spacing
            stroke_width = max(2, int(font_size * 0.04))  # Reduced from 0.05

            # Draw top text
            y_position = margin
            for line in self._wrap_text(top_text, font, max_text_width):
                x_position = (img.width - font.getlength(line)) // 2
                self._draw_text_with_outline(draw, line, x_position, y_position, font, stroke_width)
                y_position += line_height

            # Draw bottom text
            bottom_lines = self._wrap_text(bottom_text, font, max_text_width)
            y_position = img.height - margin - (len(bottom_lines) * line_height)
            for line in bottom_lines:
                x_position = (img.width - font.getlength(line)) // 2
                self._draw_text_with_outline(draw, line, x_position, y_position, font, stroke_width)
                y_position += line_height

            # Save the meme
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            filename = f"{self.output_dir}/meme_{trend.split()[0].replace(' ', '_')}_{timestamp}.png"
            img.save(filename)
            return filename

        except Exception as e:
            print(f"Error creating meme: {e}")
            return None

    def run_demo(self):
        """Run a demonstration of the meme generation process."""
        print("\nRunning MemeGenerator Demo...")
        
        # Generate and save a meme
        filename = self.create_meme("AI Trends", "Resume Building")
        
        if filename:
            print(f"Successfully generated meme: {filename}")
        else:
            print("Failed to generate meme")


if __name__ == "__main__":
    try:
        generator = MemeGenerator()
        generator.run_demo()
    except Exception as e:
        print(f"Error running MemeGenerator: {e}")
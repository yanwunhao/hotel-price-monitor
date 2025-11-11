from dotenv import load_dotenv
from datetime import datetime, timedelta
from utils.booking import fetch_hotel_table
from utils.deepseek import parse_table_to_markdown

load_dotenv(override=True)

hotel_list = ["yuzawa-grand.ja.html", "yuzawa-toei-hotel.ja.html", "futaba.ja.html"]

# rest: 越後湯沢温泉さくら亭, Takinoyu

# Example usage
hotel_path = "yuzawa-toei-hotel.ja.html"
today = datetime.now()
checkin = today.strftime("%Y-%m-%d")
checkout = (today + timedelta(days=1)).strftime("%Y-%m-%d")
wait_seconds = 20

try:
    # Fetch and clean the hotel pricing table
    print(f"Fetching hotel table for {hotel_path}...")
    clean_table = fetch_hotel_table(hotel_path, checkin, checkout, wait_seconds)

    # Parse table to Markdown using DeepSeek
    print("\nParsing table to Markdown using DeepSeek...")
    markdown_table = parse_table_to_markdown(clean_table)

    print("\n" + "=" * 80)
    print("MARKDOWN TABLE (Parsed by DeepSeek):")
    print("=" * 80)
    print(markdown_table)
    print("=" * 80)

except ValueError as e:
    print(f"Error: {e}")
except Exception as e:
    print(f"Unexpected error: {e}")

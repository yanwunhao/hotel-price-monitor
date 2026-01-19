from dotenv import load_dotenv
from datetime import datetime, timedelta
from utils.booking import fetch_hotel_table
from utils.deepseek import parse_table_to_markdown

load_dotenv(override=True)

hotel_list = ["yuzawa-grand.ja.html", "yuzawa-toei-hotel.ja.html", "futaba.ja.html"]

# rest: 越後湯沢温泉さくら亭, Takinoyu


def fetch_hotel_prices(
    hotel_path: str, start_date: datetime, end_date: datetime, wait_seconds: int = 20
):
    """
    Fetch hotel prices for a date range.

    Args:
        hotel_path: The hotel path after /jp/ (e.g., "yuzawa-grand.ja.html")
        start_date: Start date (inclusive)
        end_date: End date (exclusive)
        wait_seconds: Seconds to wait for page to load (default: 20)
    """
    current_date = start_date
    while current_date <= end_date:
        checkin = current_date.strftime("%Y-%m-%d")
        checkout = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")

        print(f"\n{'=' * 80}")
        print(f"Date: {checkin}")
        print(f"{'=' * 80}")

        try:
            print(f"Fetching hotel table for {hotel_path}...")
            clean_table = fetch_hotel_table(hotel_path, checkin, checkout, wait_seconds)

            if clean_table is None:
                print("No vacancy, skipping...")
            else:
                print("\nParsing table to Markdown using DeepSeek...")
                markdown_table = parse_table_to_markdown(clean_table)

                print("\nMARKDOWN TABLE (Parsed by DeepSeek):")
                print(markdown_table)

        except Exception as e:
            print(f"Unexpected error: {e}")

        current_date += timedelta(days=1)


if __name__ == "__main__":
    fetch_hotel_prices(
        hotel_path="yuzawa-grand.ja.html",
        start_date=datetime(2026, 2, 25),
        end_date=datetime(2026, 2, 27),
        wait_seconds=20,
    )

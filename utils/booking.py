import time
from bs4 import BeautifulSoup
from selenium import webdriver


def fetch_hotel_table(hotel_path: str, checkin: str, checkout: str, wait_seconds: int = 10) -> BeautifulSoup:
    """
    Fetch hotel pricing table from Booking.com

    Args:
        hotel_path: The hotel path after /jp/ (e.g., "yuzawa-toei-hotel.ja.html")
        checkin: Check-in date in format YYYY-MM-DD (e.g., "2025-11-11")
        checkout: Check-out date in format YYYY-MM-DD (e.g., "2025-11-12")
        wait_seconds: Seconds to wait for page to load (default: 10)

    Returns:
        BeautifulSoup | None: Cleaned table element containing "本日の料金" (today's price),
                              or None if no rooms available
    """
    # Initialize Chrome driver
    driver = webdriver.Chrome()

    try:
        # Build URL
        url = f"https://www.booking.com/hotel/jp/{hotel_path}?checkin={checkin}&checkout={checkout}"
        driver.get(url)

        # Wait for page to load
        time.sleep(wait_seconds)

        # Get page HTML source
        html_content = driver.page_source

        # Parse HTML with BeautifulSoup
        soup = BeautifulSoup(html_content, "html.parser")

        # Find table with header containing "本日の料金"
        target_table = None
        all_tables = soup.find_all("table")

        for table in all_tables:
            # Check if table header contains "本日の料金"
            headers = table.find_all(["th", "td"])
            for header in headers:
                if "本日の料金" in header.get_text(strip=True):
                    target_table = table
                    break
            if target_table:
                break

        if not target_table:
            return None  # No rooms available

        # Create a deep copy of the table
        clean_table = BeautifulSoup(str(target_table), "html.parser").find("table")

        # Remove hidden elements, scripts, styles, SVGs, etc.
        for element in clean_table.find_all(["script", "style", "svg", "noscript", "iframe"]):
            element.decompose()

        # Remove elements with hidden attribute or display:none
        to_remove = []
        for element in clean_table.find_all(True):
            if element.has_attr("hidden"):
                to_remove.append(element)
                continue
            style = element.get("style", "") or ""
            if "display:none" in style.replace(" ", "") or "display: none" in style:
                to_remove.append(element)
        for element in to_remove:
            element.decompose()

        # Remove all attributes from remaining elements to reduce size
        for element in clean_table.find_all(True):
            element.attrs = {}

        return clean_table

    finally:
        driver.quit()

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
        BeautifulSoup: Cleaned table element containing "本日の料金" (today's price)

    Raises:
        ValueError: If table with "本日の料金" is not found
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
            raise ValueError("Table with '本日の料金' not found!")

        # Create a clean copy of the table without style attributes
        clean_table = target_table.__copy__()

        # Remove all style attributes from all elements
        for element in clean_table.find_all(True):
            # Remove style attribute
            if element.has_attr("style"):
                del element["style"]
            # Remove class attribute
            if element.has_attr("class"):
                del element["class"]
            # Remove inline styling attributes
            attrs_to_remove = [
                "width",
                "height",
                "bgcolor",
                "align",
                "valign",
                "border",
                "cellpadding",
                "cellspacing",
            ]
            for attr in attrs_to_remove:
                if element.has_attr(attr):
                    del element[attr]

        return clean_table

    finally:
        driver.quit()

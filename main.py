import time
import os

from dotenv import load_dotenv
from bs4 import BeautifulSoup
from openai import OpenAI
from selenium import webdriver

load_dotenv(override=True)

# Initialize Chrome driver
driver = webdriver.Chrome()
driver.get(
    "https://www.booking.com/hotel/jp/yuzawa-toei-hotel.ja.html?checkin=2025-11-11&checkout=2025-11-12"
)

# Wait for page to load
time.sleep(10)

# Get page HTML source
html_content = driver.page_source

# Parse HTML with BeautifulSoup
soup = BeautifulSoup(html_content, "html.parser")

# Print page title
print("Page Title:", soup.title.string)

# Find table with header containing "本日の料金" (Today's price)
target_table = None
all_tables = soup.find_all("table")

print(f"\nFound {len(all_tables)} tables in total")

for table in all_tables:
    # Check if table header contains "本日の料金"
    headers = table.find_all(["th", "td"])
    for header in headers:
        if "本日の料金" in header.get_text(strip=True):
            target_table = table
            print("\nFound target table with '本日の料金'!")
            break
    if target_table:
        break

# Print the table if found
if target_table:
    print("\n" + "=" * 80)
    print("TABLE CONTENT:")
    print("=" * 80)

    # Extract all rows
    rows = target_table.find_all("tr")
    for i, row in enumerate(rows):
        cells = row.find_all(["th", "td"])
        row_data = [cell.get_text(strip=True) for cell in cells]
        print(f"Row {i}: {' | '.join(row_data)}")

    print("=" * 80)

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
        # Remove id attribute (optional, uncomment if needed)
        # if element.has_attr('id'):
        #     del element['id']
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

    # Print clean HTML of the table
    print("\nCLEAN HTML (without styles):")
    print(clean_table.prettify())

    # Use DeepSeek to parse table and convert to Markdown
    client = OpenAI(
        api_key=os.environ.get("DEEPSEEK_API_KEY"), base_url="https://api.deepseek.com"
    )

    # Load prompt template from file
    with open("table_parser_prompt.txt", "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Replace placeholder with actual table HTML
    prompt = prompt_template.replace("{table_html}", clean_table.prettify())

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的数据解析助手，擅长将复杂的HTML表格转换为简洁明了的Markdown格式。",
            },
            {"role": "user", "content": prompt},
        ],
        stream=False,
    )

    print("\n" + "=" * 80)
    print("MARKDOWN TABLE (Parsed by DeepSeek):")
    print("=" * 80)
    print(response.choices[0].message.content)
    print("=" * 80)
else:
    print("\nTable with '本日の料金' not found!")
    print("Available text in first few tables:")
    for i, table in enumerate(all_tables[:3]):
        print(f"\nTable {i}: {table.get_text(strip=True)[:200]}...")

driver.quit()

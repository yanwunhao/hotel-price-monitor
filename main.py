import csv
import os
from dotenv import load_dotenv
from datetime import datetime, timedelta
from utils.booking import fetch_hotel_table
from utils.deepseek import get_min_price, parse_table_detail

load_dotenv(override=True)

hotel_list = [
    "yuzawa-grand.ja.html",
    "yuzawa-toei-hotel.ja.html",
    "otowaya-ryokan.ja.html",
]

# rest: 越後湯沢温泉さくら亭, Takinoyu


def fetch_hotel_prices(
    hotel_path: str,
    start_date: datetime,
    end_date: datetime,
    output_file: str,
    wait_seconds: int = 20,
) -> dict[str, str]:
    """
    Fetch hotel prices for a date range and save to a file.

    Args:
        hotel_path: The hotel path after /jp/ (e.g., "yuzawa-grand.ja.html")
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        output_file: Path to the output txt file
        wait_seconds: Seconds to wait for page to load (default: 20)

    Returns:
        dict: {date_str: min_price or "×"}
    """
    results = {}

    with open(output_file, "w", encoding="utf-8") as f:
        current_date = start_date
        while current_date <= end_date:
            checkin = current_date.strftime("%Y-%m-%d")
            checkout = (current_date + timedelta(days=1)).strftime("%Y-%m-%d")

            print(f"\n{'=' * 80}")
            print(f"Date: {checkin}")
            print(f"{'=' * 80}")

            f.write(f"\n{'=' * 80}\n")
            f.write(f"Date: {checkin}\n")
            f.write(f"{'=' * 80}\n")

            try:
                print(f"Fetching hotel table for {hotel_path}...")
                clean_table = fetch_hotel_table(
                    hotel_path, checkin, checkout, wait_seconds
                )

                if clean_table is None:
                    print("No vacancy, skipping...")
                    f.write("No vacancy\n")
                    results[checkin] = "×"
                else:
                    # Get minimum price
                    print("Getting minimum price...")
                    min_price = get_min_price(clean_table)
                    print(f"Min price: {min_price}")
                    f.write(f"Min price: {min_price}\n")
                    results[checkin] = min_price

                    # Get detailed info
                    print("Getting detailed info...")
                    detail = parse_table_detail(clean_table)
                    print(f"\nDetail:\n{detail}")
                    f.write(f"\nDetail:\n{detail}\n")

            except Exception as e:
                print(f"Unexpected error: {e}")
                f.write(f"Unexpected error: {e}\n")
                results[checkin] = "error"

            current_date += timedelta(days=1)

    print(f"\nOutput saved to {output_file}")
    return results


def fetch_multiple_hotels(
    hotel_list: list[str],
    start_date: datetime,
    end_date: datetime,
    csv_file: str,
    log_dir: str = "logs",
    wait_seconds: int = 20,
):
    """
    Fetch prices for multiple hotels and generate a CSV summary.

    Args:
        hotel_list: List of hotel paths
        start_date: Start date (inclusive)
        end_date: End date (inclusive)
        csv_file: Path to the output CSV file
        log_dir: Directory for individual hotel log files
        wait_seconds: Seconds to wait for page to load
    """
    os.makedirs(log_dir, exist_ok=True)

    all_results = {}

    for hotel_path in hotel_list:
        hotel_name = hotel_path.replace(".ja.html", "")
        output_file = os.path.join(log_dir, f"{hotel_name}.txt")

        print(f"\n{'#' * 80}")
        print(f"# Processing: {hotel_name}")
        print(f"{'#' * 80}")

        results = fetch_hotel_prices(
            hotel_path=hotel_path,
            start_date=start_date,
            end_date=end_date,
            output_file=output_file,
            wait_seconds=wait_seconds,
        )
        all_results[hotel_name] = results

    # Generate CSV
    dates = []
    current_date = start_date
    while current_date <= end_date:
        dates.append(current_date.strftime("%Y-%m-%d"))
        current_date += timedelta(days=1)

    hotel_names = [h.replace(".ja.html", "") for h in hotel_list]

    with open(csv_file, "w", encoding="utf-8", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["Date"] + hotel_names)
        for date in dates:
            row = [date]
            for hotel_name in hotel_names:
                row.append(all_results.get(hotel_name, {}).get(date, ""))
            writer.writerow(row)

    print(f"\n{'#' * 80}")
    print(f"CSV saved to {csv_file}")
    print(f"{'#' * 80}")


if __name__ == "__main__":
    fetch_multiple_hotels(
        hotel_list=hotel_list,
        start_date=datetime(2026, 2, 1),
        end_date=datetime(2026, 3, 31),
        csv_file="hotel_prices.csv",
        log_dir="logs",
        wait_seconds=20,
    )

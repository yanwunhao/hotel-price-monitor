import os
from bs4 import BeautifulSoup
from openai import OpenAI


def _get_client() -> OpenAI:
    """Get DeepSeek client."""
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set")
    return OpenAI(api_key=api_key, base_url="https://api.deepseek.com")


def get_min_price(table: BeautifulSoup, prompt_file: str = "min_price_prompt.txt") -> str:
    """
    Extract minimum price from HTML table using DeepSeek API.

    Args:
        table: BeautifulSoup table element to parse
        prompt_file: Path to the prompt template file

    Returns:
        str: Minimum price (e.g., "¥12,000") or "×" if not found
    """
    client = _get_client()

    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    table_html = table.prettify()
    prompt = prompt_template.replace("{table_html}", table_html)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {"role": "system", "content": "你是一个数据提取助手，只返回请求的数据，不要有其他文字。"},
            {"role": "user", "content": prompt},
        ],
        stream=False,
    )

    return response.choices[0].message.content.strip()


def parse_table_detail(table: BeautifulSoup, prompt_file: str = "table_parser_prompt.txt") -> str:
    """
    Parse HTML table to detailed summary using DeepSeek API.

    Args:
        table: BeautifulSoup table element to parse
        prompt_file: Path to the prompt template file

    Returns:
        str: Detailed summary of room information
    """
    client = _get_client()

    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    table_html = table.prettify()
    prompt = prompt_template.replace("{table_html}", table_html)

    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的数据解析助手,擅长将复杂的HTML表格转换为简洁明了的文本描述。",
            },
            {"role": "user", "content": prompt},
        ],
        stream=False,
    )

    return response.choices[0].message.content

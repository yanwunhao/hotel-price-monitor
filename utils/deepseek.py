import os
from bs4 import BeautifulSoup
from openai import OpenAI


def parse_table_to_markdown(table: BeautifulSoup, prompt_file: str = "table_parser_prompt.txt") -> str:
    """
    Parse HTML table to Markdown format using DeepSeek API

    Args:
        table: BeautifulSoup table element to parse
        prompt_file: Path to the prompt template file (default: "table_parser_prompt.txt")

    Returns:
        str: Markdown formatted table string

    Raises:
        FileNotFoundError: If prompt template file is not found
        ValueError: If DEEPSEEK_API_KEY environment variable is not set
    """
    # Check API key
    api_key = os.environ.get("DEEPSEEK_API_KEY")
    if not api_key:
        raise ValueError("DEEPSEEK_API_KEY environment variable is not set")

    # Initialize DeepSeek client
    client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")

    # Load prompt template from file
    with open(prompt_file, "r", encoding="utf-8") as f:
        prompt_template = f.read()

    # Replace placeholder with actual table HTML
    table_html = table.prettify()
    prompt = prompt_template.replace("{table_html}", table_html)

    # Call DeepSeek API
    response = client.chat.completions.create(
        model="deepseek-chat",
        messages=[
            {
                "role": "system",
                "content": "你是一个专业的数据解析助手,擅长将复杂的HTML表格转换为简洁明了的Markdown格式。",
            },
            {"role": "user", "content": prompt},
        ],
        stream=False,
    )

    return response.choices[0].message.content

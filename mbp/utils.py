from datetime import datetime


def get_formatted_year(raw_year: int) -> str:
    dt = datetime.strptime(str(raw_year), "%Y")
    return f"{raw_year}-{str(int(dt.strftime('%y')) + 1)}"

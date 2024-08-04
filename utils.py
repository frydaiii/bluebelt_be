from urllib.parse import urlparse
from datetime import datetime, time
import requests
import pytz


def is_url(url: str) -> bool:
    try:
        result = urlparse(url)
        return all([result.scheme, result.netloc])
    except ValueError:
        return False


def is_downloadable(url: str) -> bool:
    h = requests.head(url, allow_redirects=True)
    header = h.headers
    content_type = header.get('content-type')
    if 'text' in content_type.lower():
        return False
    if 'html' in content_type.lower():
        return False
    return True


def is_now_between_range_in_timezone(start_time: str, end_time: str,
                                     timezone: str) -> bool:
    current_time = datetime.now(pytz.timezone(timezone)).time()
    start_time_hour, start_time_minute = [int(e) for e in start_time.split(":")]
    end_time_hour, end_time_minute = [int(e) for e in end_time.split(":")]
    start_time = time(start_time_hour, start_time_minute)
    end_time = time(end_time_hour, end_time_minute)
    return start_time <= current_time <= end_time

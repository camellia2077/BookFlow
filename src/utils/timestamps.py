from datetime import datetime, timedelta, timezone


BEIJING_TIMEZONE = timezone(timedelta(hours=8))


def get_beijing_timestamp_for_filename():
    # Windows filenames cannot contain ":" characters, so we keep the ISO 8601
    # structure while replacing time separators with "-" for filesystem safety.
    return datetime.now(BEIJING_TIMEZONE).strftime("%Y-%m-%dT%H-%M-%S+08-00")


def build_timestamped_filename(base_name, extension):
    timestamp = get_beijing_timestamp_for_filename()
    return f"{base_name}_{timestamp}.{extension.lstrip('.')}"

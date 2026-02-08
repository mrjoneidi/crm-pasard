
import os
import uuid
from flask import current_app
from datetime import datetime, date
import jdatetime

def save_file(file):
    if not file:
        return None

    filename = f"{uuid.uuid4()}_{file.filename}"
    upload_folder = current_app.config['UPLOAD_FOLDER']
    file_path = os.path.join(upload_folder, filename)
    file.save(file_path)
    return filename # Return relative path for DB

def gregorian_to_jalali(date_obj):
    """Converts a Gregorian date object to a Jalali string (YYYY/MM/DD)."""
    if not date_obj:
        return None
    j_date = jdatetime.date.fromgregorian(date=date_obj)
    return j_date.strftime('%Y/%m/%d')

def jalali_to_gregorian(jalali_str):
    """Converts a Jalali date string (YYYY/MM/DD or YYYY-MM-DD) to a Gregorian date object."""
    if not jalali_str:
        return None
    try:
        jalali_str = jalali_str.replace('-', '/')
        year, month, day = map(int, jalali_str.split('/'))
        return jdatetime.date(year, month, day).togregorian()
    except Exception:
        return None

"""Kiểm tra bảng CSV xuất từ PySpark trước khi sử dụng trong dashboard."""
import argparse
import json
from pathlib import Path
from dashboard.data_loader import load_all,validate_tables

def run(directory):
    tables=load_all(directory)
    result=validate_tables(tables)
    print("DASHBOARD_DATA_PASS",json.dumps(result,ensure_ascii=False))
    return result

if __name__=="__main__":
    p=argparse.ArgumentParser()
    p.add_argument("--data",required=True)
    args=p.parse_args()
    run(Path(args.data))

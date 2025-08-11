"""
不動産登記情報のPDFファイルのパスを引数として指定することで、不動産番号を抽出しPDFファイルと同一階層のoutput.txtに出力する。
不動産登記情報のPDFファイルは複数指定できる。
"""

import argparse
import re
import unicodedata
from collections import defaultdict
from pathlib import Path
from typing import Dict, List, Optional

from loguru import logger
from PyPDF2 import PdfReader

pattern = re.compile(r"不動産番号│([０-９]{13})")
OUTPUT_FILE = "output.txt"


def extract_prop_number(path: Path) -> Optional[str]:
    if not path.exists():
        logger.warning(f"File not found: {path}")
        None

    reader = PdfReader(path)
    page = reader.pages[0]
    text = page.extract_text() or ""
    logger.debug(text)
    m = pattern.search(text)
    if m:
        return unicodedata.normalize("NFKC", m.group(1))
    else:
        logger.warning(f"No property number found in {path}")


def output_prop_numbers(prop_numbers_dict: Dict[Path, List[str]]):
    for out_dir, prop_numbers in prop_numbers_dict.items():
        Path(out_dir / OUTPUT_FILE).write_text(
            "\n".join(prop_numbers), encoding="utf-8"
        )


def main(paths: List[Path]):
    logger.debug(paths)
    prop_number_dict = defaultdict(list)
    for path in paths:
        out_dir = path.parent
        prop_number = extract_prop_number(path)
        if not prop_number:
            continue
        prop_number_dict[out_dir].append(prop_number)
    output_prop_numbers(prop_number_dict)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(
        description="Property Number Extractor",
    )
    parser.add_argument("paths", nargs="+", type=Path)
    args = parser.parse_args()

    main(args.paths)

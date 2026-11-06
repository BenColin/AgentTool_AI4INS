# -*- coding: utf-8 -*-
"""
Created on Tue May 13 19:29:23 2025

@author: mebiu
"""

#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
提取指定目录下所有 PDF 文件的题目
优先级：① PDF 元数据 ② 最大字号文本 ③ OCR 兜底
"""

import re, os
from pathlib import Path
import pdfplumber, pytesseract
from pdf2image import convert_from_path
import pandas as pd
from tqdm import tqdm

# === 可自行修改的全局变量 ==========================================
PDF_DIR = Path(r"PAPER_all")  # ← 指定目录
POPPLER = None     # 若 poppler 不在 PATH，可指定其 bin 目录
MAX_PAGES = 1        # 只分析首页，速度快且足够
# ==================================================================

TITLE_RE = re.compile(r"^(.*?)\s*$")  # 后续可自行增强正则

def title_from_metadata(pdf):
    """尝试读取 PDF info 中的 Title 字段"""
    title = pdf.metadata.get("Title") or ""
    return title.strip()

def title_from_font_size(pdf):
    """
    在第一页遍历字块 → 统计平均字号 → 取最大字号所在行 → 返回首行文本
    思路取自常见学术 PDF 版式
    """
    first_page = pdf.pages[0]
    lines = []
    for obj in first_page.extract_words(x_tolerance=1, y_tolerance=2, keep_blank_chars=False, use_text_flow=True):
        # pdfplumber 已按行聚合
        font_sizes = [c["size"] for c in obj["chars"]]
        if not font_sizes:
            continue
        avg_size = sum(font_sizes) / len(font_sizes)
        lines.append((avg_size, obj["text"].strip()))
    if not lines:
        return ""

    # 按字号降序、行长降序排序可过滤页眉
    lines.sort(key=lambda x: (-x[0], -len(x[1])))
    candidate = lines[0][1]

    # 排除明显非标题行（如期刊名、卷期等）
    if len(candidate.split()) < 3:
        return ""
    return candidate

def title_from_ocr(pdf_path):
    """
    若前两步失败，渲染首页为图像 → Tesseract OCR → 取首行
    """
    try:
        images = convert_from_path(str(pdf_path), first_page=1, last_page=1, fmt="png", poppler_path=POPPLER)
        text = pytesseract.image_to_string(images[0], lang="eng").strip()
        # 仅取首行，去除极短行和无意义字符
        for line in text.splitlines():
            clean = line.strip(" _-")
            if len(clean) >= 10 and clean.isprintable():
                return clean
    except Exception:
        pass
    return ""

def extract_title(pdf_path: Path) -> str:
    with pdfplumber.open(pdf_path) as pdf:
        # 1) 元数据
        title = title_from_metadata(pdf)
        if title:
            print('有元数据')
            return title

        # 2) 最大字号文本
        title = title_from_font_size(pdf)
        if title:
            print('最大字号来提取')
            return title

    # 3) OCR 兜底
    print('使用ocr')
    return title_from_ocr(pdf_path)

def main():
    results = []
    pdf_files = sorted([p for p in PDF_DIR.glob("*.pdf") if p.is_file()])
    for pdf_path in tqdm(pdf_files, desc="Scanning PDFs"):
        try:
            title = extract_title(pdf_path)
            results.append({"file": pdf_path.name, "title": title})
        except Exception as e:
            results.append({"file": pdf_path.name, "title": f"ERROR: {e}"})

    df = pd.DataFrame(results)
    csv_path = PDF_DIR / "pdf_titles.csv"
    df.to_csv(csv_path, index=False, encoding="utf-8-sig")
    print(f"\n提取完成，共 {len(df)} 篇；结果已保存：{csv_path}")

if __name__ == "__main__":
    main()

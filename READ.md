# 氙钐科技面试题

## 任务

1. 打开图片并检测图片是否打开
2. 识别图片内容并发送到客户端

## 过程

1. 使用gw检测图片是否打开(is_image_opened in main.py)
2. 将表格分为两个，左右表格分别进行检测
3. 使用tesseract进行OCR检测，结果被储存在列表中，并在client.py中被转化为json形式发送，tesseract 路径设置为 ***Tesseract-OCR/tesseract.exe*** 并支持中文识别(chi_sim.traineddata in ***Tesseract-OCR\tessdata***)

## 安装
```bash
pip install pytesseract
pip install opencv-python
pip install pygetwindow
pip install numpy
```
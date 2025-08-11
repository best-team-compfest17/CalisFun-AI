from paddleocr import PaddleOCR

ocr = PaddleOCR(use_angle_cls=True, lang='id')  # Bahasa Indonesia
result = ocr.ocr('image.png', cls=True)
for line in result:
    print(line[1][0])  # Teks terdeteksi
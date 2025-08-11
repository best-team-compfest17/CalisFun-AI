import easyocr
reader = easyocr.Reader(['id'])  # 'id' for Indonesian
result = reader.readtext('test-4.png')
print(result[0][1])  # Extracted text


# import cv2
# import numpy as np
# from PIL import Image
# import easyocr

# # Baca gambar
# image = cv2.imread('test-5.png')

# # Konversi ke grayscale
# gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# # Tingkatkan kontras dengan CLAHE (Adaptive Histogram Equalization)
# clahe = cv2.createCLAHE(clipLimit=2.0, tileGridSize=(8, 8))
# enhanced = clahe.apply(gray)

# # Simpan gambar sementara
# cv2.imwrite('enhanced_image.png', enhanced)

# # Gunakan EasyOCR pada gambar yang sudah diproses
# reader = easyocr.Reader(['id'])
# result = reader.readtext('enhanced_image.png', paragraph=True)  # Gabungkan paragraf

# # Gabungkan semua teks yang terdeteksi
# full_text = " ".join([res[1] for res in result])
# print(full_text)
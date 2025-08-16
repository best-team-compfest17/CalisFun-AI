import easyocr
reader = easyocr.Reader(['id'])  # 'id' for Indonesian
result = reader.readtext('test-4.png')
print(result[0][1])  # Extracted text
# pack.txt -> kucuk PNG + sonuna eklenmis veri (SketchUp bulut oturumuna PNG olarak yuklenir,
# build_model icinde session_files.read_bytes ile okunur; DNM01 yontemi)
import sys, io
from PIL import Image
buf = io.BytesIO(); Image.new("RGB", (8, 8), (200, 200, 200)).save(buf, "PNG")
data = open(sys.argv[1], "rb").read()
open(sys.argv[2], "wb").write(buf.getvalue() + b"\nERA01DATA\n" + data + b"\nERA01END\n")
print(len(data))

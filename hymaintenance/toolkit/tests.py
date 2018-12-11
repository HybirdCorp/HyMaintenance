from tempfile import NamedTemporaryFile

from PIL import Image


def create_temporary_file(content=b"I am not empty"):
    tmp_file = NamedTemporaryFile(dir=None, delete=True)
    tmp_file.write(content)
    tmp_file.flush()
    return open(tmp_file.name, "rb")


def create_temporary_image():
    tmp_file = NamedTemporaryFile(dir=None, delete=True, suffix=".jpg")
    img = Image.new("RGB", (150, 100))
    img.putdata([(0, 0, 0) for i in range(15000)])
    img.save(tmp_file)
    tmp_file.seek(0)
    return open(tmp_file.name, "rb")

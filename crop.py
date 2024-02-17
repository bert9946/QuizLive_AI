from PIL import Image

def crop_image(input_path, image=None, coordinates=[0.15, 0.265, 0.87, 0.93]):
    if input_path is not None:
        img = Image.open(input_path)
    elif image is not None:
        img = image
    else:
        raise ValueError('input_path and image cannot be None at the same time')

    width, height = img.size

    left = int(coordinates[0] * width)
    upper = int(coordinates[1] * height)
    right = int(coordinates[2] * width)
    lower = int(coordinates[3] * height)


    cropped_img = img.crop((left, upper, right, lower))
    return cropped_img.convert('RGB')


if __name__ == '__main__':
    # 裁剪參數（左上角和右下角的坐標）

    # 執行圖像裁剪
    image = crop_image('images/test_4.jpg')
    image.show()

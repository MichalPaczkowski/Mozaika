import multiprocessing
import os
from PIL import Image
from multiprocessing import Pool


def load_photo(file_name: str):
    photo = Image.open(file_name)
    photo = photo.convert("RGB")
    return photo

def avg_rgb_og(file_name: str, step: int):
    photo = load_photo(file_name)
    width, height = photo.size
    pixels = photo.load()
    rgb_tab = []


    for x in range(height//step):
        for y in range(width//step):
            r, g, b = (0,0,0)
            for i in range(step):
                for j in range(step):
                    rPx, gPx, bPx = pixels[y*step + i, x*step + j]
                    r += rPx
                    g += gPx
                    b += bPx
            rgb_tab.append(((r/(step*step), g/(step*step), b/(step*step)),(x, y))) # tablica krotek (rgb, wspl pierwszego pixela bloku)


    return rgb_tab

def avg_rgb_photos(folder: str, block: int):
    path = os.path.join(os.getcwd(), folder)
    files = os.listdir(path)
    tab_rgb_photos = []

    for file in files:
        path_file = os.path.join(path, file)
        photo = load_photo(path_file)
        photo = photo.resize((block, block)) # zmieniam wielkość zdjęcia na zadaną wielkość
        pixels = photo.load()
        r,g,b = 0,0,0
        for i in range(block):
            for j in range(block):
                rPx, gPx, bPx = pixels[i,j]
                r += rPx
                g += gPx
                b += bPx
        tab_rgb_photos.append(((r/(block*block), g/(block*block),b/(block*block)),file))
    return tab_rgb_photos

def fill_row(args):
    row, folder, block, idx, width, tab_rgb_photos = args
    print(idx)
    mossaic_part = Image.new('RGB', (width,block))
    cwd = os.getcwd()
    iterator = 0
    for el in row:

        min_d = 1000000
        closest_rgb = ((0,0,0), "")
        r = el[0][0]
        g = el[0][1]
        b = el[0][2]
        for rgb_photo in tab_rgb_photos:
            rP = rgb_photo[0][0]
            gP = rgb_photo[0][1]
            bP = rgb_photo[0][2]
            distance = ((r-rP)**2+(g-gP)**2+(b-bP)**2)**0.5
            if min_d > distance:
                closest_rgb = rgb_photo
                min_d = distance
        photo_to_insert = load_photo(os.path.join(cwd,folder, closest_rgb[1]))
        x, y = el[1]
        mossaic_part.paste(photo_to_insert, (block*iterator, 0))
        iterator += 1
    return((mossaic_part, idx))

def fill_og_photo(file_name: str, folder: str, step: int = 1, block: int = 1):
    rgb_tab = avg_rgb_og(file_name, step)
    tab_rgb_photos = avg_rgb_photos(folder, block)
    photo = load_photo(file_name)
    height = int(photo.size[1]/step * block)
    width = int(photo.size[0]/step * block)
    mossaic = Image.new('RGB', (width,height))
    print(len(rgb_tab), len(tab_rgb_photos), height, width)
    podzielone = []
    blocks_in_y = int(photo.size[1] / step)
    blocks_in_x = int(photo.size[0] / step)
    idx= 0 #index danego wiersza

    for i in range(blocks_in_y):
        row = rgb_tab[i * blocks_in_x: (i + 1) * blocks_in_x]
        podzielone.append((row, folder, block, idx, width, tab_rgb_photos))
        idx += 1
    with Pool(processes=multiprocessing.cpu_count()*4) as pool:
        results = pool.map(fill_row, podzielone)

    # Złóż wynikowe części
    ii = 0
    for mossaic_part, coords in results:
        print(coords, mossaic_part)
        mossaic.paste(mossaic_part, (0, coords * block))
    mossaic.save("tralalaaa.jpg")



if __name__ == '__main__':
    fill_og_photo("fototapeta-gory-jezioro-krajobraz-natura-do-salonu-sypialni,jpg.jpg", "zdjecia", 1, 40)


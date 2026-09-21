

import os
import requests

from fpdf import FPDF
from tqdm import tqdm

PAGE_POSITIONS = [{"x": 0.5295, "y": 0.3031, "w": 2.4803, "h": 3.4646},
                  {"x": 3.0098, "y": 0.3031, "w": 2.4803, "h": 3.4646},
                  {"x": 5.4902, "y": 0.3031, "w": 2.4803, "h": 3.4646},
                  {"x": 0.5295, "y": 3.7677, "w": 2.4803, "h": 3.4646},
                  {"x": 3.0098, "y": 3.7677, "w": 2.4803, "h": 3.4646},
                  {"x": 5.4902, "y": 3.7677, "w": 2.4803, "h": 3.4646},
                  {"x": 0.5295, "y": 7.2323, "w": 2.4803, "h": 3.4646},
                  {"x": 3.0098, "y": 7.2323, "w": 2.4803, "h": 3.4646},
                  {"x": 5.4902, "y": 7.2323, "w": 2.4803, "h": 3.4646},]

def load_image(src, name):
    if not os.path.exists('img/'):
        os.mkdir('img')
    with requests.get(src, stream=True, headers={'User-agent': 'Mozilla/5.0'}) as img:
        filename = f"img/{''.join(c for c in name if c.isalnum())}.webp"
        if not os.path.exists(filename) or name in ['Forest', 'Island', 'Mountain', 'Swamp', 'Plains']:
            with open(filename, 'wb+') as file:
                for chunk in img.iter_content(chunk_size=16*1024):
                    file.write(chunk)

    return filename

def generate_pdf(collections, out_filename, collate=True, seed=None):
    pages = []
    if collate:
        for group in range(0, len(collections), 9):
            for i in range(16):
                pages.append([collection[i] for collection in collections[group:group+9]])
    else:
        for collection in collection:
            for p in range(0, len(collection), 9):
                pages.append(collection[p:p+9])

    print([len(page) for page in pages])
        
    pdf = FPDF(unit="in", format='letter')
    pdf.set_margins(0, 0, 0)
    pdf.set_font('Courier')
    
    for page in tqdm(pages):
        # front faces
        pdf.add_page()
        pdf.text(0.2, 0.2, str(seed))
        for i in range(len(page)):
            try:
                pdf.image(load_image(page[i]['src'], page[i]['title']), **PAGE_POSITIONS[i])
            except Exception as e:
                print("failed to print", page[i]['title'])
                print(e)

        # back faces
        pdf.add_page()
        for i in range(len(page)):
            px, py = (i % 3, i // 3)
            px = 2 - px
            j = py * 3 + px

            try:
                pdf.image(load_image(page[i]['src2'], page[i]["title2"]), **PAGE_POSITIONS[j])
            except Exception as e:
                print("failed to print", page[i]['title'])
                print(e)
    
    pdf.output(f'out/{out_filename}.pdf')

import requests
import os
import re
import json
import random
import time
import copy

from bs4 import BeautifulSoup
from tqdm import tqdm
from fpdf import FPDF

COLLATE = True

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

PAGE_POSITIONS = [{"x": 0.5295, "y": 0.3031, "w": 2.4803, "h": 3.4646},
                  {"x": 3.0098, "y": 0.3031, "w": 2.4803, "h": 3.4646},
                  {"x": 5.4902, "y": 0.3031, "w": 2.4803, "h": 3.4646},
                  {"x": 0.5295, "y": 3.7677, "w": 2.4803, "h": 3.4646},
                  {"x": 3.0098, "y": 3.7677, "w": 2.4803, "h": 3.4646},
                  {"x": 5.4902, "y": 3.7677, "w": 2.4803, "h": 3.4646},
                  {"x": 0.5295, "y": 7.2323, "w": 2.4803, "h": 3.4646},
                  {"x": 3.0098, "y": 7.2323, "w": 2.4803, "h": 3.4646},
                  {"x": 5.4902, "y": 7.2323, "w": 2.4803, "h": 3.4646},]

setName = input('input set tag (MSH): ')
if not setName:
    setName = 'MSH'
count = input('how many sets (3): ')
if not count:
    count = 3
else:
    count = int(count)
library = {"r": [], "u": [], "c": [], "land": []}

# from wizards.com
# def load_search(params=[f"s:{setName}"]):
#     result = []

#     print(f"loading cards with params: {' '.join(params)}")

#     nextPage = 1
#     while nextPage > -1:
#         search = requests.get('https://gatherer.wizards.com/search', {"searchTerm": ' '.join(params), "page": nextPage})
#         print(f"fetching {search.url}")
#         search_page = BeautifulSoup(search.content, "html.parser")

#         cards = search_page.select('img.rounded-card.opacity-0')
#         for card in cards:
#             result.append({"title": card.attrs['title'], "src": card.attrs['src']})

#         # pagination
#         wrapper = str(search_page.find('form', attrs={'data-testid': 'cardFiltersWrapper'}))
#         match = re.search(r'\d*-(\d*) of (\d*)', wrapper)

#         last = int(match.group(1))
#         total = int(match.group(2))

#         if last < total:
#             nextPage += 1
#         else:
#             nextPage = -1

#     print(f"{len(result)} cards found")
#     return result

# from scryfall
def load_search(params=[f"e:{setName}"]):
    result = {}

    print(f"loading cards with params: {' '.join(params)}")
    
    params.append('unique:prints')
    nextPage = 1
    while nextPage > -1:
        search = requests.get('https://api.scryfall.com/cards/search', {"q": ' '.join(params), "order": "usd", "dir": "desc", "page": nextPage}, headers={'User-agent': 'Mozilla/5.0'})
        print(f"fetching {search.url}")
        search = search.json()

        if "data" not in search:
            break
        for card in search['data']:
            if 'image_uris' in card and card['name'] not in result:
                result[card['name']] = (card['image_uris']['png'], int(re.findall(r'\d+', card['collector_number'])[0]))

        if search['has_more']:
            nextPage += 1
        else:
            nextPage = -1

    print(f"{len(result)} cards found")
    return [{"title": key, "src": value[0]} for key, value in result.items()]

if not os.path.exists('out/'):
    os.mkdir('out')

if os.path.exists(f'out/{setName}.json'):
    print(f"loading from cache")
    with open(f'out/{setName}.json', 'r') as file:
        library = json.load(file)
else:
    print(f"loading from scryfall API")
    library['mr'] = load_search([f'e:{setName}', 'r>r'])
    library['r'] = load_search([f'e:{setName}', 'r:r'])
    library['u'] = load_search([f'e:{setName}', 'r:u'])
    library['c'] = load_search([f'e:{setName}', 'r:c', '-t:land'])
    library['land'] = load_search([f'e:{setName}', 't:land', "r:c"])

    with open(f'out/{setName}.json', 'w+') as file:
        json.dump(library, file)

print(f"loaded {len(library['r'])} rares+, {len(library['u'])} uncommons, and {len(library['c'])} commons (+{len(library['land'])} lands)")

sets = []
# picking sets
for s in range(count):
    if not os.path.exists('out/'):
        os.mkdir('out')
    
    print('generating set', s)

    seed = time.time_ns() // 1_000_000
    random.seed(seed)

    cards = []

    library_copy = copy.deepcopy(library)

    # 1 land
    cards.append(library_copy['land'].pop(random.randint(0, len(library_copy['land'])-1)))

    # 10 commons
    for _ in range(10):
        cards.append(library_copy['c'].pop(random.randint(0, len(library_copy['c'])-1)))

    # potential foil replacing a common
    # if random.randint(0, x) == x:
    #     cards.pop()
    #     library_combined = [*library_copy['c'], *library_copy['u'], *library_copy['r'], *library_copy['mr']]
    #     cards.append(library_combined.pop(random.randint(0, len(library_combined)-1)))

    # 3 uncommons
    for _ in range(3):
        cards.append(library_copy['u'].pop(random.randint(0, len(library_copy['u'])-1)))

    # 1 rare/mythic rare
    for _ in range(1):
        if random.randint(0, 7) == 7:
            cards.append(library_copy['mr'].pop(random.randint(0, len(library_copy['mr'])-1)))
        else:
            cards.append(library_copy['r'].pop(random.randint(0, len(library_copy['r'])-1)))
    
    # random.shuffle(cards)
    
    # 1 token
    try:
        tokens = requests.get(f"https://scryfall.com/sets/T{setName}")
        tokens_page = BeautifulSoup(tokens.content, "html.parser")

        tokens = tokens_page.select("img.card")
        token = tokens.pop(random.randint(0, len(tokens)-1))
        cards.append({"title": token.attrs['alt'], "src": token.attrs['src']})
    except:
        print("no tokens found :c")
    
    sets.append(cards)
    with open(f'out/set{s}.json', "w+") as file:
        json.dump({"seed": seed, "cards": cards}, file)

pages = []
if COLLATE:
    for i in range(16):
        pages.append([set[i] for set in sets])
else:
    for set in sets:
        for p in range(0, len(set), 9):
            pages.append(set[p:p+9])

    
pdf = FPDF(unit="in", format='letter')
for page in tqdm(pages):
    pdf.add_page()
    for i in range(len(page)):
        try:
            pdf.image(load_image(page[i]['src'], page[i]['title']), **PAGE_POSITIONS[i])
        except:
            print("failed to print", cards[i]['title'])
pdf.output('out/sets.pdf')

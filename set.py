import json
import os
import requests

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
def load_search(params=[]):
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
            if card['name'] not in result:
                if 'image_uris' in card:
                    result[card['name']] = (card['image_uris']['png'], 'back', "https://cards.scryfall.io/back.png")
                elif 'card_faces' in card:
                    faces = card['card_faces']
                    result[card['name']] = (faces[0]['image_uris']['png'], f'{card["name"]}_back', faces[1]['image_uris']['png'])

        if search['has_more']:
            nextPage += 1
        else:
            nextPage = -1

    print(f"{len(result)} cards found")
    return [{"title": key, "title2": value[1], "src": value[0], "src2": value[2]} for key, value in result.items()]

def load_set(setName):
    library = {"r": [], "u": [], "c": [], "land": []}

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

    print(f"loaded {len(library['r']) + len(library['mr'])} rares+, {len(library['u'])} uncommons, and {len(library['c'])} commons (+{len(library['land'])} lands)")
    return library

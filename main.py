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

from set import load_set
from pdf import generate_pdf

COLLATE = True

while True:
    print('mode:')
    print('s. sets (generate)')
    print('d. deck (just print lol)')
    mode = input()

    if mode == 's':
        setName = input('input set tag (MSH): ')
        if not setName:
            setName = 'MSH'

        count = input('how many packs (3): ')
        count = int(count) if count else 3
            
        seed = input('seed (-1): ')
        seed = int(seed) if seed else -1

        library = load_set(setName)

        if seed == -1:
            seed = time.time_ns() % (2 ** 32)
        print(f'generating packs with seed {seed}')
        random.seed(seed)

        def randint(start, stop):
            number = random.randint(start, stop-1)
            # print(f"randint {start}-{stop}: {number}")
            return number

        packs = []
        # picking packs
        for s in range(count):
            if not os.path.exists('out/'):
                os.mkdir('out')
            
            print('generating pack', s)

            library_copy = copy.deepcopy(library)

            cards = []

            # 1 land
            cards.append(library_copy['land'].pop(randint(0, len(library_copy['land']))))

            # 10 commons
            for _ in range(10):
                cards.append(library_copy['c'].pop(randint(0, len(library_copy['c']))))

            # potential foil replacing a common
            # if randint(0, x+1) == x:
            #     cards.pop()
            #     library_combined = [*library_copy['c'], *library_copy['u'], *library_copy['r'], *library_copy['mr']]
            #     cards.append(library_combined.pop(randint(0, len(library_combined))))

            # 3 uncommons
            for _ in range(3):
                cards.append(library_copy['u'].pop(randint(0, len(library_copy['u']))))

            # 1 rare/mythic rare
            for _ in range(1):
                if randint(0, 8) == 7:
                    cards.append(library_copy['mr'].pop(randint(0, len(library_copy['mr']))))
                else:
                    cards.append(library_copy['r'].pop(randint(0, len(library_copy['r']))))
            
            # random.shuffle(cards)
            
            # 1 token
            try:
                tokens = requests.get(f"https://scryfall.com/sets/T{setName}")
                tokens_page = BeautifulSoup(tokens.content, "html.parser")

                tokens = tokens_page.select("img.card")
                token = tokens.pop(randint(0, len(tokens)))
                cards.append({"title": token.attrs['alt'], "src": token.attrs['src'], 'title2': 'back', 'src2': "https://cards.scryfall.io/back.png"})
            except:
                print("no tokens found :c")

            cards.append(seed) # [-1] for seed
            
            packs.append(cards)
            with open(f'out/pack{s}.json', "w+") as file:
                json.dump({"seed": seed, "cards": cards}, file)

        generate_pdf(packs, 'packs', COLLATE, seed)
        break
    elif mode == 'd':
        def card_info(dict):
            return {"title": dict['title'], "title2": "back", "src": f"https://cards.scryfall.io/png/front/c/a/{dict['scryfall_id']}", "src2": "https://cards.scryfall.io/back.png"}
        id = input('deck id (accepting moxfield): ')
        deck = requests.get(f'https://api2.moxfield.com/v3/decks/all/{id}', headers={'User-agent': 'Mozilla/5.0'})
        print(f"fetching {deck.url}")
        print(deck.text)
        deck = deck.json()

        cards = []
        cards.extend([card_info(card) for card in deck['boards']['commanders']['cards'].values()])

        cards.extend([card_info(card) for card in deck['boards']['mainboard']['cards'].values() if ('basic land' not in deck['type_line'].lower())])
        cards.extend([card_info(card) for card in deck['boards']['sideboard']['cards'].values()])


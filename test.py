import requests

with requests.get('https://cards.scryfall.io/grid/front/5/7/57bcf5f4-da1e-4b6a-85ef-aad91d2276cf.webp', stream=True) as img:
    print(img.content)
    with open('img/test.webp', 'wb+') as file:
        for chunk in img.iter_content(chunk_size=16*1024):
            file.write(chunk)

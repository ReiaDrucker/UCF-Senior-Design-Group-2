import requests

left_url = 'https://cdn.loc.gov/master/pnp/cwpb/03200/03261a.tif'
right_url = 'https://cdn.loc.gov/master/pnp/cwpb/03200/03262a.tif'

def save_image(url, path):
    r = requests.get(url, stream=True)

    if r.status_code != 200:
        raise RuntimeError('Failed to download image')

    with open(path, 'wb') as f:
        for chunk in r:
            f.write(chunk)

save_image(left_url, 'left.tif')
save_image(right_url, 'right.tif')

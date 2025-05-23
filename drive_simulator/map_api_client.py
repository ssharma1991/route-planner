import os
from time import sleep 
import requests
import math
from io import BytesIO
from PIL import Image, ImageOps


class MapAPIClient:
    def __init__(self):
        # Create a directory to store the tiles
        self.cache_path = "osm_tiles"
        if not os.path.exists(self.cache_path):
            os.mkdir(self.cache_path)
    
    def get_tile(self, xtile, ytile, zoom):
        # Download and cache the tile if it doesn't exist
        path = self.cache_path + f"/{zoom}_{xtile}_{ytile}.png"
        if not os.path.exists(path):
            tile = self.download_tile(xtile, ytile, zoom)
            with open(path, "wb") as f:
                f.write(tile)

        # Read the tile from the cache
        with open(path, "rb") as f:
                tile = f.read()
        tile = Image.open(BytesIO(tile))

        # Add mild blue edge to each tile
        blue_border = Image.new('RGB',(254,254),(0,0,0))
        blue_border = ImageOps.expand(blue_border, border=1, fill=(0,0,255))
        mask = Image.new('L',(254,254),(255))
        mask = ImageOps.expand(mask, border=1, fill=(200))
        tile = Image.composite(tile, blue_border, mask)

        return tile
    
    def download_tile(self, xtile, ytile, zoom):
        url = f"https://a.tile.openstreetmap.org/{zoom}/{xtile}/{ytile}.png"
        print(f"Downloading {url}")
        headers = {'User-Agent': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:109.0) Gecko/20100101 Firefox/113.0'}
        response = requests.get(url, headers=headers)
        response.raise_for_status()
        return response.content
    
    # Ref: https://wiki.openstreetmap.org/wiki/Slippy_map_tilenames#Python
    def deg2tilenum(self, lat_deg, lon_deg, zoom):
        lat_rad = math.radians(lat_deg)
        n = 2.0 ** zoom
        xtile = int((lon_deg + 180.0) / 360.0 * n)
        ytile = int((1.0 - math.log(math.tan(lat_rad) + (1 / math.cos(lat_rad))) / math.pi) / 2.0 * n)
        return (xtile, ytile)
    
    def tilenum2deg(self, xtile, ytile, zoom):
        n = 2.0 ** zoom
        lon_deg = xtile / n * 360.0 - 180.0
        lat_rad = math.atan(math.sinh(math.pi * (1 - 2 * ytile / n)))
        lat_deg = math.degrees(lat_rad)
        return (lat_deg, lon_deg)
    
    def get_osrm_route(self, start, end):
        url = f"http://router.project-osrm.org/route/v1/driving/{start.lon},{start.lat};{end.lon},{end.lat}?overview=full&geometries=geojson"
        print(f"Fetching route from OSRM: from ({start.lat}, {start.lon}) to ({end.lat}, {end.lon})")
        response = requests.get(url)
        return response.json()

    # Ref: https://www.opentopodata.org/
    def get_opentopo_elevation_batch(self, waypoints, batch_size=100):
        elevations = []

        for i in range(0, len(waypoints), batch_size):
            batch = waypoints[i:i + batch_size]
            batch_elevations = self.get_opentopo_elevation(batch)
            elevations.extend(batch_elevations)

            # Wait for 1 second between API calls
            sleep(1)

        return elevations

    def get_opentopo_elevation(self, waypoints):
        if len(waypoints) > 100:
            print("Too many waypoints, using only the first 100. For more waypoints, use get_opentopo_elevation_batch()")
            waypoints = waypoints[:100]

        url = "https://api.opentopodata.org/v1/aster30m?locations="
        locations = "|".join([f"{w.lat},{w.lon}" for w in waypoints])
        print(f"Fetching elevation data from OpenTopo for {len(waypoints)} waypoints")
        response = requests.get(url + locations)

        if response.status_code == 200:
            data = response.json()
            return [result['elevation'] for result in data['results']]
        else:
            print(f"Error fetching elevation data: {response.status_code}")
            return []

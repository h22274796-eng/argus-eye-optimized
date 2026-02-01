import exifread

class GeoReferencer:
    def get_coords(self, path):
        with open(path, 'rb') as f:
            tags = exifread.process_file(f)
            try:
                lat = self._convert(tags['GPS GPSLatitude'], tags['GPS GPSLatitudeRef'].printable)
                lon = self._convert(tags['GPS GPSLongitude'], tags['GPS GPSLongitudeRef'].printable)
                return lat, lon
            except:
                return None, None

    def _convert(self, val, ref):
        d = float(val.values[0].num) / val.values[0].den
        m = float(val.values[1].num) / val.values[1].den
        s = float(val.values[2].num) / val.values[2].den
        res = d + (m/60) + (s/3600)
        return res if ref in ['N', 'E'] else -res
from backend.utils.geo_utils import GeoReferencer

class ExportService:
    def to_kml(self, detections):
        geo = GeoReferencer()
        return geo.generate_kml(detections)

export_service = ExportService()
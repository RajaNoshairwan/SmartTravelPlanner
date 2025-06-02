from utils.distance_calculator import get_or_add_city_coordinates
 
def test_new_city():
    # city very unlikely to be in CSV
    lat, lon = get_or_add_city_coordinates("Shahdadkot")
    assert isinstance(lat, float) and isinstance(lon, float) 
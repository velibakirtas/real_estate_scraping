import math

class GridGenerator:
    def __init__(self, target_hectares=8):
        """
        target_hectares: The desired area of each search box (default 8).
        """
        # 1 Hectare = 10,000 square meters
        self.target_sq_meters = target_hectares * 10000
        # Determine the side length of the square (Sqrt of Area)
        # 80,000 m2 -> ~282.84 meters
        self.side_length_meters = math.sqrt(self.target_sq_meters)
        print(f"🎯 Target Configuration: {target_hectares} Hectares")
        print(f"📏 Grid Box Size: {self.side_length_meters:.2f}m x {self.side_length_meters:.2f}m")

    def _meters_to_lat_degrees(self):
        """1 degree of Latitude is constant ~111,111 meters."""
        return self.side_length_meters / 111111

    def _meters_to_lng_degrees(self, latitude):
        """
        1 degree of Longitude varies by Latitude.
        Formula: 111,111 * cos(latitude)
        """
        lat_radians = math.radians(latitude)
        meters_per_degree = 111111 * math.cos(lat_radians)
        return self.side_length_meters / meters_per_degree

    def generate_tiles(self, ne_lat, ne_lng, sw_lat, sw_lng):
        """
        Slices the defined area into smaller tiles.
        """
        # 1. Calculate step sizes based on the center latitude of the area
        center_lat = (ne_lat + sw_lat) / 2
        lat_step = self._meters_to_lat_degrees()
        lng_step = self._meters_to_lng_degrees(center_lat)

        print(f"🔢 Calculated Steps -> Lat: {lat_step:.6f}, Lng: {lng_step:.6f}")
        
        tiles = []
        
        # 2. Iterate (Scan from South-West to North-East)
        current_lat = sw_lat
        while current_lat < ne_lat:
            current_lng = sw_lng
            while current_lng < ne_lng:
                # Calculate the Top-Right corner of this specific tile
                tile_ne_lat = min(current_lat + lat_step, ne_lat)
                tile_ne_lng = min(current_lng + lng_step, ne_lng)
                
                # Store the tile
                tiles.append({
                    "ne_lat": round(tile_ne_lat, 6),
                    "ne_lng": round(tile_ne_lng, 6),
                    "sw_lat": round(current_lat, 6),
                    "sw_lng": round(current_lng, 6)
                })
                
                # Move East
                current_lng += lng_step
            
            # Move North
            current_lat += lat_step
            
        return tiles

# --- Test Execution Block ---
if __name__ == "__main__":
    # 1. Define a sample area (e.g., A part of Beşiktaş/Istanbul)
    # You can change these to your target area
    TEST_NE_LAT = 41.0450
    TEST_NE_LNG = 29.0050
    TEST_SW_LAT = 41.0350
    TEST_SW_LNG = 28.9850

    # 2. Initialize the Generator for 8 Hectares
    generator = GridGenerator(target_hectares=8)

    # 3. Generate
    print(f"\n🌍 Scanning Area: NE({TEST_NE_LAT}, {TEST_NE_LNG}) - SW({TEST_SW_LAT}, {TEST_SW_LNG})")
    grid = generator.generate_tiles(TEST_NE_LAT, TEST_NE_LNG, TEST_SW_LAT, TEST_SW_LNG)

    # 4. Report
    print(f"\n✅ Generated {len(grid)} tiles.")
    
    print("\n--- Sample Tiles (First 3) ---")
    for i, tile in enumerate(grid):
        print(f"Tile {i+1}: {tile}")

    # 5. Verification (Optional): Calculate area of the first tile to prove it's ~8ha
    if grid:
        sample = grid[0]
        d_lat = sample['ne_lat'] - sample['sw_lat']
        d_lng = sample['ne_lng'] - sample['sw_lng']
        # Rough calc back to meters
        h_meters = d_lat * 111111
        w_meters = d_lng * (111111 * math.cos(math.radians(TEST_SW_LAT)))
        area_hectares = (h_meters * w_meters) / 10000
        print(f"\n🔍 Verification: Tile 1 Area ≈ {area_hectares:.2f} Hectares")
import unittest


class TestFlightLogic(unittest.TestCase):

    def test_bounding_box_validation(self):
        """Test if we can correctly identify if a point is inside our box."""
        # Our Box: lamin=45.8, lomin=5.9, lamax=47.8, lomax=10.5
        lat, lon = 46.0, 8.0  # Inside Switzerland

        is_inside = (45.8 <= lat <= 47.8) and (5.9 <= lon <= 10.5)
        self.assertTrue(is_inside, "Point should be inside the bounding box")

    def test_velocity_conversion(self):
        """Test conversion from m/s to km/h."""
        velocity_ms = 100
        expected_kmh = 360
        result = velocity_ms * 3.6
        self.assertEqual(result, expected_kmh)


if __name__ == '__main__':
    unittest.main()
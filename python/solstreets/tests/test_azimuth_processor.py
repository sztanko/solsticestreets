from solstreets.entities import StreetSegment
from solstreets.azimuth_processor import combine_segments


def test_combine_segents():
    points = [[0, 0], [1, 1], [2, 2]]
    segments = [StreetSegment("", "", [points[i - 1], points[i]], 0, 0, 0) for i in range(1, len(points))]
    after_points = [s.points for s in combine_segments(segments)]
    assert len(after_points) == 1
    assert after_points == [[[0, 0], [2, 2]]]

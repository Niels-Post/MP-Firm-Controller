from detection.transformation.shape.Quadrilateral import Quadrilateral, Point
from detection.transformation.shape.Rectangle import Rectangle


class PositionTransformer:
    """
    Map positions within a quadrilateral to a rectangle
    """

    def __init__(self, quad: Quadrilateral, rect: Rectangle):
        self.quad = quad
        self.rect = rect

    def get_transformed_position(self, p: Point) -> Point:
        """
        Transform a single position to a position in the quadrialteral
        :param p:
        :return:
        """
        h_distances = self.quad.get_minimum_horizontal_distances(p)
        u_coordinate = h_distances[0] / sum(h_distances)
        v_distances = self.quad.get_minimum_vertical_distances(p)
        v_coordinate = v_distances[0] / sum(v_distances)

        return self.rect.get_xy_from_uv(u_coordinate, v_coordinate)

    def get_transformed_quad(self, quad: Quadrilateral) -> Quadrilateral:
        return Quadrilateral(
            *[self.get_transformed_position(p) for p in quad.coordinates]
        )



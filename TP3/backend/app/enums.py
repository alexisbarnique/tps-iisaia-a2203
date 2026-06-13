import enum


class CategoryEnum(str, enum.Enum):
    event = "event"
    movie_series = "movie_series"
    book = "book"
    city = "city"
    place = "place"


class PlaceTypeEnum(str, enum.Enum):
    restaurant = "restaurant"
    cafe = "cafe"
    museum = "museum"
    bar = "bar"
    park = "park"
    other = "other"

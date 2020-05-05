from .region import register_italy_regions_api
from .provinces import register_italy_provinces_api
from .region_case import register_italy_region_case_api

__all__ = [
    "register_italy_provinces_api",
    "register_italy_regions_api",
    "register_italy_region_case_api",
]

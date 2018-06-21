from astroquery.ned import Ned
from astroquery.exceptions import RemoteServiceError

from tom_catalogs.harvester import AbstractHarvester, EmptyResultException


class NEDHarvester(AbstractHarvester):
    name = 'NED'

    def query(self, term):
        try:
            self.catalog_data = Ned.query_object(term)
        except RemoteServiceError:
            raise EmptyResultException

    def to_target(self):
        target = super().to_target()
        target.type = 'SIDEREAL'
        target.ra = self.catalog_data['RA(deg)'][0]
        target.dec = self.catalog_data['DEC(deg)'][0]
        return target

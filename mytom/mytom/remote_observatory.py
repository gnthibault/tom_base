from crispy_forms.layout import Layout
from django import forms

# Locals
from tom_observations.facility import BaseRoboticObservationFacility, BaseRoboticObservationForm

class RemoteObservatoryBaseForm(BaseRoboticObservationForm):
    exposure_time = forms.IntegerField()
    exposure_count = forms.IntegerField()

    def layout(self):
        return Layout(
            'exposure_time',
            'exposure_count'
        )


class RemoteObservatory(BaseRoboticObservationFacility):
    name = 'RemoteObservatory'
    observation_types = [('spectro_lr', 'spectro_hr')]
    observation_forms = {
        'spectro_lr': RemoteObservatoryBaseForm,
        'spectro_hr': RemoteObservatoryBaseForm,
    }
    SITES = {
        # https://trevincaskies.com/#faq
        'trevinca_skies': {
            'latitude': 42.230175,
            'longitude': -6.972704,
            'elevation': 800
        }
    }

    def data_products(self, observation_id, product_id=None):
       return []

    def get_form(self, observation_type):
        return self.observation_forms[observation_type]

    def get_observation_status(self, observation_id):
        return ['IN_PROGRESS']

    def get_observation_url(self, observation_id):
        return ''

    def get_observing_sites(self):
        return self.SITES

    def get_terminal_observing_states(self):
        return ['IN_PROGRESS', 'COMPLETED']

    def submit_observation(self, observation_payload):
        """
        See https://tom-toolkit.readthedocs.io/en/latest/observing/observation_module.html
        The important method here is submit_observation. This method, when implemented fully, will send the
        observation payload to the remote observatory and then return a list of observation ids. Those ids will be
        stored in the database to be used later, in methods like get_observation_status(self, observation_id).
        In our dummy implementation, we simply print out the observation payload and return a single fake id with
        return [1].
        """
        print(observation_payload)
        return [1]

    def validate_observation(self, observation_payload):
        pass

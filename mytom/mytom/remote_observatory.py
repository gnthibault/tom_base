from crispy_forms.layout import Layout
from django import forms
import requests

# Locals
from tom_observations.facility import BaseRoboticObservationFacility, BaseRoboticObservationForm

class RemoteObservatoryFacilityForm(BaseRoboticObservationForm):
    exposure_time = forms.IntegerField()
    exposure_count = forms.IntegerField()

    def layout(self):
        return Layout(
            'exposure_time',
            'exposure_count'
        )

class RemoteObservatoryFacility(BaseRoboticObservationFacility):
    """
    Main documentation here: https://tom-toolkit.readthedocs.io/en/latest/api/tom_observations/facilities.html
    """
    name = 'RemoteObservatory'
    observation_types = [('spectro_lr', 'spectro_hr')]
    observation_forms = {
        'default_field': RemoteObservatoryFacilityForm,
        'spectro_lr'   : RemoteObservatoryFacilityForm,
        'spectro_hr'   : RemoteObservatoryFacilityForm,
    }
    SITES = {
        # https://trevincaskies.com/#faq
        'trevinca_skies': {
            'latitude': 42.230175,
            'longitude': -6.972704,
            'elevation': 800
        },
        'indi_simulator': {
            'latitude': 45.678,
            'longitude': 4.567,
            'elevation': 800
        }
    }
    base_url = "http://127.0.0.1:8888"

    def data_products(self, observation_id, product_id=None):
        url = f"{self.base_url}/get_observation_data/{observation_id}"
        response = requests.get(url)
        response.raise_for_status()
        save_to = f"data_product_{observation_id}.zip"
        with open(save_to, "wb") as f:
            f.write(response.content)
        print(f"Saved zip file to {save_to}")

    def get_template_form(self):
        pass
    def get_form(self, observation_type):
        try:
            return self.observation_forms[observation_type]
        except KeyError:
            return self.observation_forms["default_field"]

    def get_observation_status(self, observation_id):
        url = f"{self.base_url}/get_observation_status/{observation_id}"
        response = requests.get(url)
        response.raise_for_status()
        return [response.json()["status"]]

    def get_observation_url(self, observation_id):
        return f"{self.base_url}/get_observation_status/{observation_id}"

    def get_observing_sites(self):
        return self.SITES

    def get_terminal_observing_states(self):
        return ["posted", "scheduling", "acquiring", "calibrating", "ready"]

    def submit_observation(self, observation_payload):
        """
        See https://tom-toolkit.readthedocs.io/en/latest/observing/observation_module.html
        The important method here is submit_observation. This method, when implemented fully, will send the
        observation payload to the remote observatory and then return a list of observation ids. Those ids will be
        stored in the database to be used later, in methods like get_observation_status(self, observation_id).
        In our dummy implementation, we simply print out the observation payload and return a single fake id with
        return [1].
        """
        url = f"{self.base_url}/request_observation"
        response = requests.post(url, json=observation_payload)
        response.raise_for_status()
        return [response.json()["observation_id"]]

    def validate_observation(self, observation_payload):
        pass

from crispy_forms.layout import Layout
from django import forms
import requests
from enum import Enum

# Locals
from tom_observations.facility import BaseRoboticObservationFacility, BaseRoboticObservationForm
from tom_targets.models import Target




class InstrumentSetup(str, Enum):
    LR_SPECTROSCOPY        = "lr_spectroscopy"
    HR_SPECTROSCOPY        = "hr_spectroscopy"
    FIEL_IMAGING           = "field_imaging"

class AcquisitionWorkflow(str, Enum):
    DEFAULT                = "default"


class RemoteObservatoryFacilityForm(BaseRoboticObservationForm):
    instrument_setup       = forms.ChoiceField(
        choices=[(i.value,)*2 for i in InstrumentSetup],
        required=True,
        label="Select an Instrument setup"
    )
    acquisition_workflow   = forms.ChoiceField(
        choices=[(i.value,)*2 for i in AcquisitionWorkflow],
        required=True,
        label="Select an acquisition workflow"
    )
    time_per_exposure      = forms.IntegerField(required=False)
    number_exposure        = forms.IntegerField(required=False)
    target_snr             = forms.FloatField(required=False)

    def layout(self):
        return Layout(
            'instrument_setup',
            'acquisition_workflow',
            'time_per_exposure',
            'number_exposure',
            'target_snr'
        )

    def observation_payload(self):
        """
        This method is called to extract the data from the form into a dictionary that
        can be used by the rest of the module. In the base implementation it simply dumps
        the form into a json string.
        """
        target = Target.objects.get(pk=self.cleaned_data['target_id'])
        payload = self.serialize_parameters()
        payload.pop("target_id", None)
        payload.pop("cadence_strategy", None)
        payload.pop("facility", None)
        payload.pop("observation_type", None)
        payload["target"] = target.name
        return payload


class RemoteObservatoryFacility(BaseRoboticObservationFacility):
    """
    Main documentation here: https://tom-toolkit.readthedocs.io/en/latest/api/tom_observations/facilities.html
    """
    name = 'RemoteObservatory'
    observation_types = [('Default observation')]
    observation_forms = {
        'Default observation': RemoteObservatoryFacilityForm,
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
        """
        Using an observation_id, retrieve a list of the data
        products that belong to this observation. In this case,
        the LCO module retrieves a list of frames from the LCO
        data archive.
        """
        url = f"{self.base_url}/get_observation_data/{observation_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()['data_products']

    def get_template_form(self):
        pass

    def get_form(self, observation_type):
        try:
            return self.observation_forms[observation_type]
        except KeyError:
            return self.observation_forms["Default observation"]

    def get_observation_status(self, observation_id):
        url = f"{self.base_url}/get_observation_status/{observation_id}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()

    def get_observation_url(self, observation_id):
        return f"{self.base_url}/get_observation_status/{observation_id}"

    def get_observing_sites(self):
        return self.SITES

    def get_terminal_observing_states(self):
        #return ["posted", "scheduling", "acquiring", "calibrating", "ready"]
        return ["ready", "canceled", "failed", "timed_out"]


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
        return [response.json()["id"]]

    def validate_observation(self, observation_payload):
        """
        Same thing as submit_observation, but a dry run. You can
        skip this in different modules by just using "pass"

        Typically called by the ObservationForm.is_valid() method.
        """
        pass

    def get_facility_weather_urls(self):
        """
        Returns a dictionary containing a URL for weather information
        for each site in the Facility SITES. This is intended to be useful
        in observation planning.

        `facility_weather = {'code': 'XYZ', 'sites': [ site_dict, ... ]}`
        where
        `site_dict = {'code': 'XYZ', 'weather_url': 'http://path/to/weather'}`

        """
        return {}

    def get_facility_status(self):
        """
        Returns a dictionary describing the current availability of the Facility
        telescopes. This is intended to be useful in observation planning.
        The top-level (Facility) dictionary has a list of sites. Each site
        is represented by a site dictionary which has a list of telescopes.
        Each telescope has an identifier (code) and an status string.

        The dictionary hierarchy is of the form:

        `facility_dict = {'code': 'XYZ', 'sites': [ site_dict, ... ]}`
        where
        `site_dict = {'code': 'XYZ', 'telescopes': [ telescope_dict, ... ]}`
        where
        `telescope_dict = {'code': 'XYZ', 'status': 'AVAILABILITY'}`

        See lco.py for a concrete implementation example.
        """
        return {}

    def cancel_observation(self, observation_id):
        """
        Takes an observation id and submits a request to the observatory that the observation be cancelled.

        If the cancellation was successful, return True. Otherwise, return False.
        """
        url = f"{self.base_url}/cancel_observation/{observation_id}"
        response = requests.get(url)
        response.raise_for_status()

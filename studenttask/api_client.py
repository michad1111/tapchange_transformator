import requests
from fastapi import FastAPI
from loguru import logger
from pydantic import BaseModel, ConfigDict


class SimulatorUpdateData(BaseModel):
    """
    Pydantic model for parsing simulator data received via POST requests.

    Contains grid state information like voltage bands, tap changer positions,
    and voltage measurements needed for control calculations.
    """

    # Configure model to be immutable for data safety
    model_config = ConfigDict(frozen=True)

    # Task identifier string
    task: str = ""

    # Matriculation number
    matriculation_number: str = ""

    # Voltage band limits for normal operation
    upper_voltage_band: float
    lower_voltage_band: float

    # Safety voltage limits that should never be exceeded
    upper_voltage_safety: float
    lower_voltage_safety: float

    # Valid tap changer position range
    min_step_position: int
    max_step_position: int

    # Reference voltage level for the grid
    nominal_voltage: float

    # Current tap changer state
    current_tapchanger_position: int

    # Mapping of tap positions to their voltage factors
    tapchanger_voltage_factors: dict[str, float]

    # Current range control factor for voltage spreading
    current_rangecontrol_factor: float

    # Measured voltage extremes in the street
    min_street_voltage: float
    max_street_voltage: float

    def get_current_tapchanger_position(self) -> int:
        """
        Get the current position of the tap changer.

        Returns:
            int: Current tap changer position
        """
        return self.current_tapchanger_position

    def get_tapchanger_voltage_factor(self, step: int) -> float:
        """
        Get the voltage factor for a specific tap position.

        Args:
            step: Tap changer position to get factor for

        Returns:
            float: Voltage factor for the given position

        Raises:
            KeyError: If the step position doesn't exist
        """
        return self.tapchanger_voltage_factors[str(step)]

    def get_range_control_factor(self) -> float:
        """
        Get the current range control factor.

        Returns:
            float: Current range control factor value
        """
        return self.current_rangecontrol_factor

    def get_min_street_voltage(self) -> float:
        """
        Get the minimum voltage measured in the street.

        Returns:
            float: Minimum street voltage in volts
        """
        return self.min_street_voltage

    def get_max_street_voltage(self) -> float:
        """
        Get the maximum voltage measured in the street.

        Returns:
            float: Maximum street voltage in volts
        """
        return self.max_street_voltage


class HeartbeatInfo(BaseModel):
    """
    Model for heartbeat response payload.

    Contains boolean flag indicating if service is alive.
    """

    is_alive: bool


class TaskRegistrationInfo(BaseModel):
    """
    Model for task registration request payload.

    Contains URL where the studenttask service can be reached.
    """

    studenttask_url: str


class APIClient:
    """
    Client for handling API communication between studenttask and simulator.

    Manages registration, heartbeat responses and FastAPI application setup.
    """

    def __init__(
        self, simulator_url: str, studenttask_url: str, timeout: float = 1.0
    ) -> None:
        """
        Initialize API client with connection settings.

        Args:
            simulator_url: Base URL of the simulator API
            studenttask_url: URL where this studenttask instance is hosted
            timeout: Request timeout in seconds
        """
        self.simulator_url = simulator_url
        self.studenttask_url = studenttask_url
        self.timeout = timeout
        self.app = FastAPI()
        self.is_registered = False

        # Register heartbeat endpoint
        self.app.get("/heartbeat/")(self.return_if_alive)

    def register_with_simulator(self) -> None:
        """
        Register this studenttask instance with the simulator.

        Makes POST request to simulator's registration endpoint with this service's URL.
        Sets is_registered flag on successful registration.

        Raises:
            requests.RequestException: If registration request fails
        """
        response = requests.post(
            f"{self.simulator_url}/api/register/task",
            json={"studenttask_url": self.studenttask_url},
            timeout=self.timeout,
        )
        if response.status_code == 200:
            self.is_registered = True
            logger.info(f"Registered with Simulator at: '{self.simulator_url}'")

    def return_if_alive(self) -> HeartbeatInfo:
        """
        Handle heartbeat endpoint requests.

        Returns:
            HeartbeatInfo: Response indicating service is alive
        """
        logger.info("Received GET request for heartbeat")
        return HeartbeatInfo(is_alive=True)

    def get_app(self) -> FastAPI:
        """
        Get the FastAPI application instance.

        Returns:
            FastAPI: The configured FastAPI application
        """
        return self.app

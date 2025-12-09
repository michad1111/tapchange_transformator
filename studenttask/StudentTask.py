"""
Name: Michel Hadwiger
Matriculation number: 11814638
"""

import os

import uvicorn
from loguru import logger

from .api_client import APIClient, SimulatorUpdateData
from .eSteps import eSteps


class StudentTask:
    """
    Main class implementing voltage control logic for a smart grid transformer.

    Handles tap changer control, spreading detection and range control factor adjustments
    based on voltage measurements from the grid simulator.
    """

    # Constants for connection settings
    TIMEOUT_DURATION: float = 1.0
    STUDENTTASK_PORT: int = 7777
    SIMULATOR_PORT: int = 8000

    def __init__(self) -> None:
        """
        Initialize StudentTask with connection settings and API endpoints.

        Sets up URLs for simulator and own service connections, initializes API client
        and registers control calculation endpoint.
        """
        logger.info("Initializing StudentTask")

        # Set up URLs for local connections, allowing override of simulator URL via environment variable
        if not (backend_url := os.environ.get("BACKEND_URL")):
            # Default local URLs if no environment override
            self.backend_url = f"http://localhost:{self.SIMULATOR_PORT}/"
            self.own_studenttask_url = (
                f"http://host.docker.internal:{self.STUDENTTASK_PORT}/"
            )
            logger.warning(
                "No BACKEND_URL environment variable found, using localhost and host.docker.internal"
            )
        else:
            # Use environment provided URLs
            self.backend_url = backend_url
            self.own_studenttask_url = os.environ.get(
                "STUDENTTASK_URL", f"http://localhost:{self.STUDENTTASK_PORT}/"
            )
            logger.success(
                f"Using BACKEND_URL environment variable: {self.backend_url}"
                f" and STUDENTTASK_URL environment variable: {self.own_studenttask_url}"
            )

        logger.debug(f"StudentTask URL: {self.own_studenttask_url}")
        logger.debug(f"Simulator URL: {self.backend_url}")

        # Initialize API client for communication with simulator
        self.api_client = APIClient(
            self.backend_url, self.own_studenttask_url, self.TIMEOUT_DURATION
        )
        self.app = self.api_client.get_app()
        logger.info("API client initialized")

        # Register the calculate_control endpoint to handle POST requests
        self.app.post("/calculateControl/")(self.calculate_control)
        logger.info("Registered calculateControl endpoint")

    def calculate_control(self, simulator: SimulatorUpdateData) -> dict:
        """
        This is where you, the student, write your own algorithm for the tapchanger!
        You only have to change the values for the variables in the return statement, the Simulator will
        get updated with these values.

        simulator has the following functions to help with the logic:
            Getting values:
                Function name                                       - Type              - Explanation
                ===========================================================================================================================================
                simulator.get_min_street_voltage()                  - float             - Method to get the minimum street voltage.
                simulator.get_max_street_voltage()                  - float             - Method to get the maximum street voltage.
                simulator.get_range_control_factor()                - float             - Method to get the current range control factor.
                simulator.get_current_tapchanger_position()         - int               - Method to get the current tapchanger position.
                simulator.get_tapchanger_voltage_factor(int step)   - float             - Method to get the voltage factor for a given step.

            Changing values:
                Variable name                                             - Explanation
                ================================================================================================================================
                tapchanger_behavior (int)                                 - Set the tapchanger behavior.
                spreading_detected (bool)                                 - Set the spreading detected.
                range_control_factor (float)                              - Set the range control factor.

            Existing values:
                Variable name           - Type
                ===============================
                simulator.upper_voltage_band      - float
                simulator.lower_voltage_band      - float
                simulator.upper_voltage_safety    - float
                simulator.lower_voltage_safety    - float
                simulator.min_step_position       - int
                simulator.max_step_position       - int
                simulator.nominal_voltage         - float
                simulator.task                    - str
        """

        logger.info(
            "Name: Hadwiger, MatrNr: 11814638"
        )

        # Variables needed to return at end of algorithm
        is_spreading = False
        new_pos = eSteps.STAY
        range_control_factor = simulator.get_range_control_factor()

        # ============================================
        # TODO: WRITE YOUR OWN ALGORITHM HERE
        # This can be deleted befor you start programming
        task_nr = 2

        logger.info(f"Aufgabe {task_nr}")
        # Aufgabe 2: Warning Limits
        if task_nr == 2:
            use_safety_limits = True
        else:
            use_safety_limits = False

        upper_safety = simulator.upper_voltage_safety
        lower_safety = simulator.lower_voltage_safety
        # TODO: make safety limits configurable
        if use_safety_limits:
            upper_limit = upper_safety
            lower_limit = lower_safety
        else:
            upper_limit = simulator.upper_voltage_band
            lower_limit = simulator.lower_voltage_band

        # Getting the current tapposition, typecasting it to a float
        # and printing it out with a python f-string and two decimals
        current_tap_position = int(simulator.get_current_tapchanger_position())

        min_street_voltage = simulator.get_min_street_voltage()
        max_street_voltage = simulator.get_max_street_voltage()
        range_control_factor = simulator.get_range_control_factor()
        # tapchanger_voltage_factor = simulator.get_tapchanger_voltage_factor()

        min_step = simulator.min_step_position
        max_step = simulator.max_step_position

        logger.info(
            f"Current: Tap {current_tap_position:.2f}, Voltages (min/max) ({min_street_voltage:.2f}, {max_street_voltage:.2f})V, \n \
                {'safety limits' if use_safety_limits else 'hard limits'} applied - Limits ({lower_limit:.2f}, {upper_limit:.2f})V - delta (lower/upper) ({lower_safety - simulator.lower_voltage_band:.2f}, {simulator.upper_voltage_band - upper_safety:.2f})V"
        )
        if min_street_voltage < lower_limit:
            if current_tap_position + 1 <= max_step:
                new_pos = eSteps.SWITCHHIGHER
                logger.info(
                    f"Umin ({min_street_voltage:.2f}V) < lower band ({lower_limit:.2f}V). Switching higher. Tap {current_tap_position} -> {current_tap_position + 1}"
                )
            else:
                new_pos = eSteps.STAY
                logger.info(
                    f"Umin ({min_street_voltage:.2f}V) < lower band ({lower_limit:.2f}V). Tap {current_tap_position} at max Tap ({max_step}).  Staying at Tap {current_tap_position}"
                )
            
        elif max_street_voltage > upper_limit:
            if current_tap_position - 1 >= min_step:
                new_pos = eSteps.SWITCHLOWER
                logger.info(
                    f"Umax ({max_street_voltage:.2f}V) > upper band ({upper_limit:.2f}V). Switching lower. Tap {current_tap_position} -> {current_tap_position - 1}"
                )
            else:
                new_pos = eSteps.STAY
                logger.info(
                    f"Umax ({max_street_voltage:.2f}V) > upper band ({upper_limit:.2f}V). Tap {current_tap_position} at min Tap ({max_step}).  Staying at Tap {current_tap_position}"
                )
        else:
            new_pos = eSteps.STAY
            # range_control_factor -= 0.0
            # is_spreading = False
            logger.info(
                f"Voltages within bands ({upper_limit:.2f}V - {upper_limit:.2f}V). Staying. Tap {current_tap_position}"
            )

        # ============================================

        # Do NOT change this return.
        # Only change the value of the variables themself
        logger.info(
            f"Final decisions - Position: {new_pos}, Spreading: {is_spreading}, Factor: {range_control_factor}"
        )
        return {
            "tapchanger_behavior": new_pos,
            "spreading_detected": is_spreading,
            "range_control_factor": range_control_factor,
        }

    def run(self) -> None:
        """
        Start the StudentTask service.

        Registers with simulator and starts FastAPI server to handle control requests.

        Returns:
            None

        Raises:
            None
        """
        logger.info("Starting StudentTask")
        # Register this instance with the simulator before starting
        self.api_client.register_with_simulator()
        logger.info("Registered with simulator")

        # Start the FastAPI server
        logger.info(f"Starting FastAPI server on port {self.STUDENTTASK_PORT}")
        uvicorn.run(self.app, host="0.0.0.0", port=self.STUDENTTASK_PORT)


def main() -> None:
    """
    Entry point function that creates and runs a StudentTask instance.

    Returns:
        None

    Raises:
        None
    """
    logger.info("Starting main function")
    # Create and run the student task instance
    student_task = StudentTask()
    student_task.run()


if __name__ == "__main__":
    main()

"""
Name: Max Mustermann
Matriculation number: 123456
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
    SIMULATOR_PORT: int = 3000

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
            "Name: Mustermann \
                    \nMatrNr: 123456"
        )

        # Variables needed to return at end of algorithm
        is_spreading = False
        new_pos = eSteps.STAY
        range_control_factor = simulator.get_range_control_factor()

        # ============================================
        # TODO: WRITE YOUR OWN ALGORITHM HERE
        # This can be deleted befor you start programming

        # Getting the current tapposition, typecasting it to a float
        # and printing it out with a python f-string and two decimals
        current_tap_position = float(simulator.get_current_tapchanger_position())
        if current_tap_position == 0 and new_pos == eSteps.STAY:
            logger.info(f"Current Tap: {current_tap_position:.2f}")

        # Stupid logic for tapchanger
        if current_tap_position == 0:
            new_pos = eSteps.SWITCHHIGHER
            range_control_factor -= 0.1
            is_spreading = False
        elif current_tap_position == 1 or current_tap_position == -1:
            new_pos = eSteps.SWITCHLOWER
            range_control_factor += 0.1
            is_spreading = True
        else:
            new_pos = eSteps.STAY
            range_control_factor = 0.5
            is_spreading = False
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

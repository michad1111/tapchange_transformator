from unittest.mock import Mock

import pytest

from studenttask.eSteps import eSteps
from studenttask.StudentTask import StudentTask


@pytest.mark.unit
class TestStudentTask:
    @pytest.fixture
    def student_task(self):
        # Create a fresh StudentTask instance for each test
        return StudentTask()

    @pytest.fixture
    def mock_simulator_data(self):
        """Create a mock SimulatorUpdateData with configurable values"""
        mock = Mock()
        # Set default voltage band limits and safety thresholds
        mock.upper_voltage_band = 240
        mock.lower_voltage_band = 220
        mock.upper_voltage_safety = 238
        mock.lower_voltage_safety = 222
        mock.nominal_voltage = 230
        mock.max_step_position = 2
        mock.min_step_position = -2

        # Define helper methods that return default values
        # These can be overridden in individual tests
        mock.get_range_control_factor = lambda: 1.0
        mock.get_current_tapchanger_position = lambda: 0
        mock.get_tapchanger_voltage_factor = lambda pos: 1.0 + (pos * 0.02)
        mock.get_min_street_voltage = lambda: 230
        mock.get_max_street_voltage = lambda: 230
        mock.task = lambda: 1

        return mock

    def test_normal_operation_no_violations(
        self, student_task: StudentTask, mock_simulator_data: Mock
    ):
        """Test that tap changer stays in position when voltages are within limits"""
        # When voltages are within normal operating bands,
        # the system should maintain current position and settings
        mock_simulator_data.task = 1
        result = student_task.calculate_control(mock_simulator_data)

        # Verify tap changer stays put, no spreading detected, and control factor unchanged
        assert result["tapchanger_behavior"] == eSteps.STAY
        assert result["spreading_detected"] == False
        assert result["range_control_factor"] == 1.0

    # TODO: WRITE 5 MORE TESTS (Yes the one above is just an example to show how to use the Mock Module and doesn't count)

    # Task 1
    def test_upper_voltage_band_violation(
        self, student_task: StudentTask, mock_simulator_data: Mock
    ):
        """Test that tap changer steps down when voltage exceeds upper band"""
        mock_simulator_data.get_max_street_voltage = lambda: 245
        mock_simulator_data.task = 1

        result = student_task.calculate_control(mock_simulator_data)

        assert result["tapchanger_behavior"] == eSteps.SWITCHLOWER
        assert result["spreading_detected"] == False
        assert result["range_control_factor"] == 1.0

    def test_lower_voltage_band_violation(
        self, student_task: StudentTask, mock_simulator_data: Mock
    ):
        """Test that tap changer steps up when voltage falls below lower band"""
        mock_simulator_data.get_min_street_voltage = lambda: 215
        mock_simulator_data.task = 1

        result = student_task.calculate_control(mock_simulator_data)

        assert result["tapchanger_behavior"] == eSteps.SWITCHHIGHER
        assert result["spreading_detected"] == False
        assert result["range_control_factor"] == 1.0

    def test_tapchanger_at_max_position(
        self, student_task: StudentTask, mock_simulator_data: Mock
    ):
        """Test that tap changer does not exceed max position when stepping up"""
        mock_simulator_data.get_min_street_voltage = lambda: 215
        mock_simulator_data.get_current_tapchanger_position = lambda: 2
        mock_simulator_data.task = 1

        result = student_task.calculate_control(mock_simulator_data)

        assert result["tapchanger_behavior"] == eSteps.STAY
        assert result["spreading_detected"] == False
        assert result["range_control_factor"] == 1.0

    def test_tapchanger_at_min_position(
        self, student_task: StudentTask, mock_simulator_data: Mock
    ):
        """Test that tap changer does not exceed min position when stepping down"""
        mock_simulator_data.get_max_street_voltage = lambda: 245
        mock_simulator_data.get_current_tapchanger_position = lambda: -2
        mock_simulator_data.task = 1

        result = student_task.calculate_control(mock_simulator_data)

        assert result["tapchanger_behavior"] == eSteps.STAY
        assert result["spreading_detected"] == False
        assert result["range_control_factor"] == 1.0

    # Task 2
    def test_upper_safety_violation(
        self, student_task: StudentTask, mock_simulator_data: Mock
    ):
        """Test that tap changer steps down when safety voltage is exceeded"""
        mock_simulator_data.get_max_street_voltage = lambda: 239
        mock_simulator_data.task = 2

        result = student_task.calculate_control(mock_simulator_data)

        assert result["tapchanger_behavior"] == eSteps.SWITCHLOWER
        assert result["spreading_detected"] == False
        assert result["range_control_factor"] == 1.0

    def test_lower_safety_violation(
        self, student_task: StudentTask, mock_simulator_data: Mock
    ):
        """Test that tap changer steps down when safety voltage is exceeded"""
        mock_simulator_data.get_min_street_voltage = lambda: 221
        mock_simulator_data.task = 2

        result = student_task.calculate_control(mock_simulator_data)

        assert result["tapchanger_behavior"] == eSteps.SWITCHHIGHER
        assert result["spreading_detected"] == False
        assert result["range_control_factor"] == 1.0

    # Task 3
    def test_spreading_detected(
        self, student_task: StudentTask, mock_simulator_data: Mock
    ):
        """Test that spreading is detected"""
        mock_simulator_data.get_min_street_voltage = lambda: 215
        mock_simulator_data.get_max_street_voltage = lambda: 238
        mock_simulator_data.task = 3

        result = student_task.calculate_control(mock_simulator_data)

        assert result["tapchanger_behavior"] == eSteps.STAY
        assert result["spreading_detected"] == True
        assert result["range_control_factor"] == 1.0

    # Task 4
    def test_adjust_range_control_factor(
        self, student_task: StudentTask, mock_simulator_data: Mock
    ):
        """Test that range control factor is adjusted when spreading is detected"""
        mock_simulator_data.get_min_street_voltage = lambda: 215
        mock_simulator_data.get_max_street_voltage = lambda: 238
        mock_simulator_data.task = 4

        result = student_task.calculate_control(mock_simulator_data)

        assert result["tapchanger_behavior"] == eSteps.STAY
        assert result["spreading_detected"] == True
        assert result["range_control_factor"] != 1.0

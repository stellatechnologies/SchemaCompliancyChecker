import unittest
import json
from pathlib import Path
from typing import Dict, Any

from main import validate_schema, validate_data, validate_table_names, SchemaValidatorLogger, validate_column_names, validate_column_types, validate_foreign_keys, validate_properties

class TestSchemaValidator(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.scenarios_dir = Path(__file__).parent / 'scenarios'
        
    def run_scenario(self, scenario_dir: str) -> None:
        """Run a test scenario from the scenarios directory"""
        scenario_path = self.scenarios_dir / scenario_dir
        print(f"\nRunning scenario: {scenario_dir}")
        
        # Load scenario definition
        with open(scenario_path / 'scenario.json') as f:
            scenario = json.load(f)
            
        # Load schema and data
        try:
            with open(scenario_path / scenario['schema_file']) as f:
                schema = json.load(f)
            with open(scenario_path / scenario['data_file']) as f:
                data = json.load(f)
        except FileNotFoundError as e:
            print(f"Error loading files: {e}")
            raise
            
        # Create logger for this test
        logger = SchemaValidatorLogger()
        
        if 'schema_validation' in scenario_dir:
            print(f"Running schema validation test")
            try:
                validate_schema(schema, logger)
                if scenario['expected_results']['structural_errors']:
                    self.fail("Expected ValueError was not raised")
            except ValueError:
                pass
        elif 'data_validation' in scenario_dir:
            print(f"Running data validation test")
            validate_schema(schema, logger)
            try:
                validate_data(data, logger)
                if scenario['expected_results']['structural_errors']:
                    self.fail("Expected ValueError was not raised")
            except ValueError:
                pass
        elif 'table_validation' in scenario_dir:
            print(f"Running table validation test")
            validate_schema(schema, logger)
            try:
                validate_data(data, logger)
            except ValueError:
                pass
            validate_table_names(data, schema, logger)
        elif 'column_validation' in scenario_dir:
            print(f"Running column validation test")
            validate_schema(schema, logger)
            try:
                validate_data(data, logger)
            except ValueError:
                pass
            validate_column_names(data, schema, logger)
        elif 'type_validation' in scenario_dir:
            print(f"Running type validation test")
            validate_schema(schema, logger)
            try:
                validate_data(data, logger)
            except ValueError:
                pass
            validate_column_types(data, schema, logger)
        elif 'foreign_key_validation' in scenario_dir:
            print(f"Running foreign key validation test")
            validate_schema(schema, logger)
            try:
                validate_data(data, logger)
            except ValueError:
                pass
            validate_foreign_keys(data, schema, logger)
        elif 'property_validation' in scenario_dir:
            print(f"Running property validation test")
            validate_schema(schema, logger)
            try:
                validate_data(data, logger)
            except ValueError:
                pass
            validate_properties(data, schema, logger)
        else:
            print(f"Running schema validation test")
            try:
                validate_schema(schema, logger)
                if scenario['expected_results']['structural_errors']:
                    self.fail("Expected ValueError was not raised")
            except ValueError:
                pass
        
        # Add debug output before checking results
        print("\nActual results:")
        print(f"Structural errors: {logger.structural_errors}")
        print(f"Warnings: {logger.warnings}")
        print(f"Errors: {logger.errors}")
        print(f"Info: {logger.info}")
        print("\nExpected results:")
        print(f"Structural errors: {scenario['expected_results']['structural_errors']}")
        print(f"Warnings: {scenario['expected_results']['warnings']}")
        print(f"Errors: {scenario['expected_results']['errors']}")
        print(f"Info: {scenario['expected_results']['info']}")
        
        # Check expected results
        expected = scenario['expected_results']
        
        # Check structural errors
        for expected_error in expected['structural_errors']:
            self.assertTrue(
                any(expected_error in e for e in logger.structural_errors),
                f"Expected structural error not found: {expected_error}"
            )
        
        # Check warnings
        for expected_warning in expected['warnings']:
            self.assertTrue(
                any(expected_warning in w for w in logger.warnings),
                f"Expected warning not found: {expected_warning}"
            )
        
        # Check errors
        for expected_error in expected['errors']:
            self.assertTrue(
                any(expected_error in e for e in logger.errors),
                f"Expected error not found: {expected_error}"
            )
            
        # Check info messages
        for expected_info in expected['info']:
            self.assertTrue(
                any(expected_info in i for i in logger.info),
                f"Expected info message not found: {expected_info}"
            )
            
        # Check counts match
        self.assertEqual(len(logger.structural_errors), len(expected['structural_errors']),
                        "Unexpected number of structural errors")
        self.assertEqual(len(logger.warnings), len(expected['warnings']),
                        "Unexpected number of warnings")
        self.assertEqual(len(logger.errors), len(expected['errors']),
                        "Unexpected number of errors")
        self.assertEqual(len(logger.info), len(expected['info']),
                        "Unexpected number of info messages")

    def test_schema_validation(self):
        """Run all schema validation test scenarios"""
        schema_validation_dir = self.scenarios_dir / 'schema_validation'
        for scenario_dir in schema_validation_dir.iterdir():
            if scenario_dir.is_dir():
                with self.subTest(scenario=scenario_dir.name):
                    self.run_scenario(f"schema_validation/{scenario_dir.name}")

    def test_data_validation(self):
        """Run all data validation test scenarios"""
        data_validation_dir = self.scenarios_dir / 'data_validation'
        for scenario_dir in data_validation_dir.iterdir():
            if scenario_dir.is_dir():
                with self.subTest(scenario=scenario_dir.name):
                    self.run_scenario(f"data_validation/{scenario_dir.name}")

    def test_table_validation(self):
        """Run all table validation test scenarios"""
        table_validation_dir = self.scenarios_dir / 'table_validation'
        for scenario_dir in table_validation_dir.iterdir():
            if scenario_dir.is_dir():
                with self.subTest(scenario=scenario_dir.name):
                    self.run_scenario(f"table_validation/{scenario_dir.name}")

    def test_column_validation(self):
        """Run all column validation test scenarios"""
        column_validation_dir = self.scenarios_dir / 'column_validation'
        for scenario_dir in column_validation_dir.iterdir():
            if scenario_dir.is_dir():
                with self.subTest(scenario=scenario_dir.name):
                    self.run_scenario(f"column_validation/{scenario_dir.name}")

    def test_type_validation(self):
        """Run all type validation test scenarios"""
        type_validation_dir = self.scenarios_dir / 'type_validation'
        for scenario_dir in type_validation_dir.iterdir():
            if scenario_dir.is_dir():
                with self.subTest(scenario=scenario_dir.name):
                    self.run_scenario(f"type_validation/{scenario_dir.name}")

    def test_foreign_key_validation(self):
        """Run all foreign key validation test scenarios"""
        foreign_key_validation_dir = self.scenarios_dir / 'foreign_key_validation'
        for scenario_dir in foreign_key_validation_dir.iterdir():
            if scenario_dir.is_dir():
                with self.subTest(scenario=scenario_dir.name):
                    self.run_scenario(f"foreign_key_validation/{scenario_dir.name}")

    def test_property_validation(self):
        """Run all property validation test scenarios"""
        property_validation_dir = self.scenarios_dir / 'property_validation'
        for scenario_dir in property_validation_dir.iterdir():
            if scenario_dir.is_dir():
                with self.subTest(scenario=scenario_dir.name):
                    self.run_scenario(f"property_validation/{scenario_dir.name}")
                    
    
"""
Centralized validation functions for defensive coding against input errors.

Provides validation for files, data structures, dates, numeric values, and ranges.
All validators raise exceptions with descriptive error messages on validation failure.
"""

import os
from datetime import datetime


def validate_file_exists(filepath: str) -> None:
    """
    Validate that a file exists and is readable.
    
    Args:
        filepath: Path to the file to validate
        
    Raises:
        FileNotFoundError: If file does not exist
        PermissionError: If file exists but is not readable
    """
    if not os.path.exists(filepath):
        raise FileNotFoundError(f"File not found: '{filepath}'")
    
    if not os.path.isfile(filepath):
        raise FileNotFoundError(f"Path is not a file: '{filepath}'")
    
    if not os.access(filepath, os.R_OK):
        raise PermissionError(f"File is not readable: '{filepath}'")


def validate_date(year: int, month: int, day: int) -> None:
    """
    Validate date components for valid calendar date.
    
    Args:
        year: Year value
        month: Month value (1-12)
        day: Day value (1-31)
        
    Raises:
        ValueError: If date components are invalid
    """
    if month < 1 or month > 12:
        raise ValueError(f"Invalid month: {month} (must be 1-12)")
    
    if day < 1 or day > 31:
        raise ValueError(f"Invalid day: {day} (must be 1-31)")
    
    try:
        datetime(year, month, day)
    except ValueError as e:
        raise ValueError(f"Invalid date: {year}-{month:02d}-{day:02d} - {str(e)}")


def validate_age_string(age_str: str) -> tuple:
    """
    Validate age format "YY-MM" or "YY" and return parsed tuple.
    
    Args:
        age_str: Age string in format "YY-MM" or "YY"
        
    Returns:
        Tuple of (age_years, age_months)
        
    Raises:
        ValueError: If format is invalid or values are out of range
    """
    if not age_str or not isinstance(age_str, str):
        raise ValueError(f"Invalid age string: {age_str} (must be string)")
    
    if "-" in age_str:
        parts = age_str.split("-")
        if len(parts) != 2:
            raise ValueError(f"Invalid age format: '{age_str}' (expected YY-MM)")
        
        try:
            age_year = int(parts[0])
            age_month = int(parts[1])
        except ValueError:
            raise ValueError(f"Invalid age format: '{age_str}' (age components must be numeric)")
        
        if age_year < 0 or age_year > 150:
            raise ValueError(f"Invalid age year: {age_year} (must be 0-150)")
        
        if age_month < 0 or age_month > 11:
            raise ValueError(f"Invalid age month: {age_month} (must be 0-11)")
        
        return age_year, age_month
    else:
        try:
            age_year = int(age_str)
        except ValueError:
            raise ValueError(f"Invalid age format: '{age_str}' (expected YY or YY-MM)")
        
        if age_year < 0 or age_year > 150:
            raise ValueError(f"Invalid age year: {age_year} (must be 0-150)")
        
        return age_year, 0


def validate_scenario_data(data: dict) -> None:
    """
    Validate scenario JSON structure and required fields.
    
    Args:
        data: Scenario data dictionary to validate
        
    Raises:
        ValueError: If required fields are missing or invalid
    """
    if not isinstance(data, dict):
        raise ValueError("Scenario data must be a dictionary")
    
    if "birthdate" not in data:
        raise ValueError("Scenario data missing required field: 'birthdate'")
    
    if "scenarios" not in data:
        raise ValueError("Scenario data missing required field: 'scenarios'")
    
    if not isinstance(data["scenarios"], list):
        raise ValueError("'scenarios' field must be a list")
    
    if len(data["scenarios"]) == 0:
        raise ValueError("'scenarios' list is empty")
    
    # Validate each scenario
    for i, scenario in enumerate(data["scenarios"]):
        if not isinstance(scenario, dict):
            raise ValueError(f"Scenario {i} is not a dictionary")
        
        required_fields = ["scenario_name", "start_date", "end_date"]
        for field in required_fields:
            if field not in scenario:
                raise ValueError(f"Scenario {i} missing required field: '{field}'")


def validate_benefits_data(data: dict) -> None:
    """
    Validate benefits JSON structure and age ranges.
    
    Args:
        data: Benefits data dictionary to validate
        
    Raises:
        ValueError: If structure is invalid or data is missing
    """
    if not isinstance(data, dict):
        raise ValueError("Benefits data must be a dictionary")
    
    if "benefits" not in data:
        raise ValueError("Benefits data missing required field: 'benefits'")
    
    if not isinstance(data["benefits"], list):
        raise ValueError("'benefits' field must be a list")
    
    if len(data["benefits"]) == 0:
        raise ValueError("'benefits' list is empty")
    
    # Validate each benefit entry
    for i, entry in enumerate(data["benefits"]):
        if not isinstance(entry, dict):
            raise ValueError(f"Benefit entry {i} is not a dictionary")
        
        if "age" not in entry or "benefit" not in entry:
            raise ValueError(f"Benefit entry {i} missing required fields: 'age', 'benefit'")
        
        try:
            validate_age_string(entry["age"])
        except ValueError as e:
            raise ValueError(f"Benefit entry {i} has invalid age: {str(e)}")
        
        if not isinstance(entry["benefit"], (int, float)):
            raise ValueError(f"Benefit entry {i} benefit must be numeric, got {type(entry['benefit'])}")


def validate_earning_limits(data: dict) -> None:
    """
    Validate earning limits JSON structure and rules.
    
    Args:
        data: Earning limits data dictionary to validate
        
    Raises:
        ValueError: If structure is invalid or required fields missing
    """
    if not isinstance(data, dict):
        raise ValueError("Earning limits data must be a dictionary")
    
    if "rules" not in data:
        raise ValueError("Earning limits data missing required field: 'rules'")
    
    if not isinstance(data["rules"], list):
        raise ValueError("'rules' field must be a list")
    
    if len(data["rules"]) == 0:
        raise ValueError("'rules' list is empty")
    
    # Validate each rule
    for i, rule in enumerate(data["rules"]):
        if not isinstance(rule, dict):
            raise ValueError(f"Rule {i} is not a dictionary")
        
        required_fields = ["year", "age_before_nra", "age_nra_year"]
        for field in required_fields:
            if field not in rule:
                raise ValueError(f"Rule {i} missing required field: '{field}'")


def validate_income_csv_row(row: dict, row_number: int) -> None:
    """
    Validate income CSV row for correct structure and value ranges.
    
    Args:
        row: CSV row as dictionary
        row_number: Row number in CSV (for error messages)
        
    Raises:
        ValueError: If row data is invalid
    """
    required_fields = ["year", "month", "amount"]
    for field in required_fields:
        if field not in row:
            raise ValueError(f"CSV row {row_number} missing required field: '{field}'")
    
    try:
        year = int(row["year"])
        month = int(row["month"])
        amount = float(row["amount"])
    except (ValueError, TypeError) as e:
        raise ValueError(f"CSV row {row_number} has non-numeric value: {str(e)}")
    
    if year < 1900 or year > 2100:
        raise ValueError(f"CSV row {row_number}: year {year} out of reasonable range (1900-2100)")
    
    if month < 1 or month > 12:
        raise ValueError(f"CSV row {row_number}: month {month} must be 1-12")
    
    if amount < 0:
        raise ValueError(f"CSV row {row_number}: amount {amount} cannot be negative")


def validate_positive_number(value: float, field_name: str) -> None:
    """
    Validate that a number is non-negative.
    
    Args:
        value: The value to validate
        field_name: Name of the field (for error messages)
        
    Raises:
        ValueError: If value is negative or not numeric
    """
    if not isinstance(value, (int, float)):
        raise ValueError(f"{field_name} must be numeric, got {type(value)}")
    
    if value < 0:
        raise ValueError(f"{field_name} cannot be negative: {value}")


def validate_data_not_empty(data, data_name: str) -> None:
    """
    Validate that loaded data is not None or empty.
    
    Args:
        data: The data to validate
        data_name: Name of the data (for error messages)
        
    Raises:
        ValueError: If data is None or empty
    """
    if data is None:
        raise ValueError(f"{data_name} is None")
    
    if isinstance(data, (dict, list)) and len(data) == 0:
        raise ValueError(f"{data_name} is empty")

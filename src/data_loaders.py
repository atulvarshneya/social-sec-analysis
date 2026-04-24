from src.config import config  # For loading configuration settings (file paths, parameters)
from src.validators import (
    validate_file_exists, validate_scenario_data, validate_benefits_data,
    validate_earning_limits, validate_income_csv_row, validate_age_string,
    validate_data_not_empty
)
from src.logger import logger, log_file_loaded, log_file_error, log_validation_error
import json  # For parsing JSON data files (benefits, earning limits, scenarios)
import pandas as pd  # For reading CSV income data

def load_scenario_data():
    """Load retirement scenarios from JSON file with validation.
    
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If JSON is malformed or missing required fields
    """
    try:
        validate_file_exists(config.SCENARIO_DATA_FILE)
    except (FileNotFoundError, PermissionError) as e:
        log_file_error(config.SCENARIO_DATA_FILE, str(e))
        raise
    
    try:
        with open(config.SCENARIO_DATA_FILE, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {str(e)}"
        log_file_error(config.SCENARIO_DATA_FILE, error_msg)
        raise ValueError(error_msg)
    
    try:
        validate_scenario_data(data)
    except ValueError as e:
        log_validation_error(config.SCENARIO_DATA_FILE, str(e))
        raise
    
    birthdate = data['birthdate']
    scenarios = data.get('scenarios', [])
    log_file_loaded(config.SCENARIO_DATA_FILE, len(scenarios))
    
    for scenario in scenarios:
        # Calculate total months of retirement based on start and end dates
        eyear, emonth, eday = map(int, scenario['end_date'].split('-'))
        syear, smonth, sday = map(int, scenario['start_date'].split('-'))
        scenario['months'] = (eyear - syear) * 12 + (emonth - smonth) + 1 # Calculate total months of retirement, start and end months inclusive, ignore days for simplicity
        # Add birthdate to each scenario for use in calculations (e.g., determining age at retirement)
        scenario['birthdate'] = birthdate  # Add birthdate to each scenario for use in calculations
    return scenarios


def load_earning_limits() -> dict:
    """
    Load SSA earning limits and reduction factors by year and earnings test phase.
    
    Returns dict with rules: each rule contains year, phase ('age_before_nra', 'age_nra_year', 'age_after_nra'),
    annual income limit, and reduction factor (e.g., $1 reduction per $3 excess income).
    
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If JSON is malformed or missing required fields
    """
    try:
        validate_file_exists(config.EARNING_LIMITS_FILE)
    except (FileNotFoundError, PermissionError) as e:
        log_file_error(config.EARNING_LIMITS_FILE, str(e))
        raise
    
    try:
        with open(config.EARNING_LIMITS_FILE, 'r') as f:
            data = json.load(f)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {str(e)}"
        log_file_error(config.EARNING_LIMITS_FILE, error_msg)
        raise ValueError(error_msg)
    
    try:
        validate_earning_limits(data)
    except ValueError as e:
        log_validation_error(config.EARNING_LIMITS_FILE, str(e))
        raise
    
    rules = data.get('rules', [])
    log_file_loaded(config.EARNING_LIMITS_FILE, len(rules))
    return rules


def parse_age_str(age_str: str) -> tuple:
    """
    Parse age string in format 'years-months' or just 'years' into (age_years, age_months) tuple.
    Example: '62-06' returns (62, 6); '70' returns (70, 0).
    
    Raises:
        ValueError: If age format is invalid or values are out of range
    """
    return validate_age_string(age_str)


def load_benefits_data() -> dict:
    """
    Load Primary Insurance Amount (PIA) by age at retirement and interpolate for intermediate months.
    
    SSA provides benefit amounts at key ages (e.g., 62, 63, FRA, 70).
    This function interpolates monthly benefits between these key points.
    
    Returns dict mapping 'year-month' strings to benefit amounts (e.g., '62-06' -> 1234.56).
    
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If JSON is malformed or missing required fields
    """
    try:
        validate_file_exists(config.BENEFITS_BY_AGE_FILE)
    except (FileNotFoundError, PermissionError) as e:
        log_file_error(config.BENEFITS_BY_AGE_FILE, str(e))
        raise
    
    try:
        with open(config.BENEFITS_BY_AGE_FILE, 'r') as f:
            raw_data = json.load(f)
    except json.JSONDecodeError as e:
        error_msg = f"Invalid JSON format: {str(e)}"
        log_file_error(config.BENEFITS_BY_AGE_FILE, error_msg)
        raise ValueError(error_msg)
    
    try:
        validate_benefits_data(raw_data)
    except ValueError as e:
        log_validation_error(config.BENEFITS_BY_AGE_FILE, str(e))
        raise
    
    nra = raw_data.get('normal_retirement_age', 67)  # Default NRA is 67 years
    config.NRA_AGE = nra  # Set NRA age in config for use in main calculations

    max_retirement_age = raw_data.get('max_retirement_age', 70)  # Default max retirement age is 70 years
    config.MAX_RETIREMENT_AGE = max_retirement_age  # Set max retirement age in config for use in main calculations

    data = raw_data['benefits']
    
    benefits = {}
    num_entries = len(data)
    for i, benefit_entry in enumerate(data):
        benefit = benefit_entry['benefit']
        age_str = benefit_entry['age']
        age_year, age_month = parse_age_str(age_str)

        # Interpolate monthly benefits between key ages (up to age 69)
        if age_year < 70 and i < num_entries - 1:
            # Linear interpolation between current and next benefit
            next_benefit_entry = data[i+1]
            next_benefit = next_benefit_entry['benefit']
            next_age_str = next_benefit_entry['age']
            next_age_year, next_age_month = parse_age_str(next_age_str)
            gap = (next_age_year - age_year) * 12 + (next_age_month - age_month)

            for month in range(age_month, age_month + gap):
                interpolated_benefit = benefit + (next_benefit - benefit) * ((month - age_month) / gap)
                interpolation_year = age_year
                interpolation_month = month
                if month >= 12:
                    interpolation_year += 1
                    interpolation_month = month % 12
                benefits[f"{interpolation_year}-{interpolation_month:02d}"] = round(interpolated_benefit, 2)
    
    # Add the final benefit
    last_benefit = data[-1]['benefit']
    last_age_str = data[-1]['age']
    last_age_year, last_age_month = parse_age_str(last_age_str)
    benefits[f"{last_age_year}-{last_age_month:02d}"] = round(last_benefit, 2)
    
    log_file_loaded(config.BENEFITS_BY_AGE_FILE, len(benefits))
    return benefits


def load_income_data() -> dict:
    """
    Load monthly income from CSV file into nested dictionary structure.
    
    CSV format: year, month, amount
    Missing months are treated as zero income during calculations.
    
    Returns nested dict: {year: {month: amount}}, e.g., {2026: {5: 3000.00, 6: 2500.00}}.
    
    Raises:
        FileNotFoundError: If file does not exist
        ValueError: If CSV is malformed or contains invalid data
    """
    try:
        validate_file_exists(config.INCOME_DATA_FILE)
    except (FileNotFoundError, PermissionError) as e:
        log_file_error(config.INCOME_DATA_FILE, str(e))
        raise
    
    income_data = {}
    
    try:
        df = pd.read_csv(config.INCOME_DATA_FILE)
    except Exception as e:
        error_msg = f"Failed to read CSV: {str(e)}"
        log_file_error(config.INCOME_DATA_FILE, error_msg)
        raise ValueError(error_msg)
    
    row_number = 0
    try:
        for row_number, (_, row) in enumerate(df.iterrows(), start=2):  # Start at 2 (accounting for header)
            try:
                validate_income_csv_row(row, row_number)
            except ValueError as e:
                log_validation_error(config.INCOME_DATA_FILE, str(e))
                raise
            
            year = int(row["year"])
            month = int(row["month"])
            amount = float(row["amount"])
            
            if year not in income_data:
                income_data[year] = {}
            income_data[year][month] = amount
    except ValueError as e:
        log_file_error(config.INCOME_DATA_FILE, str(e))
        raise
    
    log_file_loaded(config.INCOME_DATA_FILE, len(df))
    return income_data
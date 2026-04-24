from src.config import config
from src.validators import validate_positive_number
from src.logger import logger

# Helper functions for income calculations, earnings test phases, and benefit lookups.

def year_income_summation(income_data: dict, year: int, start_month: int = 1, end_month: int = 12) -> float:
    """
    Calculate total income for a given year between specified months (inclusive).
    
    Used for both full-year income (Jan-Dec) and prorated income (retirement month onward).
    Treats missing months as zero income.
    
    Args:
        income_data: Nested dict {year: {month: amount}}
        year: The year to sum income for
        start_month: Starting month (1-12), default 1
        end_month: Ending month (1-12), default 12
    
    Returns:
        Total income for the specified month range, or 0.0 if year not in data
        
    Raises:
        ValueError: If month values are out of valid range
    """
    # Validate month ranges
    if start_month < 1 or start_month > 12:
        raise ValueError(f"Invalid start_month: {start_month} (must be 1-12)")
    
    if end_month < 1 or end_month > 12:
        raise ValueError(f"Invalid end_month: {end_month} (must be 1-12)")
    
    if start_month > end_month:
        raise ValueError(f"Invalid month range: start_month ({start_month}) > end_month ({end_month})")
    
    total_income = 0.0
    if year in income_data:
        for month in range(1, 13):
            if (month < start_month) or (month > end_month):
                continue
            amount = income_data[year].get(month, 0.0)
            if amount < 0:
                logger.warning(f"Negative income found for {year}-{month:02d}: {amount} (treating as 0)")
                amount = 0.0
            total_income += amount
    return total_income


def identify_phase(current_year: int, current_month: int, birth_year: int, birth_month: int) -> str:
    """
    Determine the current earnings test phase based on age and Full Retirement Age.
    
    SSA applies different earnings test rules depending on the phase:
    - 'age_before_nra': Before the year reaching NRA (full reduction for excess income)
    - 'age_nra_year': During the year reaching NRA (special rules)
    - 'age_after_nra': At or after NRA (no earnings test applies)
    
    Args:
        current_year, current_month: Current month being evaluated
        birth_year, birth_month: Individual's birth date
    
    Returns:
        Phase string: 'age_before_nra', 'age_nra_year', or 'age_after_nra'
        
    Raises:
        ValueError: If month values are out of valid range
    """
    # Validate month ranges
    if current_month < 1 or current_month > 12:
        raise ValueError(f"Invalid current_month: {current_month} (must be 1-12)")
    
    if birth_month < 1 or birth_month > 12:
        raise ValueError(f"Invalid birth_month: {birth_month} (must be 1-12)")
    
    nra_year = birth_year + config.NRA_AGE
    nra_month = birth_month

    if (current_year == nra_year):
        if (current_month < nra_month):
            phase = "age_nra_year"
        else:
            phase = "age_after_nra"
    elif (current_year > nra_year):
        phase = "age_after_nra"
    else:
        phase = "age_before_nra"

    return phase


def lookup_benefit(benefits_data: dict, start_year: int, start_month: int, birth_year: int, birth_month: int) -> float:
    """
    Look up the Primary Insurance Amount (PIA) based on age at retirement.
    
    SSA calculates age using year and month (not day).
    Retrieves interpolated benefit from the benefits table.
    
    Args:
        benefits_data: Dict mapping 'year-month' strings to benefit amounts
        start_year, start_month: Retirement start date
        birth_year, birth_month: Birth date
    
    Returns:
        Monthly benefit amount (PIA) for the given age, or 0.0 if not found
        
    Raises:
        ValueError: If month values are out of valid range or benefit not found
    """
    # Validate month ranges
    if start_month < 1 or start_month > 12:
        raise ValueError(f"Invalid start_month: {start_month} (must be 1-12)")
    
    if birth_month < 1 or birth_month > 12:
        raise ValueError(f"Invalid birth_month: {birth_month} (must be 1-12)")
    
    # Calculate age in years and months at retirement
    age_years = start_year - birth_year
    if start_month < birth_month:  # SSA hasn't counted the birth month yet this year
        age_years -= 1
    age_months = start_month - birth_month
    if age_months < 0:
        age_months += 12
    
    # Cap age to max retirement age for benefits table lookup
    if age_years >= config.MAX_RETIREMENT_AGE:
        age_years = config.MAX_RETIREMENT_AGE
        age_months = 0

    age_str = f"{age_years}-{age_months:02d}"

    # Look up benefit amount for this age
    if age_str not in benefits_data:
        logger.warning(f"Benefit not found for age {age_str} (retirement {start_year}-{start_month:02d}, birth {birth_year}-{birth_month:02d}), returning 0.0")
        benefit = 0.0
    else:
        benefit = benefits_data[age_str]
    
    return benefit
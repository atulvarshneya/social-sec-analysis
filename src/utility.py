from src.config import config

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
    """
    total_income = 0.0
    if year in income_data:
        for month in range(1, 13):
            if (month < start_month) or (month > end_month):
                continue
            total_income += income_data[year].get(month, 0.0)
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
    """
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
    """
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
    benefit = benefits_data.get(age_str, 0.0)
    return benefit
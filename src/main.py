from src.config import config  # For loading configuration settings (file paths, parameters)
from src.data_loaders import load_scenario_data  # For loading retirement scenarios from JSON file
from src.data_loaders import load_earning_limits, load_benefits_data, load_income_data  # For loading data from various sources
from src.utility import year_income_summation, identify_phase, lookup_benefit  # For income calculations, phase identification, and benefit lookups
from src.reports import reports  # For generating Excel reports from results
from src.validators import validate_data_not_empty
from src.logger import logger, log_scenario_start, log_scenario_complete, log_data_check

def main():
    """
    Main execution: Load data and process all scenarios.
    For each scenario, calculate monthly benefits with earnings test applied.
    
    Raises:
        Exception: If any data loading or validation fails
    """
    try:
        # Load all reference data
        logger.info("Loading reference data...")
        rules = load_earning_limits()
        income_data = load_income_data()
        benefits = load_benefits_data()
        scenarios = load_scenario_data()
        
        # Validate loaded data
        validate_data_not_empty(rules, "Earning limits rules")
        validate_data_not_empty(income_data, "Income data")
        validate_data_not_empty(benefits, "Benefits data")
        validate_data_not_empty(scenarios, "Scenarios")
        
        log_data_check("All data loaded", "PASS", f"{len(scenarios)} scenarios ready")
        
    except Exception as e:
        logger.error(f"Failed to load data: {str(e)}")
        raise

    # Process each retirement scenario from the data file
    all_scenarios_results = {}  # Store results for all scenarios if needed for further analysis
    for scenario in scenarios:
        try:
            log_scenario_start(scenario['scenario_name'], scenario['start_date'])
            all_scenarios_results[scenario['scenario_name']] = {}  # Initialize results storage for this scenario
            
            # Parse scenario parameters
            start_year, start_month, start_day = map(int, scenario["start_date"].split('-'))
            birth_year, birth_month, birth_day = map(int, scenario["birthdate"].split('-'))

            # Get initial benefit based on retirement age
            try:
                monthly_benefit = lookup_benefit(benefits, start_year, start_month, birth_year, birth_month)
                if monthly_benefit == 0.0:
                    logger.warning(f"Initial benefit calculation returned 0.0 for scenario '{scenario['scenario_name']}'")
            except (ValueError, KeyError) as e:
                logger.error(f"Failed to calculate initial benefit for scenario '{scenario['scenario_name']}': {str(e)}")
                raise
            
            logger.info(f"Initial monthly benefit: {monthly_benefit}")

            # Track all monthly data and annual withholding for this scenario
            scenario_table = all_scenarios_results[scenario['scenario_name']]  # {year: {month: {eligible_benefit, monthly_income, phase, income_limit, paid_benefit}}}
            annual_total_withheld = {}  # {year: total_withheld} - tracks cumulative reductions per year

            # ===== MONTHLY LOOP: Process each month of retirement =====
            for planmonth in range(scenario['months']):
                try:
                    # Calculate current month's date
                    current_year = start_year + planmonth // 12
                    current_month = start_month + planmonth % 12
                    if current_month > 12:
                        current_year += 1
                        current_month -= 12
                    
                    # Initialize annual withholding tracker for new years
                    if current_year not in annual_total_withheld:
                        annual_total_withheld[current_year] = 0.0

                    # ===== HANDLE NORMAL RETIREMENT AGE =====
                    # When the individual reaches their NRA, recalculate the benefit
                    # The recalculated amount accounts for months where benefits were withheld
                    if current_year == birth_year + config.NRA_AGE and current_month == birth_month:
                        logger.info(f"Reached normal retirement age in {current_year}-{current_month:02d}.")
                        
                        # Scan all months prior to NRA and count those where no benefit was paid
                        # (These months count as if the person deferred, resulting in a higher benefit)
                        eliminated_months = []
                        for year, months in scenario_table.items():
                            for month, details in months.items():
                                if details['paid_benefit'] == 0.0 and details['eligible_benefit'] > 0.0:
                                    # This month had earnings test reduction; it counts as deferred
                                    eliminated_months.append((year, month, details['eligible_benefit'], details['paid_benefit']))
                        
                        # Recalculate benefit as if the person started at a later age
                        # Each withheld month is treated like a month of deferral
                        effective_start_month = start_month + len(eliminated_months)
                        effective_start_year = start_year + effective_start_month // 12
                        effective_start_month = effective_start_month % 12
                        monthly_benefit = lookup_benefit(benefits, effective_start_year, effective_start_month, birth_year, birth_month)
                        logger.info(f"Effective start: {effective_start_year}-{effective_start_month:02d}, # eliminated months: {len(eliminated_months)}")
                        logger.info(f"Recalculated monthly benefit: {monthly_benefit}")
                    
                    # ===== DETERMINE EARNINGS TEST PHASE =====
                    # Different phases have different earnings test rules
                    phase = identify_phase(current_year, current_month, birth_year, birth_month)
                    
                    # Look up earnings test rules for this year and phase
                    if phase == "age_after_nra":
                        # No earnings test after NRA, so no income limit or reduction factor
                        income_limit = None
                        reduction_factor = None
                    else:
                        # Find rules for this year and phase
                        for rule in rules:
                            if rule['year'] == current_year:
                                income_limit = rule[phase]['annual_limit']
                                reduction_factor = rule[phase]['reduction_factor']
                                break

                    # ===== CALCULATE INCOME-BASED BENEFIT REDUCTION =====
                    # SSA applies earnings test on an annual basis (not monthly)
                    # The reduction is spread across all remaining months in the year
                    
                    if current_year == start_year:
                        # PRORATED FIRST YEAR: Only months from start_month through Dec count
                        # Income is prorated to full-year equivalent, and reduction is also prorated
                        prorated_annual_income = year_income_summation(income_data, current_year, start_month, 12)
                        prorated_income_limit = None if income_limit is None else income_limit * (12 - start_month + 1) / 12.0
                        excess_income = 0.0 if prorated_income_limit is None else max(0.0, prorated_annual_income - prorated_income_limit)
                        reduction_amount = 0.0 if reduction_factor is None else excess_income / reduction_factor
                    else:
                        # FULL YEARS: All 12 months' income counted against annual limit
                        annual_income = year_income_summation(income_data, current_year)
                        excess_income = 0.0 if income_limit is None else max(0.0, annual_income - income_limit)
                        reduction_amount = 0.0 if reduction_factor is None else excess_income / reduction_factor

                    # ===== APPLY MONTHLY WITHHOLDING =====
                    # The annual reduction is spread across the remaining months of the year
                    # Each month withholds some amount until the annual reduction is satisfied
                    
                    if reduction_amount - annual_total_withheld[current_year] > 0.0:
                        # Still have reduction amount to apply this month
                        month_reduction = min(monthly_benefit, (reduction_amount - annual_total_withheld[current_year]))
                        paid_benefit = monthly_benefit - month_reduction
                        annual_total_withheld[current_year] += month_reduction
                    else:
                        # Annual reduction has been satisfied, pay full benefit
                        paid_benefit = monthly_benefit

                    # ===== RECORD MONTHLY RESULTS =====
                    if current_year not in scenario_table:
                        scenario_table[current_year] = {}
                    monthly_income = income_data.get(current_year, {}).get(current_month, 0.0)
                    scenario_table[current_year][current_month] = {
                        "eligible_benefit": monthly_benefit,
                        "monthly_income": monthly_income,
                        "phase": phase,
                        "income_limit": income_limit,
                        "paid_benefit": paid_benefit
                    }
                
                except (ValueError, KeyError) as e:
                    logger.error(f"Error processing month {current_year}-{current_month:02d} for scenario '{scenario['scenario_name']}': {str(e)}")
                    raise
            
            log_scenario_complete(scenario['scenario_name'])
            
        except Exception as e:
            logger.error(f"Failed to process scenario '{scenario['scenario_name']}': {str(e)}")
            raise

    return all_scenarios_results  # Return results for potential further analysis


if __name__ == "__main__":
    try:
        all_results = main()
        try:
            reports(all_results)
            logger.info("Report generation completed successfully")
        except Exception as e:
            logger.error(f"Failed to generate reports: {str(e)}")
            raise
    except Exception as e:
        logger.error(f"Application failed: {str(e)}")
        exit(1)
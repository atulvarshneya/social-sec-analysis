# Create a simple config namespace to store file paths
# (An alternative to using a dictionary or config class)
config = type('Config', (), {})()

# File paths for data inputs
config.EARNING_LIMITS_FILE = 'data/earnings_limits.json'  # SSA earnings limits and reduction factors by year and phase
config.BENEFITS_BY_AGE_FILE = 'data/benefits_by_age.json'  # Primary Insurance Amount (PIA) by age at retirement
config.INCOME_DATA_FILE = 'data/income_data.csv'  # Individual income history (year, month, amount)
config.SCENARIO_DATA_FILE = 'data/scenario_data.json'  # Retirement scenarios to analyze (start date, duration, birthdate)
config.COMBINED_BENEFITS_FILE = "output/combined_scenario_benefits.xlsx" # Output file for combined scenario benefits analysis

# SSA Normal Retirement Age (NRA) in years. This is required to be in 'benefits_by_age.json' file, but we set a default here.
# NRA is also known as Full Retirement Age (FRA), both are used interchangeably in SSA context.
config.NRA_AGE = 67  # Normal Retirement Age in years (used for earnings test phase determination)
# SSA has a maximum retirement age for benefits calculation, which is typically 70 years.
# This is required to be in 'benefits_by_age.json' file, but we set a default here.
config.MAX_RETIREMENT_AGE = 70  # Maximum retirement age for benefits calculation (used for benefits by age)
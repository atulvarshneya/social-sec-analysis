## Disclaimer

This software is provided 'as is', without any warranty of any kind, express or implied. The author(s) will not be held liable for any damages arising from the use of this software.

# Social Security Benefits Analysis Tool

This tool helps you analyze your Social Security benefits trajectory based on your claiming age, accounting for benefit reductions due to continued earned income after enrollment. 

## How Social Security Benefits Work

Your Social Security benefit amount is determined by your lifetime contributions (Social Security taxes paid) and your age when you begin receiving benefits. This benefit amount is fixed for life, subject to annual Cost of Living Adjustments (COLA). Each year, the Social Security Administration applies a COLA factor to your benefit to account for inflation.

If you continue earning wages after claiming Social Security benefits, your benefits may be reduced based on your earnings and the applicable income limits:
- **Before Full Retirement Age (FRA)**: $1 benefit reduction for every $2 earned above the annual limit
- **Year you reach FRA**: $1 benefit reduction for every $3 earned above the limit (only for earnings before reaching FRA)
- **After reaching FRA**: No reduction regardless of earnings

When benefits are eliminated due to excess earnings during certain months, your benefit is recalculated at FRA as if you had started claiming at a later date.

## Features

This tool performs the following calculations and analyses:

1. **Benefit Lookup**: Retrieves your monthly Social Security benefit amount based on your claiming age (with interpolation if necessary)
2. **Earnings Reduction Calculation**: Computes benefit reductions based on your annual wages, applicable income limits, and benefit phase
3. **FRA Recalculation**: Recalculates your benefit at Full Retirement Age to account for months when benefits were eliminated due to excess earnings
4. **Scenario Analysis**: Generates detailed comparison across multiple scenarios
5. **Excel Report**: Creates a comprehensive `output/combined_scenario_benefits.xlsx` with:
   - Summary comparison sheet across all scenarios
   - Monthly details for each scenario (including earnings reductions and cumulative totals)
   - Annual summary for each scenario

**Note**: This tool does not currently apply COLA adjustments to benefit projections.

# Installation

This tool is written in Python. It has been tested on Python 3.11. You will need to install this version of Python if not already installed.

to install this tool -
1. download this repository in a folder,
2. cd into that folder and install dependencies by running the following command  
    `pip install -r requirements.txt`

# Setup Requirements

Before running the tool, you must prepare the following input files in the `data/` directory:

## 1. data/benefits_by_age.json

This file contains your monthly Social Security benefit amounts at different claiming ages from your Social Security Administration statement.

**Example:**
```json
{
  "description": "Monthly Social Security benefits by claiming age",
  "notes": "Replace placeholder values with amounts from your SSA statement. Include age values (years and months) from current age through age 70",
  "normal_retirement_age": 67,
  "max_retirement_age": 70,
  "benefits": [
    {"age": "64-7", "benefit": 2000.00},
    {"age": "65", "benefit": 2100.00},
    {"age": "66", "benefit": 2200.00},
    {"age": "67", "benefit": 2300.00},
    {"age": "68", "benefit": 2400.00},
    {"age": "69", "benefit": 2500.00},
    {"age": "70", "benefit": 2600.00}
  ]
}
```

## 2. data/earnings_limits.json

This file contains the annual earnings limits and reduction factors for each year from now until you reach Full Retirement Age (age 67).

**Important**: The Social Security Administration only publishes these limits through the current year. You must estimate values for future years based on historical trends.

**Example:**

```json
{
  "description": "Annual earning limits and reduction factors for Social Security earnings test. Must go from current year to year you turn 67 (FRA).",
  "notes": "Reduction factor is the divisor: $1 reduction per $2 earned = 2, $1 reduction per $3 earned = 3",
  "rules": [
    {
      "year": 2026,
      "age_before_nra": {
        "annual_limit": 24480,
        "reduction_factor": 2,
        "description": "$1 benefit reduction for every $2 in earnings above limit"
      },
      "age_nra_year": {
        "annual_limit": 65160,
        "reduction_factor": 3,
        "months_counted": "only months before reaching NRA",
        "description": "$1 benefit reduction for every $3 in earnings above limit, applies Jan 1 to month before NRA"
      }
    },
    {
      "year": 2027,
      ... please add "age_before_nra", and "age_nra_year" elements
    },
    {
      "year": 2028,
      ... please add "age_before_nra", and "age_nra_year" elements
    }
  ]
}
```

## 3. data/income_data.csv

This file contains your monthly earned income during retirement. Include entries only for months when you expect to have earnings.

**Example:**
```csv
year,month,amount
2026,1,30000.00
2026,2,30000.00
2026,3,30000.00
2026,4,30000.00
2026,5,30000.00
2026,6,30000.00
2026,7,30000.00
2026,8,30000.00
2026,9,30000.00
2026,10,30000.00
2026,11,30000.00
2026,12,30000.00
2027,1,30000.00
```

## 4. data/scenario_data.json

This file defines the scenarios you want analyzed. Each scenario specifies a benefits start date and analysis end date. You can create any number of scenarios for comparison.

**Example:**
```json
{
    "description": "Scenario data for social security benefits calculation.",
    "birthdate": "1961-06-01",
    "scenarios": [
        {
        "scenario_name": "Start 2026-05",
        "start_date": "2026-05-01",
        "end_date": "2046-06-01"
        },
        {
        "scenario_name": "Start 2026-09",
        "start_date": "2026-09-01",
        "end_date": "2046-06-01"
        }
    ]
}
```

# Running the Tool

After preparing all required input files, execute the tool with the following command:

```bash
python -m src.main
```

The tool will generate a comprehensive analysis report as `output/combined_scenario_benefits.xlsx`.

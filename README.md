## Disclaimer

This tool can have errors. It is based on my understanding of how the SoSec benefits work. Please use it with this understanding, and with caution.

# Social Security Benefits Analysis Tool

This tool helps you analyze how your benefits will pan out depending on when you start considering reductions if you have some wages after you start. 

The SoSec benefit amount is based on your contributions for the duration you worked (i.e., paid SoSec taxes), and are fixed for life depending on the age at which you enroll to start receiving benefits. Every year SSA decides a Cost of Living Adjustment (COLA) factor which is multiplied to your fixed benefit amount to compensate for the inflation etc.

If you continue to earn wages after you enroll to start SoSec benefits, then the SoSec benefits can be reduced depending on the phase (before reaching FRA, during the calendar year of reaching FRA, after FRA) and corresponding maximum income limit announced by SSA every year. Once you have reached FRA, there is no reduction to benefits.

Note, if due to wages, your SoSec benefits are eliminated for certain months, then, on the month you turn 67 (FRA), the SoSec benefit is recalculated as if you started that many months later.

This tool does the following
* looks up (and interpolates, if necessary) the benefit amount per your SSA SoSec statement per the date you enroll to start receiving SoSec benefits
* computes the reduction in the SoSec benefits based on your wages and max income limit for each year and depending on your phase
* recalculates the benefit number once you reach FRA, based on the number of onths your benefits were eliminated due to your wages
* it **DOES NOT** take into account the COLA adjustments to the SoSec benefits
* creates an MS Excel file `output/combined_scenario_benefits.xlsx` which has sheets with a summarized comparison sheet, and sheets with the information for all the scenarios

The output MS Excel file has the first sheet where all scenarios monthly calculated (with reduction) benefits, and running cumulative numbers are provided. And, for each scenario specified, it has one sheet that provides monthly details and another sheet for annual details.

# To run it, you need to prepare the following files
* **data/benefits_by_age.json** - in this file you need to provide the benefits data you get from SSA. Provided below is a sample content:
```json
{
  "description": "Monthly eligible Social Security benefits by age at which benefits are claimed",
  "notes": "Here we have some placeholder values, put your actual values from SSA statement. Include age yy-mm values from now till 70",
  "normal_retirement_age": 67,
  "max_retirement_age": 70,
  "benefits": [
    {"age": "64-7", "benefit": 2000.00},
    {"age": "65", "benefit": 2100.00},
    {"age": "66", "benefit": 2200.00},
    {"age": "67","benefit": 2300.00},
    {"age": "68", "benefit": 2400.00},
    {"age": "69", "benefit": 2500.00},
     {"age": "70", "benefit": 2600.00}
  ]
}
```
* **data/earnings_limits.json** - in this file you need to provide the annual wages limits as provided by SSA. The limits entries (`annual_limit`, and `reduction_factor`) are required for all years till you turn 67. Unfortunately, SSA does not provide these for future years, so you will need to estimate them.  Provided below is a sample content:

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
* **data/income_data.csv** - this CSV file is required to provide the monthly wages expected till you plan to earn wages during your retirement. Provide entries only for the months you expect to earn. Provided below is a sample content:
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
* **data/scenario_data.json** - this is where you sepcify all the scenarios you want evaluated for analysis. Provided below is a sample content with two scenarios specified - you can have any number of scenarios:
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

# Running the tool
Having prepared the files, run the tool with the following command:
```bash
python -m src.main
```


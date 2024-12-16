# Optimized Deployment Strategy Generator for Charge Robotics

Welcome to our repository containing the code to complement our Design Report, "Optimization and Generation of Deployment Strategies for Charge Robotics’ Solar Farm Construction Pipeline." The following files will be of interest to you:

1) **mip_strategy_generator**: This is our main code that can be used to determine an optimal deployment strategy with Mixed Integer Programming, based on a given solar site and set of resources. It's currently set up to do this for the test case provided to us, reading from the file **test_data_20k.json**.

2) **run_factories**: The Sequential Objective Function that can produce a project completion time and cost estimate for a given deployment strategy. We've included a sample of what format the deployment strategy should take. It's also called in **mip_strategy_generator** to estimate the time and cost for the optimal strategy generated.

3) **run_factory**: A simplified version of the Sequential Objective Function (single factory, no movement) used in **mip_strategy_generator**.

4) **charge_existing_test_case**: Calls **run_factories** on the representative strategy based on Charge Robotics' existing process.

5) **animation**: Code for producing a .gif file animating a given strategy, as seen in **factory_animation.gif**.

6) **multiple_plots_scenarios** / **plot_factory_scenarios.py**: Code for investigating the time-cost tradeoff for different resource availabilities. Plots generated can be found in _cost-time-tradeoff-plots_.

7) **esc-470-design-report**: A PDF copy of our Design Report.

The various archival folders document our design work en route to our final design, in case it is of interest. Please let us know if you have any questions!

Thank you,

ESC470 Team 2

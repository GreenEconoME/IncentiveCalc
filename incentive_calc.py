# Import dependencies
import streamlit as st
import pandas as pd

# Import helper functions
from utils.gen_export import gen_export
from utils.graphs import graph_project_costs, roi_graph

# Set the page config
st.set_page_config(layout = 'wide')

# Instantiate a list to hold the incentive dictionaries as they are created
incentive_dicts = []

# Set a title for the page
st.markdown("<h1 style = 'text-align: center; color: green;'>Green Econome</h1>", unsafe_allow_html = True)
st.markdown("<h2 style = 'text-align: center; color: black;'>Tax Opportunity Calculator</h2>", unsafe_allow_html = True)

# Add a sidebar to hold the building input information
st.sidebar.markdown('<h1>Building and Project Information</h1>', unsafe_allow_html = True)

# Add a number input for the building gfa
building_gfa = st.sidebar.number_input('Building Gross Floor Area:', 
                                       value = 218347)

# Add an input box for tax rate
tax_rate = st.sidebar.number_input('Tax Rate:', value = 30, min_value = 0, max_value = 100) / 100

# Add a slide bar to gather the efficency gain over baseline
efficiency_gain = st.sidebar.slider('% Efficiency Gain Over Baseline:', 
                                    min_value = 25, 
                                    max_value = 50, 
                                    step = 5)

# Add a checkbox for prevailing wage
prev_wage = st.sidebar.checkbox('Prevailing Wage?', value = True)
# Add a note to select the projects that will be included
st.sidebar.markdown('<h2>Projects to Include:</h2>', unsafe_allow_html = True)

# Add a checkbox to add the individual projects
solar_project = st.sidebar.checkbox('Solar Project?', value = True)
# If there is solar project, gather the project cost and estimated annual savings
if solar_project:
    sol_total_proj_cost = st.sidebar.number_input('Solar Project Cost:', 
                                                  value = 190800)
    sol_ann_savings = st.sidebar.number_input('Solar Annual Savings:', 
                                              value = 15000)
    sol_decay_rate = st.sidebar.number_input('Solar Performance Decay Rate %', 
                                             value = 2)
    
    # Create a dictionary to hold the solar incentives
    solar_incentives = {'Project' : 'Solar',
                        'Project Cost' : sol_total_proj_cost, 
                        'MACRS Bonus Depreciation*' : -sol_total_proj_cost * .25 * tax_rate, 
                        'State (CA) 10 Year Depreciation*': -sol_total_proj_cost * .08 * tax_rate, 
                        'ITC Tax Credit' : -sol_total_proj_cost * tax_rate, 
                        'Energy Community Bonus-Tax Credit': -sol_total_proj_cost *.1,
                        'Utility Incentive' : 0}
    incentive_dicts.append(solar_incentives)
    
    
battery_project = st.sidebar.checkbox('Battery Storage?', value = True)
# If there is battery project, gather the project cost and estimated annual savings
if battery_project:
    bat_total_proj_cost = st.sidebar.number_input('Battery Project Cost:', 
                                                  value = 284843)
    bat_ann_savings = st.sidebar.number_input('Battery Storage Annual Savings:', 
                                              value = 20000)
    bat_decay_rate = st.sidebar.number_input('Battery Performance Decay Rate %', 
                                             value = 2)
    
    # Create a dictionary to hold the battery incentives
    battery_incentives = {'Project' : 'Battery Storage',
                        'Project Cost' : bat_total_proj_cost, 
                        'MACRS Bonus Depreciation*' : -bat_total_proj_cost * .25 * tax_rate, 
                        'State (CA) 10 Year Depreciation*': -bat_total_proj_cost * .08 * tax_rate, 
                        'ITC Tax Credit' : -bat_total_proj_cost * tax_rate, 
                        'Energy Community Bonus-Tax Credit': -bat_total_proj_cost *.1,
                        'Utility Incentive' : -bat_total_proj_cost * .25}
    incentive_dicts.append(battery_incentives)
    

# Instantiate a counter for total tax credits
tot_tax_credits = 0
# Add rows of data explaining total cost, savings, cost after savings
if solar_project or battery_project:
    # Create a dataframe from the incentive dictionaries
    incentive_df = pd.DataFrame(incentive_dicts)
    incentive_df.set_index('Project', inplace = True)
    incentive_df['Cost After Incentives'] = incentive_df.sum(axis = 1)


    # Create a dataframe for the metadata
    if prev_wage:
        ded_179_var = efficiency_gain / 10
    else:
        ded_179_var = efficiency_gain / 50
    # Generate the metadata df
    metadata = {'Building GFA': building_gfa, 
                'Tax Rate' : tax_rate, 
                'Efficiency Gain Over Baseline (%)' : efficiency_gain, 
                'Prevailing Wage' : prev_wage, 
                '179D Deduction per sqft ($)' : ded_179_var, 
                'Total 179D Deduction ($)' : ded_179_var * building_gfa}
    metadata_df = pd.DataFrame([metadata])
    metadata_df.index = ['Values']

    # Create a button to generate the export
    st.sidebar.write('Click to Export Incentive Data')
    st.sidebar.download_button(label = 'Export Data', 
                            data = gen_export(metadata_df, incentive_df), 
                            file_name = 'Incentive Calculator Data.xlsx')

    # Add the row of info for the solar project
    if solar_project:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Project', 'Solar')
        col2.metric('Total project cost', '${:,.0f}'.format(incentive_df.loc['Solar', 'Project Cost']))
        col3.metric('Total Tax Credit', '${:,.0f}'.format(incentive_df.loc['Solar', 'Project Cost'] - incentive_df.loc['Solar', 'Cost After Incentives']))
        col4.metric('Cost After Tax Credit', '${:,.0f}'.format(incentive_df.loc['Solar', 'Cost After Incentives']))
        # Increase the total incentives
        tot_tax_credits += (incentive_df.loc['Solar', 'Project Cost'] - incentive_df.loc['Solar', 'Cost After Incentives'])
    # Add the row of info for the battery project
    if battery_project:
        col1, col2, col3, col4 = st.columns(4)
        col1.metric('Project', 'Battery Storage')
        col2.metric('Total project cost', '${:,.0f}'.format(incentive_df.loc['Battery Storage', 'Project Cost']))
        col3.metric('Total Tax Credit', '${:,.0f}'.format(incentive_df.loc['Battery Storage', 'Project Cost'] - incentive_df.loc['Battery Storage', 'Cost After Incentives']))
        col4.metric('Cost After Tax Credit', '${:,.0f}'.format(incentive_df.loc['Battery Storage', 'Cost After Incentives']))
        # Increase the total incentives
        tot_tax_credits += (incentive_df.loc['Battery Storage', 'Project Cost'] - incentive_df.loc['Battery Storage', 'Cost After Incentives'])
    # Add the row of info for the Inflation Reductino Act (IRA) Section 179D
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Building GFA', '{:,.0f}'.format(building_gfa))
    if prev_wage:
        col2.metric('179D Deduction per Square Foot', '${:,.2f}'.format(efficiency_gain / 10))
        col3.metric('Total 179D Deduction', '${:,.0f}'.format(building_gfa * efficiency_gain / 10))
        col4.metric('179D Effective Savings', '${:,.0f}'.format(building_gfa * efficiency_gain / 10 * tax_rate))
        # Increase the total incentives
        tot_tax_credits += (building_gfa * efficiency_gain / 10 * tax_rate)
    else:
        col2.metric('179D Deduction per Square Foot', '${:,.2f}'.format(efficiency_gain / 50))
        col3.metric('Total 179D Deduction', '${:,.0f}'.format(building_gfa * efficiency_gain / 50))
        col4.metric('179D Effective Savings', '${:,.0f}'.format(building_gfa * efficiency_gain / 50 * tax_rate))
        # Increase the total incentives
        tot_tax_credits += (building_gfa * efficiency_gain / 50 * tax_rate)

    # Add the line for the total incentives
    st.markdown(f"<h3 style = 'text-align: center; color: black;'>Total Effective Savings: {'${:,.0f}'.format(tot_tax_credits)}</h3>", 
                unsafe_allow_html = True)

    # Plot the project cost breakdown graph
    st.plotly_chart(graph_project_costs(incentive_df), use_container_width = True)

    # Plot the graphs for the selected projects
    if solar_project:
        st.plotly_chart(roi_graph(incentive_df.loc['Solar', 'Cost After Incentives'], 
                                  sol_ann_savings, 
                                  'Solar Savings', 
                                  decay_rate = sol_decay_rate / 100), 
                                  use_container_width = True)
    if battery_project:
        st.plotly_chart(roi_graph(incentive_df.loc['Battery Storage', 'Cost After Incentives'], 
                                  bat_ann_savings, 
                                  'Battery Storage Savings', 
                                  decay_rate = bat_decay_rate / 100), 
                                  use_container_width = True)

else:
    st.markdown("<h2 style = 'text-align: center; color: black;'>Select a project to include to calculate tax opportunities.</h2>", 
                unsafe_allow_html = True)
    # Add the row of info for the Inflation Reductino Act (IRA) Section 179D
    col1, col2, col3, col4 = st.columns(4)
    col1.metric('Building GFA', '{:,.0f}'.format(building_gfa))
    if prev_wage:
        col2.metric('179D Deduction per Square Foot', '${:,.2f}'.format(efficiency_gain / 10))
        col3.metric('Total 179D Deduction', '${:,.0f}'.format(building_gfa * efficiency_gain / 10))
        col4.metric('179D Effective Savings', '${:,.0f}'.format(building_gfa * efficiency_gain / 10 * tax_rate))
        # Increase the total incentives
        tot_tax_credits += (building_gfa * efficiency_gain / 10 * tax_rate)
    else:
        col2.metric('179D Deduction per Square Foot', '${:,.2f}'.format(efficiency_gain / 50))
        col3.metric('Total 179D Deduction', '${:,.0f}'.format(building_gfa * efficiency_gain / 50))
        col4.metric('179D Effective Savings', '${:,.0f}'.format(building_gfa * efficiency_gain / 50 * tax_rate))
        # Increase the total incentives
        tot_tax_credits += (building_gfa * efficiency_gain / 50 * tax_rate)
    # Add the line for the total incentives
    st.markdown(f"<h3 style = 'text-align: center; color: black;'>Total Effective Savings: {'${:,.0f}'.format(tot_tax_credits)}</h3>", 
                unsafe_allow_html = True)


with st.expander('Click for information about the incentives.'):
    st.markdown("""
                Information links on individual incentives:
                * [Inflation Reduction Act](https://www.irs.gov/credits-and-deductions-under-the-inflation-reduction-act-of-2022)
                * MACRS Bonus Depreciation
                * State (CA) 10 Year Depreciation*
                * ITC Tax Credit
                * Energy Community Bonus-Tax Credit
                * Utility Incentive (SGIP)
                * 179D Deduction
                """)

# TODO
# Format the excel export

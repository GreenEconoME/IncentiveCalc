# Import dependencies
import numpy as np
import plotly.graph_objects as go
import pandas as pd
from scipy.optimize import brentq

# Define a function to calculate cumulative savings with decay over a given number of years
def cumulative_savings_with_decay(years, annual_savings, decay_rate):
    cumulative_savings = 0
    current_savings = annual_savings
    for year in range(1, int(years) + 1):
        cumulative_savings += current_savings
        current_savings *= (1 - decay_rate)
    # Add the partial year contribution if years is not an integer
    if years % 1 > 0:
        cumulative_savings += current_savings * (years % 1)
    return cumulative_savings

# Define a function to find the exact breakeven year
def find_breakeven_year(total_cost, annual_savings, decay_rate):
    return brentq(lambda years: cumulative_savings_with_decay(years, annual_savings, decay_rate) - total_cost, 0, 100)

# Define a function that will graph the cost columns
def graph_project_costs(df):
    fig = go.Figure()

    for col in df:
        if col != 'Project Cost':
            fig.add_trace(go.Bar(x = df.index, 
                                    y = df[col], 
                                    name = col, 
                                    meta = col,
                                    customdata = np.stack((df[col], df['Project Cost'], df[col] / df['Project Cost'] * 100), axis = -1),
                                    hovertemplate = '<br>'.join(['%{meta}', 
                                                                 'Total Project Cost: %{customdata[1]:$,.0f}', 
                                                                 'Amount: %{y:$,.0f}', 
                                                                 '% Of Total: %{customdata[2]:.1f}%'
                                                                 '<extra></extra>'])))
            
    fig.update_layout(barmode = 'relative',
                        title = 'Project Cost Breakdown',
                        yaxis_title = 'Cost ($)')
                
    return fig

# Define a function that will create a ROI graph
def roi_graph(total_cost, annual_savings, title, decay_rate):
    # Get the number of years that it would take to get a full return
    num_years = int(max(10, total_cost // annual_savings + 6))

    # Create a dataframe that reflects the annual savings
    years = list(range(1, num_years + 1))

    cumulative_savings = []
    net_profit = []
    current_savings = annual_savings
    for year in years:
        if year == 1:
            cumulative_savings.append(current_savings)
        else:
            current_savings *= (1 - decay_rate)
            cumulative_savings.append(cumulative_savings[-1] + current_savings)
        net_profit.append(cumulative_savings[-1] - total_cost)

    data = {'Year' : years, 
            'Cumulative Savings' : cumulative_savings, 
            'Net Profit' : net_profit}
    df = pd.DataFrame(data)

    fig = go.Figure()

    fig.add_trace(go.Scatter(x = df['Year'], 
                             y = df['Cumulative Savings'],
                             mode = 'lines+markers', 
                             name = 'Cumulative Savings', 
                             hovertemplate = '<br>'.join(['Cumulative Savings: $%{y:,.0f}', 
                                                          '<extra></extra>'])))
    
    fig.add_trace(go.Scatter(x = df['Year'], 
                             y = df['Net Profit'],
                             mode = 'lines+markers', 
                             name = 'Net Profit', 
                             hovertemplate = '<br>'.join(['Net Profit: $%{y:,.0f}', 
                                                          '<extra></extra>'])))
    
    fig.add_vline(x = find_breakeven_year(total_cost, annual_savings, decay_rate), 
                #   x = total_cost / annual_savings, 
                  line_dash = "dash", 
                  line_color = "red", 
                  annotation_text = f'Break-even {find_breakeven_year(total_cost, annual_savings, decay_rate):.1f} Years')
    
    fig.update_layout(hovermode = 'x unified', 
                      title = title, 
                      xaxis_title = 'Years After Completion',
                      yaxis_title = 'Savings ($)')
    
    return fig
# Import required libraries
import pandas as pd
import dash
import dash_html_components as html
import dash_core_components as dcc
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = dash.Dash(__name__)


options_sites = [{'label': 'All Sites', 'value': 'ALL'}]
for index, element in enumerate(spacex_df['Launch Site'].unique()):
    options_sites.append({'label':element, 'value':'site'+str(index)})

def get_label_for_value(value):
    for option in options_sites:
        if option['value'] == value:
            return option['label']
    return None

max_payload = max(spacex_df['Payload Mass (kg)'])
min_payload = min(spacex_df['Payload Mass (kg)'])

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                dcc.Dropdown(
                                    id='site-dropdown', 
                                    options=options_sites,
                                    value='ALL',
                                    placeholder="Select a Launch Site",
                                    searchable=True
                                ),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart')),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                dcc.RangeSlider(id='payload-slider',
                                    min=0,
                                    max=10000,
                                    step=1000,
                                    marks={0: '0', 2500:'2500', 5000:'5000', 7500:'7500'},
                                    value=[min_payload, max_payload]
                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart')),
                                ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'))
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        data = spacex_df
        fig = px.pie(data, values='class', names='Launch Site', title='Proportion of launch success per site')
        return fig
    else:
        site_name = get_label_for_value(entered_site)
        data = spacex_df[spacex_df['Launch Site'] == site_name]
        value_counts = data['class'].value_counts()
        value_counts_df = value_counts.reset_index()
        value_counts_df.columns = ['class', 'counts']
        fig = px.pie(value_counts_df, values='counts', names='class', title='Proportion of launch success and failure for the selected site')
        return fig

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              Input(component_id='site-dropdown', component_property='value'), 
              Input(component_id='payload-slider', component_property='value'))
def get_scatter_chart(entered_site, entered_range):
    data = spacex_df[(spacex_df['Payload Mass (kg)'] > entered_range[0]) & (spacex_df['Payload Mass (kg)'] < entered_range[1])]
    if entered_site == 'ALL':
        fig = px.scatter(data, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Launch success and failure based on payload mass')
        return fig
    else:
        data = data[data['Launch Site'] == get_label_for_value(entered_site)]
        fig = px.scatter(data, x='Payload Mass (kg)', y='class', color='Booster Version Category', title='Launch success and failure based on payload mass')
        return fig
    

# Run the app
if __name__ == '__main__':
    app.run_server()

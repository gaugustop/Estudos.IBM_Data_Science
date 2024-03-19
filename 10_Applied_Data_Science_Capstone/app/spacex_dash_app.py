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

launch_sites = ['ALL'] + list(spacex_df['Launch Site'].unique())

df_launch_pie = spacex_df[spacex_df['class'] == 1]['Launch Site'].value_counts(ascending=True).reset_index()
df_launch_pie.columns = ['Launch Site', 'Count']

payload_min = spacex_df['Payload Mass (kg)'].min()
payload_max = spacex_df['Payload Mass (kg)'].max()
# Create a dash application
app = dash.Dash(__name__)

# Create an app layout
app.layout = html.Div(children=[html.H1('SpaceX Launch Records Dashboard',
                                        style={'textAlign': 'center', 'color': '#503D36',
                                               'font-size': 40}),
                                # TASK 1: Add a dropdown list to enable Launch Site selection
                                # The default select value is for ALL sites
                                # dcc.Dropdown(id='site-dropdown',...)
                                dcc.Dropdown(id = 'dropdown-site',
                                             options = launch_sites,
                                             value = 'ALL',
                                             placeholder = 'ALL'),
                                html.Br(),

                                # TASK 2: Add a pie chart to show the total successful launches count for all sites
                                # If a specific launch site was selected, show the Success vs. Failed counts for the site
                                html.Div(dcc.Graph(id='success-pie-chart',
                                                   figure = px.pie(df_launch_pie,
                                                            names = 'Launch Site',
                                                            values = 'Count',
                                                            title = 'Successful Launch Sites Count '))),
                                html.Br(),

                                html.P("Payload range (Kg):"),
                                # TASK 3: Add a slider to select payload range
                                #dcc.RangeSlider(id='payload-slider',...)
                                dcc.RangeSlider(id = 'payload-slider',
                                                min = payload_min,
                                                max = payload_max,
                                                step = None,
                                                marks = {i:f'{i} kg' for i in spacex_df['Payload Mass (kg)'].unique()},
                                                value = [payload_min,payload_max],
                                                ),

                                # TASK 4: Add a scatter chart to show the correlation between payload and launch success
                                html.Div(dcc.Graph(id='success-payload-scatter-chart',
                                                   figure = px.scatter(spacex_df,
                                                                       x = 'Payload Mass (kg)',
                                                                       y = 'class',
                                                                       color = 'class')),)
                                    ])

# TASK 2:
# Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(Output(component_id = 'success-pie-chart', component_property = 'figure'),
              Input(component_id = 'dropdown-site', component_property = 'value'))
def update_pie_launch_sites(launch_site):
    if launch_site == 'ALL':
        figure = px.pie(df_launch_pie,
                        names = 'Launch Site',
                        values = 'Count',
                        title = 'Successful Launch Sites Count')
    else:
        df_aux = spacex_df[spacex_df['Launch Site'] == launch_site]['class'].value_counts().reset_index()
        df_aux.columns = ['Launch Site', 'Count']
        df_aux['Outcome'] = ['Fail','Success']
        figure = px.pie(df_aux,
                        names = 'Outcome',
                        values = 'Count',
                        title = f'Outcome for launch site {launch_site}')
    return figure

# TASK 4:
# Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(Output(component_id = 'success-payload-scatter-chart', component_property='figure'),
             [Input(component_id = 'dropdown-site', component_property = 'value'),
              Input(component_id = 'payload-slider', component_property = 'value')])
def update_scatter_plot(launch_site, payload_range):
    cond1 = spacex_df['Payload Mass (kg)'] >= float(payload_range[0])
    cond2 = spacex_df['Payload Mass (kg)'] <= float(payload_range[1])
    df_aux = spacex_df[cond1 & cond2]
    if launch_site != 'ALL':
        df_aux = df_aux[df_aux['Launch Site'] == launch_site]
    figure = px.scatter(df_aux,
                        x = 'Payload Mass (kg)',
                        y = 'class',
                        color = 'class',
                        title = f'Launch success vs Payload. Launch Site: {launch_site}')
    return figure

# Run the app
if __name__ == '__main__':
    app.run_server()

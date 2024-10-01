import streamlit as st
import pandas as pd
import plotly.express as px
from ESLData import esl_data  # Assuming the ESL data processing function is in ESLData.py

# Function to process the ESL data
def process_esl_data():
    # Parse the ESL files and convert them to a DataFrame
    data = esl_data()
    df = pd.DataFrame(data)
    # Convert 'TimePeriod' to datetime for easier resampling
    df['TimePeriod'] = pd.to_datetime(df['TimePeriod'], format='%Y-%m')
    return df

# Streamlit app
def main():
    st.title('Voltaflow Energie Visualizer')

    # Parse the ESL data
    df = process_esl_data()

    if not df.empty:
        # User selection for time granularity
        time_granularity = st.selectbox('Choose a time granularity:', ('Monthly', 'Yearly', 'Daily'))

        # Resample data based on the selected granularity
        if time_granularity == 'Yearly':
            # Group the data by year and sum the values
            df_resampled = df.resample('Y', on='TimePeriod').sum().reset_index()
            x_axis_format = "%Y"  # Show only the year
            dtick = "M12"  # Ticks for every year
        if time_granularity == 'Monthly':
            # Monthly data (no resampling needed)
            df_resampled = df
            x_axis_format = "%b %Y"  # Show month and year
            dtick = "M1"  # Ticks for every month

        # Display the data in a table
        st.subheader(f'Energy Data (Bezug and Einspeisung) - {time_granularity}')
        st.dataframe(df_resampled)

        # Plotting with Plotly for better control of x-axis labels and size
        fig = px.line(df_resampled, x='TimePeriod', y=['Bezug', 'Einspeisung'],
                      labels={'value': 'Energy (kWh)', 'TimePeriod': 'Date'},
                      title=f'Energy Consumption and Feed-in Over Time ({time_granularity})')

        # Customize x-axis to show correct format based on time granularity
        fig.update_layout(
            autosize=True,  # Make the plot autosize to use all available space
            margin=dict(l=40, r=40, b=100, t=80),  # Adjust margins
            xaxis=dict(
                tickmode='linear',
                dtick=dtick,  # Use ticks based on time granularity
                tickformat=x_axis_format,  # Format based on time granularity
                tickangle=-45,  # Rotate x-axis labels for better readability
                title_font=dict(size=14),  # Increase font size of the x-axis title
                tickfont=dict(size=12)  # Increase font size of the x-axis labels
            ),
            yaxis=dict(
                title_font=dict(size=14),  # Adjust font size for y-axis
                tickfont=dict(size=12)
            )
        )

        # Display the plot
        st.plotly_chart(fig, use_container_width=True)  # Full width of the container

    else:
        st.warning('No data available to display.')

if __name__ == '__main__':
    main()

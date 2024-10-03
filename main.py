import streamlit as st
import pandas as pd
import plotly.express as px
from ESLData import esl_data
import psutil
import os
import time


# for Streamlit Theming
st.set_page_config(layout="wide")
CURRENT_THEME = "light"




# Function to process the ESL data
def process_esl_data():
    # Parse the ESL files and convert them to two DataFrames: cumulative and monthly
    cumulative_data, monthly_data = esl_data()

    # Convert both lists to DataFrames
    df_cumulative = pd.DataFrame(cumulative_data)
    df_monthly = pd.DataFrame(monthly_data)
    #exporting esl data
    df_cumulative.to_csv("esl_export/cumulative_data.csv", index=False)
    df_cumulative.to_json("esl_export/cumulative_data.json", orient="records")
    df_monthly.to_csv("esl_export/monthly_data.csv", index=False)
    df_monthly.to_json("esl_export/monthly_data.json", orient="records")
    # Convert 'TimePeriod' to datetime for easier resampling
    df_cumulative['TimePeriod'] = pd.to_datetime(df_cumulative['TimePeriod'], format='%Y-%m')
    df_monthly['TimePeriod'] = pd.to_datetime(df_monthly['TimePeriod'], format='%Y-%m')

    return df_cumulative, df_monthly


# Streamlit app
def main():
    st.title('Voltaflow Energie Visualizer')

    # Parse the ESL data
    df_cumulative, df_monthly = process_esl_data()

    if not df_cumulative.empty and not df_monthly.empty:
        # User selection for time granularity
        time_granularity = st.selectbox('Wählen Sie eine Zeitspanne aus', ('Monatlich', 'Jährlich'))

        # Resample data based on user selection (yearly or monthly)
        if time_granularity == 'Jährlich':
            # Resample cumulative data to yearly
            df_cumulative_resampled = df_cumulative.resample('Y', on='TimePeriod').sum()
            df_cumulative_resampled['TimePeriod'] = df_cumulative_resampled.index

            # Resample monthly data to yearly
            df_monthly_resampled = df_monthly.resample('Y', on='TimePeriod').sum()
            df_monthly_resampled['TimePeriod'] = df_monthly_resampled.index

            # Set title for yearly
            cumulative_title = 'Kumulativer jährlicher Energiebezug und Einspeisung'
            monthly_title = 'Jährlicher Energiebezug und Einspeisung'
            xaxis_format = "%Y"  # Yearly format
        if time_granularity == 'Monatlich':
            # No resampling needed for monthly data
            df_cumulative_resampled = df_cumulative
            df_monthly_resampled = df_monthly

            # Set title for monthly
            cumulative_title = 'Kumulativer monatlicher Energiebezug und Einspeisung'
            monthly_title = 'Monatlicher Energiebezug und Einspeisung'
            xaxis_format = "%b %Y"  # Monthly format

        # Resample data based on the selected granularity
        if time_granularity == 'Jährlich':
            # Resample cumulative data to yearly, taking the last value of each year
            df_cumulative_resampled = df_cumulative.resample('YE', on='TimePeriod').last().reset_index()
            # Adjust 'TimePeriod' to the beginning of the year to correct the x-axis placement
            df_cumulative_resampled['TimePeriod'] = df_cumulative_resampled['TimePeriod'].apply(
                lambda x: x.replace(month=1, day=1))
            # Resample monthly data to yearly, summing the monthly values for the year
            df_monthly_resampled = df_monthly.resample('YE', on='TimePeriod').sum().reset_index()
            df_monthly_resampled['TimePeriod'] = df_monthly_resampled['TimePeriod'].apply(
                lambda x: x.replace(month=1, day=1))
            x_axis_format = "%YE"  # Show only the year
            dtick = "M12"  # Ticks for every year
        if time_granularity == 'Monatlich':
            # Use original data for monthly granularity
            df_cumulative_resampled = df_cumulative
            df_monthly_resampled = df_monthly
            x_axis_format = "%b %Y"  # Show month and year
            dtick = "M1"  # Ticks for every month

        # Visualization for cumulative data
        st.subheader('Cumulative Energy Data (Bezug and Einspeisung)')
        st.dataframe(df_cumulative_resampled)

        fig_cumulative = px.line(df_cumulative_resampled, x='TimePeriod', y=['Bezug', 'Einspeisung'],
                                 labels={'value': 'Energie (kWh)', 'TimePeriod': 'Zeitspanne'},
                                 title=cumulative_title,
                                 color_discrete_sequence=["#ff0000", "#00ff00"]
                                 )

        # Customize x-axis for cumulative data
        fig_cumulative.update_layout(
            autosize=False,
            margin=dict(l=40, r=40, b=100, t=80),
            xaxis=dict(
                tickmode='linear',
                dtick="M12" if time_granularity == 'Jährlich' else "M1",  # Adjust tick based on granularity
                tickformat=xaxis_format,  # Dynamic format for month/year
                tickangle=-45,
                title_font=dict(size=14),
                tickfont=dict(size=12),

            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12)
            )
        )

        # Display the cumulative plot
        st.plotly_chart(fig_cumulative, use_container_width=False)

        # Visualization for monthly data using a bar chart (beam diagram)
        st.subheader('Monatliche/Jährliche Energiestatistik (Bezug and Einspeisung)')
        st.dataframe(df_monthly_resampled)
        # Bar chart for monthly energy consumption
        fig_monthly = px.bar(df_monthly_resampled, x='TimePeriod', y=['Bezug', 'Einspeisung'],
                             barmode='group',
                             labels={'value': 'Energie (kWh)', 'TimePeriod': 'Monat'},
                             title=monthly_title,
                             color_discrete_sequence=["#ff0000", "#00ff00"]
                             )

        # Customize x-axis for monthly data
        fig_monthly.update_layout(
            autosize=False,
            width=1500,
            height=400,
            margin=dict(l=40, r=40, b=100, t=80),
            xaxis=dict(
                tickmode='linear',
                dtick="M12" if time_granularity == 'Jährlich' else "M1",  # Adjust tick based on granularity
                tickformat=xaxis_format,  # Dynamic format for month/year
                tickangle=-45,
                title_font=dict(size=14),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12)
            ),
            overwrite=True
        )

        # Display the monthly bar chart
        st.plotly_chart(fig_monthly, use_container_width=False)

        # Builtin Healthcheck features

        # Get the current process ID
        pid = os.getpid()

        # Use psutil to access process information
        process = psutil.Process(pid)

        # Function to get RAM and CPU usage
        def print_usage():
            # Get the memory usage in MB
            memory_usage = process.memory_info().rss / (1024 * 1024)
            # Get the CPU usage in percentage
            cpu_usage = process.cpu_percent(interval=1)

            print(f"Memory Usage: {memory_usage:.2f} MB")
            print(f"CPU Usage: {cpu_usage:.2f}%")

        # Simulating a long-running task
        while True:
            # Do some computation here
            time.sleep(30)  # Simulating a delay
            print_usage()


    else:
        st.warning('Keine Daten zum Visualisieren')


if __name__ == '__main__':
    main()

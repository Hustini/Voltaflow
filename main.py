import streamlit as st
import pandas as pd
import plotly.express as px
from ESLData import esl_data


# Function to process the ESL data
def process_esl_data():
    # Parse the ESL files and convert them to two DataFrames: cumulative and monthly
    cumulative_data, monthly_data = esl_data()

    # Convert both lists to DataFrames
    df_cumulative = pd.DataFrame(cumulative_data)
    df_monthly = pd.DataFrame(monthly_data)

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
        time_granularity = st.selectbox('Wählen sie eine Zeitspanne aus', ('Monatlich', 'Jährlich'))

        # Resample data based on the selected granularity
        if time_granularity == 'Jährlich':
            # Resample cumulative data to yearly, taking the last value of each year
            df_cumulative_resampled = df_cumulative.resample('Y', on='TimePeriod').last().reset_index()
            # Adjust 'TimePeriod' to the beginning of the year to correct the x-axis placement
            df_cumulative_resampled['TimePeriod'] = df_cumulative_resampled['TimePeriod'].apply(lambda x: x.replace(month=1, day=1))
            # Resample monthly data to yearly, summing the monthly values for the year
            df_monthly_resampled = df_monthly.resample('Y', on='TimePeriod').sum().reset_index()
            df_monthly_resampled['TimePeriod'] = df_monthly_resampled['TimePeriod'].apply(lambda x: x.replace(month=1, day=1))

            x_axis_format = "%Y"  # Show only the year
            dtick = "M12"  # Ticks for every year
        if time_granularity == 'Monatlich':
            # Use original data for monthly granularity
            df_cumulative_resampled = df_cumulative
            df_monthly_resampled = df_monthly
            x_axis_format = "%b %Y"  # Show month and year
            dtick = "M1"  # Ticks for every month

        # ---- Cumulative Data Visualization ----
        st.subheader(f'Kumulative Energie Daten (Bezug and Einspeisung) - {time_granularity}')
        st.dataframe(df_cumulative_resampled)
        fig_cumulative = px.line(df_cumulative_resampled, x='TimePeriod', y=['Bezug', 'Einspeisung'],
                                 labels={'value': 'Energie (kWh)', 'TimePeriod': 'Zeitspanne'},
                                 title=f'Kumulativer Energiebezug und Einspeisung')

        # Customize x-axis for cumulative data
        fig_cumulative.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, b=100, t=80),
            xaxis=dict(
                tickmode='linear',
                dtick=dtick,  # Use appropriate ticks based on time granularity
                tickformat=x_axis_format,  # Format based on time granularity
                tickangle=-45,
                title_font=dict(size=14),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12)
            )
        )

        # Display the cumulative plot
        st.plotly_chart(fig_cumulative, use_container_width=True)

        # ---- Monthly Data Visualization (Bar Chart) ----
        st.subheader(f'Monatliche Energiestatistik (Bezug and Einspeisung) - {time_granularity}')
        st.dataframe(df_monthly_resampled)

        # Bar chart for monthly or yearly energy consumption
        fig_monthly = px.bar(df_monthly_resampled, x='TimePeriod', y=['Bezug', 'Einspeisung'],
                             barmode='group',
                             labels={'value': 'Energie (kWh)', 'TimePeriod': 'Monat'},
                             title='Monatlicher Energiebezug und Einspeisung')

        # Customize x-axis for monthly data
        fig_monthly.update_layout(
            autosize=True,
            margin=dict(l=40, r=40, b=100, t=80),
            xaxis=dict(
                tickmode='linear',
                dtick=dtick,  # Use appropriate ticks based on time granularity
                tickformat=x_axis_format,  # Format based on time granularity
                tickangle=-45,
                title_font=dict(size=14),
                tickfont=dict(size=12)
            ),
            yaxis=dict(
                title_font=dict(size=14),
                tickfont=dict(size=12)
            )
        )

        # Display the monthly bar chart
        st.plotly_chart(fig_monthly, use_container_width=True)

    else:
        st.warning('Keine Daten zum Visualisieren')


if __name__ == '__main__':
    main()

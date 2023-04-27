import os
import altair as alt
import pandas as pd
import json

PERCENTILE_NUM = 5
pc_cores = {1: 6, 2: 16}


def construct_df():
    realizations = []
    percentiles = []
    percentile_vals = []
    num_clients = []
    client_types = []
    for client in CLIENT_DIRS:
        realization_dirs = next(os.walk(ROOT_DIR + '/' + client))[1]
        for realization in realization_dirs:
            json_files = list(filter(lambda x: 'json' in x, next(os.walk(ROOT_DIR + '/' + client + '/' + realization))[2]))
            for res_file in json_files:
                with open(ROOT_DIR + '/' + client + '/' + realization + '/' + res_file, 'r') as rf:
                    realizations.extend([realization] * PERCENTILE_NUM)
                    client_types.extend([client] * PERCENTILE_NUM)
                    data = json.load(rf)
                    num_clients.extend([data['NumThreads']] * PERCENTILE_NUM)

                    for percentile in data['DurationHistogram']['Percentiles']:
                        percentiles.append(float(percentile['Percentile']))
                        percentile_vals.append(float(percentile['Value'] * 1000))
    return pd.DataFrame({'Realizations': realizations,
                         'Percentiles': percentiles,
                         'Percentile_vals': percentile_vals,
                         'Client': client_types,
                         'Num_clients': num_clients}).groupby(["Realizations", "Percentiles", "Num_clients"]).sum(True).reset_index()


def one_percentile_plot(df: pd.DataFrame, percentile: float):

    lim = 22 if percentile == 75 else 400
    df["Percentile_vals"] = df["Percentile_vals"].div(3)
    df["Num_clients"] = df["Num_clients"].mul(3)
    df2 = df[df['Percentiles'] == percentile]
    chart_lin = alt.Chart(df2).mark_line(point=alt.OverlayMarkDef()).encode(
        x=alt.X('Num_clients:Q', title="Simultaneous connected clients number"),
        y=alt.Y('Percentile_vals:Q', axis=alt.Axis(title=f'Latency for {percentile} percentile, ms'), scale=alt.Scale(domain=[0, lim])),
        color=alt.Color('Realizations:N', title="Server Implementation", legend=None)
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    return chart_lin


def fix_fonts(chart):
    return chart.configure_title(
        fontSize=20,
        subtitleFontSize=16
    ).configure_axis(
        labelFontSize=20,
        titleFontSize=20
    ).configure_header(
        titleFontSize=16,
        labelFontSize=16
    )


for i in [1, 2]:
    for j in [32, 64]:
        pc = i
        payload = j
        ROOT_DIR = f"newdata/pc{i}clients/{j}bytes"
        CLIENT_DIRS = next(os.walk(ROOT_DIR))[1]
        for k in [75, 99]:
            one_percentile_plot(construct_df(), k).show()


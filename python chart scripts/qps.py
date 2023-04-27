import os
import altair as alt
import pandas as pd
import json

pc_cores = {1: 6, 2: 16}


def df_for_qps():
    realizations = []
    qps = []
    num_clients = []
    client_types = []
    latency = []
    errors = []
    for client in CLIENT_DIRS:
        realization_dirs = next(os.walk(ROOT_DIR + '/' + client))[1]
        for realization in realization_dirs:
            json_files = list(filter(lambda x: 'json' in x, next(os.walk(ROOT_DIR + '/' + client + '/' + realization))[2]))
            for res_file in json_files:
                with open(ROOT_DIR + '/' + client + '/' + realization + '/' + res_file, 'r') as rf:
                    realizations.append(realization)
                    data = json.load(rf)
                    num_clients.append(data['NumThreads'])
                    qps.append(data['ActualQPS'])
                    latency.append(data["DurationHistogram"]["Avg"])
                    errors.append(data["ErrorsDurationHistogram"]["Count"])
                    client_types.append(client)

    return pd.DataFrame({'Realizations': realizations,
                         'QPS': qps,
                         'Num_clients': num_clients,
                         'Client_types': client_types,
                         'AvgLat': latency,
                         'ErrorCount': errors}).groupby(["Realizations", "Num_clients"]).sum(True).reset_index()


def make_qps_chart():
    df = df_for_qps()
    df["Num_clients"] = df["Num_clients"].mul(3)
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Realizations:N', axis=None),
        y=alt.Y('QPS:Q', title="Queries per sec", scale=alt.Scale(domain=[0, 600000])),
        color=alt.Color('Realizations:N', title="Server Implementation", legend=None),
        column=alt.Column('Num_clients:O', title="Simultaneous connected clients number")
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    return bar_chart


def make_avg_latency_chart():
    df = df_for_qps()
    df["AvgLat"] = df["AvgLat"].div(3).mul(1000)
    chart_lin = alt.Chart(df).mark_line(point=alt.OverlayMarkDef()).encode(
        x=alt.X('Num_clients:Q', title=f"Simultaneous connected clients number"),
        y=alt.Y('AvgLat:Q', axis=alt.Axis(title=f'Average Latency, msec'), scale=alt.Scale(domain=[0, 35])),
        color=alt.Color('Realizations:N', title="Server Implementation", legend=None)
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    ).configure_title(
        anchor='middle'
    )

    return chart_lin


def make_error_count_chart():
    df = df_for_qps()
    df["Num_clients"] = df["Num_clients"].mul(3)
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Realizations:N', axis=None),
        y=alt.Y('ErrorCount:Q', title="Number of Timeout Errors", scale=alt.Scale(domain=[0, 3500])),
        color=alt.Color('Realizations:N', title="Server Implementation", legend=None),
        column=alt.Column('Num_clients:O', title="Simultaneous connected clients number")
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    return bar_chart


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


# make_avg_latency_chart().show()
# make_qps_chart().show()
# make_error_count_chart().show()


for i in [1, 2]:
    for j in [32, 64]:
        pc = i
        payload = j
        ROOT_DIR = f"newdata/pc{i}clients/{j}bytes"
        CLIENT_DIRS = next(os.walk(ROOT_DIR))[1]
        fix_fonts(make_error_count_chart()).show()

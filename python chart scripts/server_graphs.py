import os
import altair as alt
import pandas as pd


pc_cores = {1: 6, 2: 16}


def fix_df_names(df):
    df["Realizations"] = df["Realizations"].replace("simple_t", "threaded")
    df["Realizations"] = df["Realizations"].replace("pool", "threadpool")
    df["Realizations"] = df["Realizations"].replace("boost_t", "boost_threaded")


def get_files(payload: int, pc: int, category: str):
    payload_filtered = list(filter(lambda x: f'b{payload}' in x, next(os.walk(ROOT_DIR + '/'))[2]))
    pc_filtered = list(filter(lambda x: f'pc{pc}' in x, payload_filtered))
    type_filtered = list(filter(lambda x: f'{category}.txt' in x, pc_filtered))

    return type_filtered


def make_rtt_chart(payload: int, pc: int):
    files = get_files(payload, pc, "rtt")
    realizations = []
    rrt = []
    num_clients = []
    for res_file in files:
        with open(ROOT_DIR + '/' + res_file, 'r') as rf:
            realizations.append(res_file[0:res_file.find("_p")])
            client_index = res_file.find("c", res_file.find("c") + 1)
            num_clients.append(int(res_file[client_index + 1: res_file.find("0b") + 1]))
            for line in rf.readlines():
                if "All Addresses" in line:
                    rrt.append(line[line.find("AVG") + 3: -2])
                    break
    df = pd.DataFrame({'Realizations': realizations,
                       'Num_clients': num_clients,
                       'RRT': rrt})
    fix_df_names(df)
    df["Num_clients"] = df["Num_clients"].mul(3)
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Realizations:N', axis=None),
        y=alt.Y('RRT:Q', title="Round-trip Time, μsec"),
        color=alt.Color('Realizations:N', title="Server Implementation"),
        column=alt.Column('Num_clients:O', title="Simultaneous connected clients number")
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    bar_chart.show()


def make_cpu_chart(payload: int, pc: int):
    files = get_files(payload, pc, "cpu")

    realizations = []
    cpu = []
    num_clients = []
    for res_file in files:
        with open(ROOT_DIR + '/' + res_file, 'r') as rf:
            realizations.append(res_file[0:res_file.find("_p")])
            client_index = res_file.find("c", res_file.find("c") + 1)
            num_clients.append(int(res_file[client_index + 1: res_file.find("0b") + 1]))
            max_cpu = 0
            for line in rf.readlines():
                line = line.strip()
                try:
                    cpu_val = 100 - float(line[line.rfind(" "):].replace(",", "."))
                    if cpu_val > max_cpu:
                        max_cpu = cpu_val
                except:
                    continue
            cpu.append(max_cpu)

    df = pd.DataFrame({'Realizations': realizations,
                       'Num_clients': num_clients,
                       'CPU': cpu})
    fix_df_names(df)
    df["Num_clients"] = df["Num_clients"].mul(3)
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Realizations:N', axis=None),
        y=alt.Y('CPU:Q', title="CPU Utilization, %", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Realizations:N', title="Server Implementation", legend=None),
        column=alt.Column('Num_clients:O', title="Simultaneous connected clients number")
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    bar_chart.configure_title(
        fontSize=20,
        subtitleFontSize=16
    ).configure_axis(
        labelFontSize=20,
        titleFontSize=20
    ).configure_header(
        titleFontSize=16,
        labelFontSize=16
    ).show()


def make_cpudist_chart(payload: int, pc: int):
    files = get_files(payload, pc, "cpudist")
    realizations = []
    cpudist = []
    num_clients = []
    for res_file in files:
        with open(ROOT_DIR + '/' + res_file, 'r') as rf:
            realizations.append(res_file[0:res_file.find("_p")])
            client_index = res_file.find("c", res_file.find("c") + 1)
            num_clients.append(int(res_file[client_index + 1: res_file.find("0b") + 1]))
            for line in rf.readlines():
                if line.startswith("avg"):
                    cpudist.append(int(line.strip().split()[2]))
                    break

    df = pd.DataFrame({'Realizations': realizations,
                       'Num_clients': num_clients,
                       'CPUDist': cpudist})
    fix_df_names(df)
    df["Num_clients"] = df["Num_clients"].mul(3)
    df["CPUDist"] = df["CPUDist"].div(1000)
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Realizations:N', axis=None),
        y=alt.Y('CPUDist:Q', title="Average on-CPU time per task, msec", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Realizations:N', title="Server Implementation"),
        column=alt.Column('Num_clients:O', title="Simultaneous connected clients number")
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    bar_chart.configure_title(
        fontSize=20,
        subtitleFontSize=16
    ).configure_axis(
        labelFontSize=20,
        titleFontSize=20
    ).configure_header(
        titleFontSize=16,
        labelFontSize=16
    ).show()


def make_net_chart(payload: int, pc: int):
    files = get_files(payload, pc, "dev")

    realizations = []
    net = []
    num_clients = []
    for res_file in files:
        with open(ROOT_DIR + '/' + res_file, 'r') as rf:
            realizations.append(res_file[0:res_file.find("_p")])
            client_index = res_file.find("c", res_file.find("c") + 1)
            num_clients.append(int(res_file[client_index + 1: res_file.find("0b") + 1]))
            max_net = 0
            for line in rf.readlines():
                line = line.strip()
                if "enp" in line:
                    net_val = float(line.split()[4].replace(",", "."))
                    if net_val > max_net:
                        max_net = net_val

            net.append(max_net)

    df = pd.DataFrame({'Realizations': realizations,
                       'Num_clients': num_clients,
                       'Throughput': net})
    fix_df_names(df)
    df["Num_clients"] = df["Num_clients"].mul(3)
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Realizations:N', axis=None),
        y=alt.Y('Throughput:Q', title="Received/Sent kB per second, kBps", scale=alt.Scale(domain=[0, 50000])),
        color=alt.Color('Realizations:N', title="Server Implementation", legend=None),
        column=alt.Column('Num_clients:O', title="Simultaneous connected clients number")
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    bar_chart.configure_title(
        fontSize=20,
        subtitleFontSize=16
    ).configure_axis(
        labelFontSize=20,
        titleFontSize=20
    ).configure_header(
        titleFontSize=16,
        labelFontSize=16
    ).show()


def make_cache_chart(payload: int, pc: int):
    files = get_files(payload, pc, "llc")

    realizations = []
    references = []
    hit_percent = []
    num_clients = []
    for res_file in files:
        with open(ROOT_DIR + '/' + res_file, 'r') as rf:
            realizations.append(res_file[0:res_file.find("_p")])
            client_index = res_file.find("c", res_file.find("c") + 1)
            num_clients.append(int(res_file[client_index + 1: res_file.find("0b") + 1]))
            reference_num = 0
            count = 0
            hit = 0
            for line in rf.readlines():
                line = line.strip()
                if "echo_server" in line:
                    count += 1
                    reference_num += int(line.split()[3])
                    hit += float(line.split()[5].replace(",", ".")[:-1])

            try:
                references.append(reference_num / count)
                hit_percent.append(hit / count)
            except ZeroDivisionError:
                references.append(0)
                hit_percent.append(0)


    df = pd.DataFrame({'Realizations': realizations,
                       'Num_clients': num_clients,
                       'Refs': references,
                       'HitCount': hit_percent})
    fix_df_names(df)
    df["Num_clients"] = df["Num_clients"].mul(3)
    df["Refs"] = df["Refs"].div(1000000)
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Realizations:N', axis=None),
        y=alt.Y('Refs:Q', title="Total Cache References, M", scale=alt.Scale(domain=[0, 500])),
        color=alt.Color('Realizations:N', title="Server Implementation"),
        column=alt.Column('Num_clients:O', title="Simultaneous connected clients number")
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    bar_chart.configure_title(
        fontSize=20,
        subtitleFontSize=16
    ).configure_axis(
        labelFontSize=20,
        titleFontSize=20
    ).configure_header(
        titleFontSize=16,
        labelFontSize=16
    ).show()

    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Realizations:N', axis=None),
        y=alt.Y('HitCount:Q', title="Cache Hit, %", scale=alt.Scale(domain=[0, 100])),
        color=alt.Color('Realizations:N', title="Server Implementation"),
        column=alt.Column('Num_clients:O', title="Simultaneous connected clients number")
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    bar_chart.configure_title(
        fontSize=20,
        subtitleFontSize=16
    ).configure_axis(
        labelFontSize=20,
        titleFontSize=20
    ).configure_header(
        titleFontSize=16,
        labelFontSize=16
    ).show()


def make_sys_chart(payload: int, pc: int):
    tracked_syscalls = ["read", "write", "futex", "sendto", "recvfrom", "epoll_wait", "epoll_ctl", "poll"]

    files = get_files(payload, pc, "syscount")
    realizations = []
    syscount = []
    systime = []
    sysname = []
    num_clients = []
    for res_file in files:
        num_of_syscalls = 0
        for syscall in tracked_syscalls:
            with open(ROOT_DIR + '/' + res_file, 'r') as rf:
                for line in rf.readlines():
                    if len(line.strip().split()) > 1 and line.strip().split()[0] == syscall:
                        num_of_syscalls += 1
                        sysname.append(syscall)
                        syscount.append(int(line.strip().split()[1]))
                        systime.append(float(line.strip().split()[2]))

        realizations.extend([res_file[0:res_file.find("_p")]] * num_of_syscalls)
        client_index = res_file.find("c", res_file.find("c") + 1)
        num_clients.extend([int(res_file[client_index + 1: res_file.find("0b") + 1])] * num_of_syscalls)

    df = pd.DataFrame({'Realizations': realizations,
                       'Num_clients': num_clients,
                       'Syscall': sysname,
                       'SysCount': syscount,
                       'SysTime': systime})
    fix_df_names(df)
    df["Num_clients"] = df["Num_clients"].mul(3)

    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('Realizations:N', axis=None),
        y=alt.Y('SysCount:Q', title="Average on-CPU time per task, microseconds"),
        color=alt.Color('Realizations:N', title="Server Implementation"),
        column=alt.Column('Num_clients:O', title="Simultaneous connected clients number"),
    ).properties(
        title={
            "text": [f"Server PC: {pc_cores[pc]} logical cores, Payload size: {payload}"],
        }
    )

    bar_chart.configure_title(
        fontSize=20,
        subtitleFontSize=16
    ).configure_axis(
        labelFontSize=20,
        titleFontSize=20
    ).configure_header(
        titleFontSize=16,
        labelFontSize=16
    ).show()


for j in [2]:
    for i in [64]:
        ROOT_DIR = f"newdata/pc{j}server"
        # make_net_chart(i, j)
        # make_cpu_chart(i, j)
        # make_cpudist_chart(i, j)  # !!!!!!!!!!!!!!!!
        make_cache_chart(i, j)
        # make_rtt_chart(i, j)
        # make_sys_chart(32, i)

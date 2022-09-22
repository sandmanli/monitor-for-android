# -*- coding: utf-8 -*-
import codecs
import datetime as dt
from typing import List, Any

import numpy as np
import os
import pandas as pd
import sys
import csv
import time
from pandas.core.indexing import length_of_indexer


def log(info):
    print('{} {}'.format(dt.datetime.now(), info))


def findPath(path, n):
    lists = []
    for mainDir, subDir, file_name_list in os.walk(path):
        for filename in file_name_list:
            if filename == n:
                lists.append(mainDir)
    return lists


def copyFiles(sourceDir, targetDir):
    copyFileCounts = 0
    log(sourceDir)
    log('copy {} the {}th file'.format(sourceDir, copyFileCounts))
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)

        if os.path.isfile(sourceF):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            copyFileCounts += 1
            if not os.path.exists(targetF) or (
                    os.path.exists(targetF) and (os.path.getsize(targetF) != os.path.getsize(sourceF))):
                open(targetF, "wb").write(open(sourceF, "rb").read())
                log('{} finish copying'.format(targetF))
            else:
                log('{} exist'.format(targetF))

        if os.path.isdir(sourceF):
            copyFiles(sourceF, targetF)


class Monitor(object):

    def __init__(self):
        self.path = None
        self.csvPath = None
        self.maxPath = None
        self.fileName = None
        self.js = None

    def main(self):
        TotalData = {}
        charts_out = {}
        tmp = self.getData('windows.csv')
        charts_out['Window'] = tmp[0]
        if tmp[0] == 1:
            TotalData['Window'] = tmp[1]
        tmp = self.getData('btm.csv')
        charts_out['btm'] = tmp[0]
        if tmp[0] == 1:
            TotalData['btm'] = tmp[1]
        tmp = self.getData('cpu.csv')
        charts_out['cpu'] = tmp[0]
        if tmp[0] == 1:
            TotalData['cpuData'] = tmp[1]
        tmp = self.getData('cpuinfo.csv')
        charts_out['cpuInfo'] = tmp[0]
        if tmp[0] == 1:
            TotalData['cpuLine'] = tmp[1][0]
            TotalData['cpuInfo'] = tmp[1][1]
            writePath = os.path.join(self.maxPath, '{}_maxCpu.csv'.format(self.fileName))
            header = ['Path', 'Command', 'CPU']
            with open(writePath, 'w', encoding='utf-8', newline='') as fp:
                writer = csv.writer(fp)
                writer.writerow(header)
                for i in range(len(tmp[1][0])):
                    writer.writerow([self.path, tmp[1][0][i][0], tmp[1][0][i][2]])
        tmp = self.getData('mem.csv')
        charts_out['mem'] = tmp[0]
        if tmp[0] == 1:
            TotalData['memData'] = tmp[1]
        tmp = self.getData('mem2.csv')
        charts_out['mem2'] = tmp[0]
        if tmp[0] == 1:
            TotalData['mem2Data'] = tmp[1]
        tmp = self.getData('meminfo.csv')
        charts_out['memInfo'] = tmp[0]
        if tmp[0] == 1:
            TotalData['pssLine'] = tmp[1][0]
            TotalData['memInfo'] = tmp[1][1]
            writePath = os.path.join(self.maxPath, '{}_maxPSS.csv'.format(self.fileName))
            header = ['Path', 'Command', 'Pss Difference(M)', 'Pss(M)']
            with open(writePath, 'w', encoding='utf-8', newline='') as fp:
                writer = csv.writer(fp)
                writer.writerow(header)
                for i in range(len(tmp[1][0])):
                    writer.writerow([self.path, tmp[1][0][i][0], tmp[1][0][i][2], tmp[1][0][i][3]])
        tmp = self.getData('meminfo2.csv')
        charts_out['psMeminfo'] = tmp[0]
        if tmp[0] == 1:
            TotalData['vssLine'] = tmp[1][0]
            TotalData['psMeminfo'] = tmp[1][1]
            writePath = os.path.join(self.maxPath, '{}_maxVSS.csv'.format(self.fileName))
            header = ['Path', 'Command', 'VSS Difference(M)', 'VSS(M)']
            with open(writePath, 'w', encoding='utf-8', newline='') as fp:
                writer = csv.writer(fp)
                writer.writerow(header)
                for i in range(len(tmp[1][0])):
                    writer.writerow([self.path, tmp[1][0][i][0], tmp[1][0][i][2], tmp[1][0][i][3]])
        tmp = self.getData('fps_window.csv')
        charts_out['fps'] = tmp[0]
        if tmp[0] == 1:
            TotalData['fpsList'] = tmp[1][0]
            TotalData['fpsData'] = tmp[1][1]
        tmp = self.getData('cur_freq.csv')
        charts_out['curFreq'] = tmp[0]
        if tmp[0] == 1:
            TotalData['curFreqData'] = tmp[1]
        tmp = self.getData('thermal.csv')
        charts_out['thermal'] = tmp[0]
        if tmp[0] == 1:
            TotalData['thermalData'] = tmp[1]
        tmp = self.getData('others.csv')
        charts_out['gpuFreq'] = tmp[0]
        if tmp[0] == 1:
            TotalData['gpuFreqData'] = tmp[1]
        tmp = self.getData('cpus.csv')
        charts_out['cpus'] = tmp[0]
        if tmp[0] == 1:
            TotalData['cpusData'] = tmp[1]
        f = codecs.open(self.js, "w", "utf-8")
        f.write("var csvData={};\nvar TotalData={};".format(charts_out, TotalData))
        f.close()
        log('Finish: {}'.format(self.js))

    def getData(self, csvName):
        self.csvPath = os.path.join(self.path, csvName)
        out = 0
        data = []
        if not os.path.exists(self.csvPath):
            log('There is no {} in {}'.format(csvName, self.path))
        else:
            if len(open(self.csvPath).readlines()) > 2:
                # check_csv 如果测试数据csv异常中断读写，最后一行异常数据需清理
                with open(self.csvPath, 'rb') as fh:
                    first = next(fh).decode()
                    offs = -100
                    while True:
                        fh.seek(offs, 2)
                        lines = fh.readlines()
                        if len(lines) > 1:
                            last = lines[-1].decode()
                            break
                        offs *= 2
                    L_first = len(first.split(','))
                    L_last = len(last.split(','))
                if L_last != L_first:
                    log("Delete the last line of {}".format(self.csvPath))
                    with open(self.csvPath) as f:
                        lines = f.readlines()
                        curr = lines[:-1]
                    f = open(self.csvPath, 'w')
                    f.writelines(curr)
                    f.close()
                # 按照csv名字分别数据处理
                if csvName == 'windows.csv':
                    data = self.Windows()
                elif csvName == 'btm.csv':
                    data = self.btm()
                elif csvName == 'cur_freq.csv':
                    data = self.curfreq()
                elif csvName == 'cpu.csv':
                    data = self.cpu()
                elif csvName == 'cpus.csv':
                    data = self.cpus()
                elif csvName == 'cpuinfo.csv':
                    data = self.cpuinfo()
                elif csvName == 'mem.csv':
                    data = self.mem()
                elif csvName == 'mem2.csv':
                    data = self.mem2()
                elif csvName == 'meminfo.csv':
                    data = self.meminfo()
                elif csvName == 'meminfo2.csv':
                    data = self.meminfo2()
                elif csvName == 'meminfo2.csv':
                    data = self.meminfo2()
                elif csvName == 'fps_window.csv':
                    data = self.FPS()
                    fps_list = []
                    fps_data = []
                    for i in range(len(data)):
                        fps_list.append('{}_{}'.format(data[i][0], data[i][1]))
                        fps_data.append(data[i][2])
                    self.csvPath = os.path.join(self.path, 'fps_system.csv')
                    if len(open(self.csvPath).readlines()) > 2:
                        data = self.FPS()
                        fps_list.append('System')
                        fps_data.append(data[0][2])
                    data = [fps_list, fps_data]
                elif csvName == 'thermal.csv':
                    data = self.thermal()
                elif csvName == 'others.csv':
                    data = self.gpuFreq()
                out = 1
            else:
                log('No data in {}'.format(self.csvPath))
        return [out, data]

    def Windows(self):
        log('windows.csv')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value='null')
        data = data[data['DisplayID'].values == 0]
        Time = data['uptime'].astype('Float64').values.tolist()
        Date_Time = data['Date_Time'].values.tolist()
        FocusedWindow = data['FocusedWindow'].values.tolist()
        FocusedActivity = data['FocusedActivity'].values.tolist()
        log('windows Finish')
        return [Time, Date_Time, FocusedWindow, FocusedActivity]

    def btm(self):
        log('btm.csv')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value='null')
        Time = data['uptime'].astype('Float64').values.tolist()
        BatteryLevel = data['BatteryLevel'].tolist()
        Batterytype = data['PlugType'].tolist()
        for i in range(len(BatteryLevel)):
            BatteryLevel[i] = int(BatteryLevel[i])
            Batterytype[i] = int(Batterytype[i])
        log('btm Finish')
        return [Time, BatteryLevel, Batterytype]

    def curfreq(self):
        log('cur_freq.csv')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value=0)
        Time = data['uptime'].astype('Float64').values.tolist()
        cpus = int(data.columns[1].replace('0:', ''))
        series = []
        for i in range(1, cpus + 1):
            tmp = data[data.columns[i]].astype('Float64').values.tolist()
            series.append(tmp)
        log('cur_freq Finish')
        return [Time, series]

    def cpus(self):
        log('cpus.csv')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value=0)
        Time = data['uptime'].astype('Float64').values.tolist()
        cpus = int(data.columns[-1]) + 1
        series = []
        statistics = []
        for i in range(1, cpus + 2):
            tmp = data[data.columns[i]].astype('Float64').values.tolist()
            series.append(tmp)
            statistics.append([round(float(np.mean(tmp)), 1), round(float(np.median(tmp)), 1)])
        log('cpus Finish')
        return [Time, series, statistics]

    def cpu(self):
        log('cpu.csv')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value='null')
        Time = data['uptime'].astype('Float64').values.tolist()
        Y_usr = data['usr'].astype('Float64').values.tolist()
        Y_sys = data['sys'].astype('Float64').values.tolist()
        Y_nic = data['nic'].astype('Float64').tolist()
        Y_idle = data['idle'].astype('Float64').values.tolist()
        Y_io = data['io'].astype('Float64').tolist()
        Y_irq = data['irq'].astype('Float64').tolist()
        Y_sirq = data['sirq'].astype('Float64').tolist()
        log('cpu Finish')
        return [Time, [Y_usr, round(float(np.mean(Y_usr)), 1), round(float(np.median(Y_usr)), 1)],
                [Y_sys, round(float(np.mean(Y_sys)), 1), round(float(np.median(Y_sys)), 1)],
                [Y_nic, round(float(np.mean(Y_nic)), 1), round(float(np.median(Y_nic)), 1)],
                [Y_idle, round(float(np.mean(Y_idle)), 1), round(float(np.median(Y_idle)), 1)],
                [Y_io, round(float(np.mean(Y_io)), 1), round(float(np.median(Y_io)), 1)],
                [Y_irq, round(float(np.mean(Y_irq)), 1), round(float(np.median(Y_irq)), 1)],
                [Y_sirq, round(float(np.mean(Y_sirq)), 1), round(float(np.median(Y_sirq)), 1)]]

    def cpuinfo(self):
        log('cpuinfo.csv')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value='null')
        Command = data['Command'].unique().tolist()
        maxCpu = []
        cpuinfo_data = []
        h = 0
        for c in Command:
            h += 1
            log('cpuinfo Command: {}'.format(c))
            data_command = data[data['Command'].values == c]
            Uptime = data_command['uptime'].astype('Float64').values.tolist()
            Pid = data_command['PID'].values.tolist()
            CPU = data_command['%CPU'].astype('Float64').values.tolist()
            CPU_max = [max(CPU), round(float(np.mean(CPU)), 1), round(float(np.median(CPU)), 1)]
            ARG = data_command['args'].values.tolist()
            thread = data_command['Thread'].values.tolist()
            tmp = len(Uptime)
            p = 1
            d_pid = [Pid[0]]
            d_times = 0
            for i in range(1, tmp):
                if Uptime[p] == Uptime[p - 1]:
                    d_times = d_times + 1
                    del Uptime[p]
                    d_pid.append(Pid[p])
                    del Pid[p]
                    if isinstance(CPU[p - 1], list) is False and isinstance(CPU[p], list) is False:
                        CPU[p - 1] = [round(CPU[p - 1] + CPU[p], 1), 2, d_times]
                    else:
                        CPU[p - 1] = [round(CPU[p - 1][0] + CPU[p], 1), 2, d_times]
                    del CPU[p]
                    del ARG[p]
                    del thread[p]
                else:
                    d_times = 0
                    if Pid[p] != Pid[p - 1] and Pid[p] not in d_pid:
                        d_pid.append(Pid[p])
                        CPU[p] = [CPU[p], 1]
                    p = p + 1
            cpuinfo_data.append([Uptime, CPU, ARG, thread])
            maxCpu.append([c, h, CPU_max])
        maxCpu.sort(key=lambda a_tuple: a_tuple[2], reverse=True)
        log('cpuinfo Finish')
        return [maxCpu, cpuinfo_data]

    def mem(self):
        log('mem.csv')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value='null')
        Time = data[data.columns[0]].astype('Float64').values.tolist()
        if 'MemAvailable' in data.columns:
            MemAvailable = (data['MemAvailable'] / 1024).astype('Float64').values.tolist()
        else:
            MemAvailable = ((data['MemFree'] + data['Buffers'] + data['Cached']) / 1024).astype('Float64').values.tolist()
        MemFree = (data['MemFree'] / 1024).astype('Float64').values.tolist()
        Buffers = (data['Buffers'] / 1024).astype('Float64').values.tolist()
        Cached = (data['Cached'] / 1024).astype('Float64').values.tolist()
        Active = (data['Active'] / 1024).astype('Float64').values.tolist()
        Inactive = (data['Inactive'] / 1024).astype('Float64').values.tolist()
        Active_a = (data['Active(anon)'] / 1024).astype('Float64').values.tolist()
        Inactive_a = (data['Inactive(anon)'] / 1024).astype('Float64').values.tolist()
        Active_f = (data['Active(file)'] / 1024).astype('Float64').values.tolist()
        Inactive_f = (data['Inactive(file)'] / 1024).astype('Float64').values.tolist()
        Dirty = (data['Dirty'] / 1024).astype('Float64').values.tolist()
        Writeback = (data['Writeback'] / 1024).astype('Float64').values.tolist()
        Mapped = (data['Mapped'] / 1024).astype('Float64').values.tolist()
        Slab = (data['Slab'] / 1024).astype('Float64').values.tolist()
        IO = ((data['Dirty'] + data['Writeback']) / 1024).astype('Float64').values.tolist()
        for i in range(len(Time)):
            MemAvailable[i] = round(MemAvailable[i], 2)
            MemFree[i] = round(MemFree[i], 2)
            Buffers[i] = round(Buffers[i], 2)
            Cached[i] = round(Cached[i], 2)
            Active[i] = round(Active[i], 2)
            Inactive[i] = round(Inactive[i], 2)
            Active_a[i] = round(Active_a[i], 2)
            Inactive_a[i] = round(Inactive_a[i], 2)
            Active_f[i] = round(Active_f[i], 2)
            Inactive_f[i] = round(Inactive_f[i], 2)
            Dirty[i] = round(Dirty[i], 2)
            Writeback[i] = round(Writeback[i], 2)
            Mapped[i] = round(Mapped[i], 2)
            Slab[i] = round(Slab[i], 2)
            IO[i] = round(IO[i], 2)
        FreeInfo = [MemFree, Buffers, Cached]
        log('mem Finish')
        return [Time, MemAvailable, FreeInfo, Active, Active_a, Active_f, Inactive, Inactive_a, Inactive_f, IO, Mapped, Slab,
                Dirty, Writeback]

    def mem2(self):
        log('mem2.csv')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value=0)
        columns = data.columns.tolist()
        del columns[0]
        Time = data[data.columns[0]].astype('Float64').values.tolist()
        D_mmap = []
        N_mmap = []
        D_mmap_other = []
        N_mmap_other = []
        for i in range(1, len(columns) + 1):
            if columns[i - 1].find('_mmap') < 0:
                N_mmap_other.append(columns[i - 1])
                D_mmap_other.append((data[data.columns[i]] / 1024).astype('Float64').values.tolist())
            else:
                N_mmap.append(columns[i - 1])
                D_mmap.append((data[data.columns[i]] / 1024).astype('Float64').values.tolist())
        for i in range(len(D_mmap)):
            for j in range(len(D_mmap[i])):
                D_mmap[i][j] = round(D_mmap[i][j], 2)
        for i in range(len(D_mmap_other)):
            for j in range(len(D_mmap_other[i])):
                D_mmap_other[i][j] = round(D_mmap_other[i][j], 2)
        log('mem2 Finish')
        return [Time, N_mmap, D_mmap, N_mmap_other, D_mmap_other]

    def meminfo(self):
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value='null')
        log('meminfo.csv')
        fd_type = len(data.columns)
        Command = data['Process_Name'].unique().tolist()
        log("Command=%s" % Command)
        maxPd = []
        meminfo_data = []
        h = 0
        for c in Command:
            log("c=%s" % c)
            data_command = data[data['Process_Name'].values == c]
            Time = data_command['uptime'].astype('Float64').values.tolist()
            Pid = data_command['PID'].values.tolist()
            Pss = (data_command['Pss'] / 1024).astype('Float64').values.tolist()
            tmp = (data_command[data_command['Pss'].values > 0]['Pss'] / 1024).astype('Float64').values.tolist()
            if len(tmp) > 0:
                Pss_max = max(tmp)
                Pss_min = min(tmp)
                Pss_mean = round(float(np.mean(tmp)), 2)
                Pss_median = round(float(np.median(tmp)), 2)
            else:
                Pss_max = 0
                Pss_min = 0
                Pss_mean = 0
                Pss_median = 0
            ARG = data_command['Args'].values.tolist()
            FD = []
            if data_command['Native_Heap(Size)'].head(1).values[0] == 'null' or int(
                    data_command['Native_Heap(Size)'].head(1).values[0]) == 0:
                meminfo_type = 0
                NHS = NHA = NHF = DHP = DHS = DHA = DHF = Views = Threads = FD = []
            else:
                meminfo_type = 1
                NHS = (data_command['Native_Heap(Size)'].replace('null', 0) / 1024).values.tolist()
                NHA = (data_command['Native_Heap(Alloc)'].replace('null', 0) / 1024).values.tolist()
                NHF = (data_command['Native_Heap(Free)'].replace('null', 0) / 1024).values.tolist()
                DHP = (data_command['Dalvik_Other'].replace('null', 0) / 1024).values.tolist()
                DHS = (data_command['Dalvik_Heap(Size)'].replace('null', 0) / 1024).values.tolist()
                DHA = (data_command['Dalvik_Heap(Alloc)'].replace('null', 0) / 1024).values.tolist()
                DHF = (data_command['Dalvik_Heap(Free)'].replace('null', 0) / 1024).values.tolist()
                Views = data_command['Views'].replace('null', 0).tolist()
                Threads = data_command['Threads'].replace('null', 0).tolist()
                if fd_type == 15:
                    FD = data_command['FD'].replace('null', 0).astype('Int32').tolist()
            Time[0] = round(Time[0], 2)
            Pss[0] = round(Pss[0], 2)
            if meminfo_type == 1:
                NHS[0] = round(NHS[0], 2)
                NHA[0] = round(NHA[0], 2)
                NHF[0] = round(NHF[0], 2)
                DHP[0] = round(DHP[0], 2)
                DHS[0] = round(DHS[0], 2)
                DHA[0] = round(DHA[0], 2)
                DHF[0] = round(DHF[0], 2)
                Views[0] = int(Views[0])
                Threads[0] = int(Threads[0])

            p = 1
            d_pid = [Pid[0]]
            d_times = 0
            for i in range(1, len(Time)):
                Time[p] = round(Time[p], 2)
                Pss[p] = round(Pss[p], 2)
                if meminfo_type == 1:
                    NHS[p] = round(NHS[p], 2)
                    NHA[p] = round(NHA[p], 2)
                    NHF[p] = round(NHF[p], 2)
                    DHP[p] = round(DHP[p], 2)
                    DHS[p] = round(DHS[p], 2)
                    DHA[p] = round(DHA[p], 2)
                    DHF[p] = round(DHF[p], 2)
                    Views[p] = int(Views[p])
                    Threads[p] = int(Threads[p])
                if Time[p] == Time[p - 1]:
                    d_pid.append(Pid[p])
                    d_times = d_times + 1
                    if isinstance(Pss[p - 1], list) is False:
                        Pss[p - 1] = [round(Pss[p - 1] + Pss[p], 2), 2, d_times]
                    else:
                        Pss[p - 1] = [round(Pss[p - 1][0] + Pss[p], 2), 2, d_times]
                    del Pss[p]
                    if meminfo_type == 1:
                        NHS[p - 1] = round(NHS[p - 1] + NHS[p], 2)
                        NHA[p - 1] = round(NHA[p - 1] + NHA[p], 2)
                        NHF[p - 1] = round(NHF[p - 1] + NHF[p], 2)
                        DHP[p - 1] = round(DHP[p - 1] + DHP[p], 2)
                        DHS[p - 1] = round(DHS[p - 1] + DHS[p], 2)
                        DHA[p - 1] = round(DHA[p - 1] + DHA[p], 2)
                        DHF[p - 1] = round(DHF[p - 1] + DHF[p], 2)
                        Views[p - 1] = round(Views[p - 1] + Views[p], 2)
                        Threads[p - 1] = round(Threads[p - 1] + Threads[p], 2)
                        del NHS[p]
                        del NHA[p]
                        del NHF[p]
                        del DHP[p]
                        del DHS[p]
                        del DHA[p]
                        del DHF[p]
                        del Views[p]
                        del Threads[p]
                        if fd_type == 15:
                            del FD[p]
                    del Pid[p]
                    del Time[p]
                    del ARG[p]
                else:
                    if Pid[p] != Pid[p - 1] and Pid[p] not in d_pid:
                        d_pid.append(Pid[p])
                        Pss[p] = [Pss[p], 1]
                    p += 1
            if meminfo_type == 0:
                meminfo_data.append([meminfo_type, Time, ARG, Pss, FD])
            else:
                meminfo_data.append(
                    [meminfo_type, Time, ARG, Pss, Views, Threads, NHS, NHA, NHF, DHP, DHS, DHA, DHF, FD])
            maxPd.append(
                [c, h, round((Pss_max - Pss_min) * 1.0, 2), round(Pss_max * 1.0, 2), Pss_mean, Pss_median])
            h += 1
        maxPd.sort(key=lambda a_tuple: a_tuple[2], reverse=True)
        log('meminfo Finish')
        return [maxPd, meminfo_data]

    def meminfo2(self):
        log('meminfo2.csv')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value='null')
        Command = data['COMMAND'].unique().tolist()
        maxPd = []
        meminfo_data = []
        h = 0
        for c in Command:
            data_command = data[data['COMMAND'].values == c]
            Time = data_command['uptime'].values.tolist()
            Pid = data_command['PID'].values.tolist()
            VSZ = data_command['VSZ'].values.tolist()
            RSS = data_command['RSS'].values.tolist()
            tmp = data_command[data_command['VSZ'].values > 0]['VSZ'].values.tolist()
            if len(tmp) > 0:
                VSZ_max = max(tmp)
                VSZ_min = min(tmp)
                VSZ_mean = round(float(np.mean(tmp)), 2)
                VSZ_median = round(float(np.median(tmp)), 2)
            else:
                VSZ_max = 0
                VSZ_min = 0
                VSZ_mean = 0
                VSZ_median = 0
            ARG = data_command['Args'].values.tolist()

            p = 1
            d_pid = [Pid[0]]
            d_times = 0
            for i in range(1, len(Time)):
                Time[p] = round(Time[p], 2)
                VSZ[p] = round(VSZ[p], 3)
                RSS[p] = round(RSS[p], 3)
                if Time[p] == Time[p - 1]:
                    d_pid.append(Pid[p])
                    d_times = d_times + 1
                    if isinstance(VSZ[p - 1], list) is False:
                        VSZ[p - 1] = [round(VSZ[p - 1] + VSZ[p], 3), 2, d_times]
                    else:
                        VSZ[p - 1] = [round(VSZ[p - 1][0] + VSZ[p], 3), 2, d_times]
                    RSS[p - 1] = round(RSS[p - 1] + RSS[p], 3)
                    del VSZ[p]
                    del RSS[p]
                    del Pid[p]
                    del Time[p]
                    del ARG[p]
                else:
                    if Pid[p] != Pid[p - 1] and Pid[p] not in d_pid:
                        d_pid.append(Pid[p])
                        VSZ[p] = [VSZ[p], 1]
                    p = p + 1
            meminfo_data.append([Time, ARG, VSZ, RSS])
            maxPd.append([c, h, round(VSZ_max - VSZ_min, 3), round(VSZ_max, 3), VSZ_mean, VSZ_median])
            h += 1
        maxPd.sort(key=lambda a_tuple: a_tuple[2], reverse=True)
        log('meminfo2 Finish')
        return [maxPd, meminfo_data]

    def FPS(self):
        log('FPS Start')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value='null')
        WN = data['WN'].max()
        if os.path.basename(self.path) == 'fps_system.csv':
            t_window = 'System'
        else:
            t_window = data.columns[2].replace('Date:', '').split('/')[-1]
        seria = []
        for i in range(1, WN + 1):
            data = data[data['WN'] == i]
            D_FU = data['FU(s)'].values.tolist()
            D_LU = data['LU(s)'].values.tolist()
            D_Date = data[data.columns[2]].values.tolist()
            D_FPS = data[data.columns[3]].values.tolist()
            D_Frames = data['Frames'].tolist()
            D_jank = data['jank'].tolist()
            D_jank_percent = (data['jank'] / data['Frames'] * 100).tolist()
            D_MFS = data['MFS(ms)'].tolist()
            D_OKT = data[data.columns[8]].tolist()
            D_OKT_percent = (data[data.columns[8]] / data['Frames'] * 100).tolist()
            D_SS = data['SS(%)'].values.tolist()
            for j in range(len(D_FU)):
                D_FU[j] = round(D_FU[j], 3)
                D_LU[j] = round(D_LU[j], 3)
                D_jank_percent[j] = round(D_jank_percent[j], 1)
                D_OKT_percent[j] = round(D_OKT_percent[j], 1)
                D_Frames[j] = int(D_Frames[j])
                D_jank[j] = int(D_jank[j])
                D_MFS[j] = int(D_MFS[j])
                D_OKT[j] = int(D_OKT[j])
            seria.append([t_window, i, [D_FU, D_LU, D_Date, D_FPS, D_Frames, D_jank, D_MFS, D_OKT, D_SS, D_OKT_percent,
                                        D_jank_percent]])
        log('FPS Finish')
        return seria

    def thermal(self):
        log('thermal Start')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value=0)
        columns = data.columns.tolist()
        del columns[0]
        Time = data['uptime'].values.tolist()
        thermalData = []
        for i in range(len(columns)):
            D = data[data.columns[i + 1]].tolist()
            for j in range(len(D)):
                D[j] = int(D[j])
            thermalData.append(D)
        log('thermal Finish')
        return [Time, columns, thermalData]

    def gpuFreq(self):
        log('gpu Start')
        data = pd.read_csv(self.csvPath, low_memory=False).fillna(value=0)
        Time = data['uptime'].values.tolist()
        gpu_freq = data['gpu_freq'].tolist()
        if 'gpu' in data.columns:
            check = 1
            gpu = data['gpu'].astype('Float64').tolist()
        else:
            check = 0
            gpu = []
        for i in range(len(gpu_freq)):
            gpu_freq[i] = int(gpu_freq[i])
        log('gpu Finish')
        if check == 0:
            return [Time, gpu_freq]
        else:
            return [Time, gpu_freq, gpu, round(float(np.mean(gpu)), 1), round(float(np.median(gpu)), 1)]


if __name__ == '__main__':
    results = findPath(sys.argv[1], "windows.csv")
    DATA_Path = sys.argv[1]
    dataPath = os.path.join(DATA_Path, 'data')
    maxCsvPath = os.path.join(DATA_Path, 'maxCSV')

    import shutil

    if os.path.exists(dataPath):
        try:
            shutil.rmtree(dataPath)
        except os.error as err:
            time.sleep(0.5)
            try:
                shutil.rmtree(dataPath)
            except os.error as err:
                log("Delete data Error!!!")

    if os.path.exists(maxCsvPath):
        try:
            shutil.rmtree(maxCsvPath)
        except os.error as err:
            time.sleep(0.5)
            try:
                shutil.rmtree(maxCsvPath)
            except os.error as err:
                log("Delete data Error!!!")
    copyFiles(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'monitor_HTML'), DATA_Path)
    if not os.path.exists(dataPath):
        os.mkdir(dataPath)
    if not os.path.exists(maxCsvPath):
        os.mkdir(maxCsvPath)

    outJs = Monitor()
    if len(results) > 0:
        caseList = []
        monitorList = []
        case = ""

        for Path in results:
            name = os.path.split(Path)
            tmpName = os.path.split(name[-2])
            if case == "":
                case = tmpName[-1]
                monitorList = [name[-1]]
            else:
                if case == tmpName[-1]:
                    monitorList.append(name[-1])
                else:
                    s = 0
                    for a in range(len(caseList)):
                        if caseList[a][0] == case:
                            caseList[a][1].extend(monitorList)
                            caseList[a][1].sort(reverse=True)
                            s = 1
                            break
                    if s == 0:
                        monitorList.sort(reverse=True)
                        caseList.append([case, monitorList])
                    case = tmpName[-1]
                    monitorList = [name[-1]]
            log('Start outJs: {}_{}.js'.format(tmpName[-1], name[-1]))
            outJs.path = Path
            outJs.maxPath = maxCsvPath
            outJs.fileName = '{}_{}'.format(tmpName[-1], name[-1])
            outJs.js = os.path.join(dataPath, '{}_{}.js'.format(tmpName[-1], name[-1]))
            outJs.main()
        s = 0
        for a in range(len(caseList)):
            if caseList[a][0] == case:
                caseList[a][1].extend(monitorList)
                caseList[a][1].sort(reverse=True)
                s = 1
                break
        if s == 0:
            monitorList.sort(reverse=True)
            caseList.append([case, monitorList])
        caseList.sort(key=lambda a_tuple: a_tuple[0], reverse=False)
        jsCodeStr = "var caseList={}".format(caseList)
        Path = os.path.join(dataPath, 'list.js')
        file = codecs.open(Path, "w", "utf-8")
        file.write(jsCodeStr)
        file.close()
        log('Finish: list.js')
    else:
        log('Not Found monitor csv files.')

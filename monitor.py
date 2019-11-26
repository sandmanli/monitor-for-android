# -*- coding: utf-8 -*-
import codecs
import datetime as dt
import os
import pandas as pd
import sys
import time
from pandas.core.indexing import length_of_indexer

def log(info):
    print('%s %s'%(dt.datetime.now(), info))

def findPath(path, name):
    lists = []
    for maindir, subdir, file_name_list in os.walk(r'%s'%path):
        for filename in file_name_list:
            if filename == name:
                lists.append(maindir)
    return lists

def copyFiles(sourceDir, targetDir):
    copyFileCounts = 0
    log(sourceDir)
    log('copy %s the %sth file'%(sourceDir,copyFileCounts))
    for f in os.listdir(sourceDir):
        sourceF = os.path.join(sourceDir, f)
        targetF = os.path.join(targetDir, f)

        if os.path.isfile(sourceF):
            if not os.path.exists(targetDir):
                os.makedirs(targetDir)
            copyFileCounts +=  1
            if not os.path.exists(targetF) or (os.path.exists(targetF) and (os.path.getsize(targetF) !=  os.path.getsize(sourceF))):
                open(targetF, "wb").write(open(sourceF, "rb").read())
                log('%s finish copying'%targetF)
            else:
                log('%s exist'%targetF)

        if os.path.isdir(sourceF):
            copyFiles(sourceF, targetF)

class monitor():

    def main(self, csvPath, jsfile):
        charts_out = []
        js = ""

        tmp = self.getData(csvPath,'windows.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var Windows=%s;
"""%tmp[1]

        tmp = self.getData(csvPath,'btm.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var btm=%s;
"""%tmp[1]

        tmp = self.getData(csvPath,'cpu.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var cpudata=%s;
"""%tmp[1]

        tmp = self.getData(csvPath,'cpuinfo.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var cpuline=%s;
function getcpuinfodata(p){
    var cpuinfo=%s;
    return cpuinfo[p];
}
"""%(tmp[1][0], tmp[1][1])
            writepath = os.path.join(os.path.dirname(jsfile),'maxCPU.csv')
            f=open(writepath,'a')
            for l in range(len(tmp[1][0])):
                f.write('%s,%s,%s'%(csvPath, tmp[1][0][l][0], tmp[1][0][l][2]))
                f.write("\n")
            f.close()

        tmp = self.getData(csvPath,'mem.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
function getmemdata(a){
    var data=%s;
    switch (a){
    case 'free':
        return [data[0], data[1], data[2]];
        break;
    case 'all':
        return [data[0], data[1], data[3], data[6], data[9], data[10], data[11]];
        break;
    case 'io':
        return [data[0], data[9], data[12], data[13]];
        break;
    case 'AI':
        return [data[0], data[3], data[6], data[4], data[7], data[5], data[8]];
        break;
    case 'MS':
        return [data[0], data[9], data[10]];
        break;
    }
}
"""%tmp[1]

        tmp = self.getData(csvPath,'mem2.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
function getmem2data(a){
    var data=%s;
    switch (a){
        case 'mmap':
            return [data[0], data[1], data[2]];
            break;
        case 'other':
            return [data[0], data[3], data[4]];
            break;
    }
}
"""%tmp[1]

        tmp = self.getData(csvPath,'meminfo.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var pssline=%s;
function getmeminfodata(p){
    var meminfo=%s;
    return meminfo[p];
}
"""%(tmp[1][0], tmp[1][1])
            writepath = os.path.join(os.path.dirname(jsfile),'maxPSS.csv')
            f=open(writepath,'a')
            for l in range(len(tmp[1][0])):
                f.write('%s,%s,%s,%s'%(csvPath, tmp[1][0][l][0], tmp[1][0][l][2], tmp[1][0][l][3]))
                f.write("\n")
            f.close()

        tmp = self.getData(csvPath,'meminfo2.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var vssline=%s;
function getvssdata(p){
    var meminfo = %s;
    return meminfo[p];
}
"""%(tmp[1][0], tmp[1][1])
            writepath = os.path.join(os.path.dirname(jsfile),'maxVSS.csv')
            f=open(writepath,'a')
            for l in range(len(tmp[1][0])):
                f.write('%s,%s,%s,%s'%(csvPath, tmp[1][0][l][0], tmp[1][0][l][2], tmp[1][0][l][3]))
                f.write("\n")
            f.close()

        tmp = self.getData(csvPath,'fps_window.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var fpslist=%s;
var fpsdata=%s;
"""%(tmp[1][0], tmp[1][1])

        tmp = self.getData(csvPath,'cur_freq.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var curfreqdata=%s;
"""%tmp[1]

        tmp = self.getData(csvPath,'thermal.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var thermaldata=%s;
"""%tmp[1]

        tmp = self.getData(csvPath,'others.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var gpufreqdata=%s;
"""%tmp[1]

        tmp = self.getData(csvPath,'cpus.csv')
        charts_out.append(tmp[0])
        if tmp[0] == 1 :
            js = js + """
var cpusdata=%s;
"""%tmp[1]

        js = "var csvData=%s;"%charts_out + js
        f = codecs.open(r'%s'%jsfile, "w", "utf-8")
        f.write('%s'%js)
        f.close()
        log('Finish: %s'%jsfile)

    def getData(self, csvPath, csvName):
        checkpath = os.path.join(csvPath, csvName)
        out = 0
        data =[]
        if not os.path.exists(checkpath):
            log('There is no %s in %s'%(csvName, csvPath))
        else:
            if len(open(checkpath).readlines()) > 2:
                self.check_csv(checkpath)
                if csvName == 'windows.csv' :
                    data = self.Windows(checkpath)
                elif csvName == 'btm.csv' :
                    data = self.btm(checkpath)
                elif csvName == 'cur_freq.csv' :
                    data = self.curfreq(checkpath)
                elif csvName == 'cpu.csv' :
                    data = self.cpu(checkpath)
                elif csvName == 'cpus.csv' :
                    data = self.cpus(checkpath)
                elif csvName == 'cpuinfo.csv' :
                    data = self.cpuinfo(checkpath)
                elif csvName == 'mem.csv' :
                    data = self.mem(checkpath)
                elif csvName == 'mem2.csv' :
                    data = self.mem2(checkpath)
                elif csvName == 'meminfo.csv' :
                    data = self.meminfo(checkpath)
                elif csvName == 'meminfo2.csv' :
                    data = self.meminfo2(checkpath)
                elif csvName == 'meminfo2.csv' :
                    data = self.meminfo2(checkpath)
                elif csvName == 'fps_window.csv' :
                    data = self.FPS(checkpath)
                    fps_list = []
                    fps_data = []
                    for i in range(len(data)):
                        fps_list.append('%s_%s'%(data[i][0], data[i][1]))
                        fps_data.append(data[i][2])
                    checkpath = os.path.join(csvPath,'fps_system.csv')
                    if len(open(checkpath).readlines()) > 2:
                        data = self.FPS(checkpath)
                        fps_list.append('System')
                        fps_data.append(data[0][2])
                    data = [fps_list, fps_data]
                elif csvName == 'thermal.csv' :
                    data = self.thermal(checkpath)
                elif csvName == 'others.csv' :
                    data = self.gpufreq(checkpath)
                out = 1
            else:
                log('No data in %s'%checkpath)
        return [out, data]

    def check_csv(self, csv):
        with open(csv, 'rb') as fh:
            first = next(fh).decode()
            offs = -100
            while True:
                fh.seek(offs, 2)
                lines = fh.readlines()
                if len(lines)>1:
                    last = lines[-1].decode()
                    break
                offs *=  2
            L_first = len(first.split(','))
            L_last = len(last.split(','))
        if L_last !=  L_first:
            log("Delete the last line of %s"%(csv))
            with open(csv) as f:
                lines = f.readlines()
                curr = lines[:-1]
            f = open(csv, 'w')
            f.writelines(curr)
            f.close()

    def Windows(self, csvPath):
        log('windows.csv')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 'null')
        Time = data['uptime'].values.tolist()
        Date_Time = data['Date_Time'].values.tolist()
        FocusedWindow = data['FocusedWindow'].values.tolist()
        FocusedApplication = data['FocusedApplication'].values.tolist()
        log('windows Finish')
        return [Time, Date_Time, FocusedWindow, FocusedApplication]

    def btm(self, csvPath):
        log('btm.csv')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 'null')
        Time = data['uptime'].values.tolist()
        BatteryLevel = data['BatteryLevel'].tolist()
        Batterytype = data['PlugType'].tolist()
        for i in range(len(BatteryLevel)):
            BatteryLevel[i] = int(BatteryLevel[i])
            Batterytype[i] = int(Batterytype[i])
        log('btm Finish')
        return [Time, BatteryLevel, Batterytype]

    def curfreq(self, csvPath):
        log('cur_freq.csv')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 0)
        Time = data['uptime'].values.tolist()
        cpus = int(data.columns[1].replace('0:',''))
        series = []
        for i in range(1, cpus+1) :
            tmp = data[data.columns[i]].astype('Float64').values.tolist()
            series.append(tmp)
        log('cur_freq Finish')
        return [Time, series]
    
    def cpus(self, csvPath):
        log('cpus.csv')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 0)
        Time = data['uptime'].values.tolist()
        cpus = int(data.columns[-1]) +1
        series = []
        for i in range(1, cpus+2) :
            tmp = data[data.columns[i]].astype('Float64').values.tolist()
            series.append(tmp)
        log('cpus Finish')
        return [Time, series]

    def cpu(self, csvPath):
        log('cpu.csv')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 'null')
        Time = data['uptime'].values.tolist()
        usr = data['usr'].astype('Float64').values.tolist()
        sys = data['sys'].astype('Float64').values.tolist()
        nic = data['nic'].astype('Float64').tolist()
        idle = data['idle'].astype('Float64').values.tolist()
        io = data['io'].astype('Float64').tolist()
        irq = data['irq'].astype('Float64').tolist()
        sirq = data['sirq'].astype('Float64').tolist()
        log('cpu Finish')
        return [Time, usr, sys, nic, idle, io, irq, sirq]

    def cpuinfo(self, csvPath):
        log('cpuinfo.csv')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 'null')
        Command = data['Command'].unique().tolist()
        maxcpu = []
        cpuinfo_data = []
        h = 0
        for c in Command:
            h+= 1
            log('cpuinfo Command: %s'%c)
            data_command = data[data['Command'].values == c]
            Uptime = data_command['uptime'].values.tolist()
            Pid = data_command['PID'].values.tolist()
            CPU = data_command['%CPU'].values.tolist()
            CPU_max = max(CPU)
            ARG = data_command['args'].values.tolist()
            thread = data_command['Thread'].values.tolist()
            tmp = len(Uptime)
            p = 1
            d_pid = [Pid[0]]
            d_times = 0
            for l in range(1,tmp):
                if Uptime[p] == Uptime[p-1]:
                    d_times = d_times+1
                    del Uptime[p]
                    d_pid.append(Pid[p])
                    del Pid[p]
                    if isinstance(CPU[p-1],list) is False and isinstance(CPU[p],list) is False:
                        CPU[p-1] = [round(CPU[p-1]+CPU[p],1),2,d_times]
                    else:
                        CPU[p-1] = [round(CPU[p-1][0]+ CPU[p],1),2,d_times]
                    del CPU[p]
                    del ARG[p]
                    del thread[p]
                else:
                    d_times = 0
                    if Pid[p] !=  Pid[p-1] and Pid[p] not in d_pid:
                        d_pid.append(Pid[p])
                        CPU[p] = [CPU[p],1]
                    p = p+1
            cpuinfo_data.append([Uptime,CPU,ARG,thread])
            maxcpu.append(['%s'%c,h,CPU_max])
        maxcpu.sort(key = lambda a_tuple:a_tuple[2],reverse = True)
        log('cpuinfo Finish')
        return [maxcpu, cpuinfo_data]

    def mem(self, csvPath):
        log('mem.csv')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 'null')
        Time = data[data.columns[0]].values.tolist()
        MemFree = (data['MemFree']/1024).values.tolist()
        Buffers = (data['Buffers']/1024).values.tolist()
        Cached = (data['Cached']/1024).values.tolist()
        Active = (data['Active']/1024).values.tolist()
        Inactive = (data['Inactive']/1024).values.tolist()
        Active_a = (data['Active(anon)']/1024).values.tolist()
        Inactive_a = (data['Inactive(anon)']/1024).values.tolist()
        Active_f = (data['Active(file)']/1024).values.tolist()
        Inactive_f = (data['Inactive(file)']/1024).values.tolist()
        Dirty = (data['Dirty']/1024).values.tolist()
        Writeback = (data['Writeback']/1024).values.tolist()
        Mapped = (data['Mapped']/1024).values.tolist()
        Slab = (data['Slab']/1024).values.tolist()
        IO = ((data['Dirty']+data['Writeback'])/1024).values.tolist()
        if len(data.columns) == 15:
            CMAFree = (data['CMA Free']/1024).values.tolist()
        Free = ((data['MemFree']+data['Buffers']+data['Cached'])/1024).values.tolist()
        for l in range(len(Time)):
            MemFree[l] = round(MemFree[l],2)
            Buffers[l] = round(Buffers[l],2)
            Cached[l] = round(Cached[l],2)
            Active[l] = round(Active[l],2)
            Inactive[l] = round(Inactive[l],2)
            Active_a[l] = round(Active_a[l],2)
            Inactive_a[l] = round(Inactive_a[l],2)
            Active_f[l] = round(Active_f[l],2)
            Inactive_f[l] = round(Inactive_f[l],2)
            Dirty[l] = round(Dirty[l],2)
            Writeback[l] = round(Writeback[l],2)
            Mapped[l] = round(Mapped[l],2)
            Slab[l] = round(Slab[l],2)
            IO[l] = round(IO[l],2)
            if len(data.columns) == 15:
                CMAFree[l] = round(CMAFree[l],2)
            Free[l] = round(Free[l],2)
        if len(data.columns) == 15:
            FreeInfo = [MemFree,Buffers,Cached,CMAFree]
        else:
            FreeInfo = [MemFree,Buffers,Cached]
        log('mem Finish')
        return [Time, Free, FreeInfo, Active, Active_a, Active_f, Inactive, Inactive_a, Inactive_f, IO, Mapped, Slab, Dirty, Writeback]

    def mem2(self, csvPath):
        log('mem2.csv')
        data=pd.read_csv(r'%s'%csvPath,warn_bad_lines=False,error_bad_lines=False).fillna(value=0)
        name=data.columns.tolist()
        del name[0]
        Time=data[data.columns[0]].values.tolist()
        D_mmap=[]
        N_mmap=[]
        D_mmap_other=[]
        N_mmap_other=[]
        for j in range(1,len(name)+1):
            if name[j-1].find('_mmap') < 0 :
                N_mmap_other.append(name[j-1])
                D_mmap_other.append((data[data.columns[j]]/1024).values.tolist())
            else:
                N_mmap.append(name[j-1])
                D_mmap.append((data[data.columns[j]]/1024).values.tolist())
        for k in range(len(D_mmap)):
            for l in range(len(D_mmap[k])):
                D_mmap[k][l]=round(D_mmap[k][l],2)
        for k in range(len(D_mmap_other)):
            for l in range(len(D_mmap_other[k])):
                D_mmap_other[k][l]=round(D_mmap_other[k][l],2)
        log('mem2 Finish')
        return [Time, N_mmap, D_mmap, N_mmap_other, D_mmap_other]

    def meminfo(self, csvPath):
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 'null')
        log('meminfo.csv')
        fd_type = len(data.columns)
        Command = data['Process_Name'].unique().tolist()
        maxpd = []
        meminfo_data = []
        h = 0
        for c in Command:
            data_command = data[data['Process_Name'].values == c]
            Time = data_command['uptime'].values.tolist()
            Pid = data_command['PID'].values.tolist()
            Pss = (data_command['Pss']/1024).values.tolist()
            tmp = (data_command[data_command['Pss'].values > 0]['Pss']/1024).values.tolist()
            if len(tmp) > 0:
                Pss_max = max(tmp)
                Pss_min = min(tmp)
            else:
                Pss_max = 0
                Pss_min = 0
            ARG = data_command['Args'].values.tolist()
            FD = []
            if data_command['Native_Heap(Size)'].head(1).values[0] == 'null' or int(data_command['Native_Heap(Size)'].head(1).values[0]) == 0:
                meminfo_type = 0
            else:
                meminfo_type = 1
                NHS = (data_command['Native_Heap(Size)'].replace('null',0)/1024).values.tolist()
                NHA = (data_command['Native_Heap(Alloc)'].replace('null',0)/1024).values.tolist()
                NHF = (data_command['Native_Heap(Free)'].replace('null',0)/1024).values.tolist()
                DHP = (data_command['Dalvik_Pss'].replace('null',0)/1024).values.tolist()
                DHS = (data_command['Dalvik_Heap(Size)'].replace('null',0)/1024).values.tolist()
                DHA = (data_command['Dalvik_Heap(Alloc)'].replace('null',0)/1024).values.tolist()
                DHF = (data_command['Dalvik_Heap(Free)'].replace('null',0)/1024).values.tolist()
                Views = data_command['Views'].replace('null',0).tolist()
                Threads = data_command['Threads'].replace('null',0).tolist()
                if fd_type == 15 :
                    FD = data_command['FD'].replace('null',0).tolist()
            Time[0] = round(Time[0],2)
            Pss[0] = round(Pss[0],2)
            if meminfo_type == 1:
                NHS[0] = round(NHS[0],2)
                NHA[0] = round(NHA[0],2)
                NHF[0] = round(NHF[0],2)
                DHP[0] = round(DHP[0],2)
                DHS[0] = round(DHS[0],2)
                DHA[0] = round(DHA[0],2)
                DHF[0] = round(DHF[0],2)
                Views[0] = int(Views[0])
                Threads[0] = int(Threads[0])

            p = 1
            d_pid = [Pid[0]]
            d_times = 0
            for l in range(1,len(Time)):
                Time[p] = round(Time[p],2)
                Pss[p] = round(Pss[p],2)
                if meminfo_type == 1:
                    NHS[p] = round(NHS[p],2)
                    NHA[p] = round(NHA[p],2)
                    NHF[p] = round(NHF[p],2)
                    DHP[p] = round(DHP[p],2)
                    DHS[p] = round(DHS[p],2)
                    DHA[p] = round(DHA[p],2)
                    DHF[p] = round(DHF[p],2)
                    Views[p] = int(Views[p])
                    Threads[p] = int(Threads[p])
                if Time[p] == Time[p-1]:
                    d_pid.append(Pid[p])
                    d_times = d_times+1
                    if isinstance(Pss[p-1],list) is False:
                        Pss[p-1] = [round(Pss[p-1]+Pss[p],2),2,d_times]
                    else:
                        Pss[p-1] = [round(Pss[p-1][0]+Pss[p],2),2,d_times]
                    del Pss[p]
                    if meminfo_type == 1:
                        NHS[p-1] = round(NHS[p-1]+NHS[p],2)
                        NHA[p-1] = round(NHA[p-1]+NHA[p],2)
                        NHF[p-1] = round(NHF[p-1]+NHF[p],2)
                        DHP[p-1] = round(DHP[p-1]+DHP[p],2)
                        DHS[p-1] = round(DHS[p-1]+DHS[p],2)
                        DHA[p-1] = round(DHA[p-1]+DHA[p],2)
                        DHF[p-1] = round(DHF[p-1]+DHF[p],2)
                        Views[p-1] = round(Views[p-1]+Views[p],2)
                        Threads[p-1] = round(Threads[p-1]+Threads[p],2)
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
                    if Pid[p] !=  Pid[p-1] and Pid[p] not in d_pid:
                        d_pid.append(Pid[p])
                        Pss[p] = [Pss[p],1]
                    p += 1
            if meminfo_type == 0:
                meminfo_data.append([meminfo_type,Time,ARG,Pss,FD])
            else:
                meminfo_data.append([meminfo_type,Time,ARG,Pss,Views,Threads,NHS,NHA,NHF,DHP,DHS,DHA,DHF,FD])
            maxpd.append(['%s'%c,h,round((Pss_max-Pss_min)*1.0,2),round(Pss_max*1.0,2)])
            h += 1
        maxpd.sort(key = lambda a_tuple:a_tuple[2],reverse = True)
        log('meminfo Finish')
        return [maxpd, meminfo_data]

    def meminfo2(self, csvPath):
        log('meminfo2.csv')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 'null')
        Command = data['COMMAND'].unique().tolist()
        maxpd = []
        meminfo_data = []
        h = 0
        for c in Command:
            data_command = data[data['COMMAND'].values==c]
            Time = data_command['uptime'].values.tolist()
            Pid = data_command['PID'].values.tolist()
            VSZ = data_command['VSZ'].values.tolist()
            RSS = data_command['RSS'].values.tolist()
            tmp = data_command[data_command['VSZ'].values > 0]['VSZ'].values.tolist()
            if len(tmp) > 0:
                VSZ_max = max(tmp)
                VSZ_min = min(tmp)
            else:
                VSZ_max = 0
                VSZ_min = 0
            ARG = data_command['Args'].values.tolist()

            p = 1
            d_pid = [Pid[0]]
            d_times = 0
            for l in range(1,len(Time)):
                Time[p] = round(Time[p],2)
                VSZ[p] = round(VSZ[p],3)
                RSS[p] = round(RSS[p],3)
                if Time[p] == Time[p-1]:
                    d_pid.append(Pid[p])
                    d_times = d_times+1
                    if isinstance(VSZ[p-1],list) is False:
                        VSZ[p-1] = [round(VSZ[p-1]+VSZ[p],3),2,d_times]
                    else:
                        VSZ[p-1] = [round(VSZ[p-1][0]+VSZ[p],3),2,d_times]
                    RSS[p-1] = round(RSS[p-1]+RSS[p],3)
                    del VSZ[p]
                    del RSS[p]
                    del Pid[p]
                    del Time[p]
                    del ARG[p]
                else:
                    if Pid[p] !=  Pid[p-1] and Pid[p] not in d_pid:
                        d_pid.append(Pid[p])
                        VSZ[p] = [VSZ[p],1]
                    p = p+1
            meminfo_data.append([Time,ARG,VSZ,RSS])
            maxpd.append(['%s'%c,h,round(VSZ_max-VSZ_min,3),round(VSZ_max,3)])
            h += 1
        maxpd.sort(key = lambda a_tuple:a_tuple[2],reverse = True)
        log('meminfo2 Finish')
        return [maxpd, meminfo_data]

    def FPS(self, csvPath):
        log('FPS Start')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 'null')
        WN = data['WN'].max()
        if os.path.basename(r'%s'%csvPath) == 'fps_system.csv' :
            t_window = 'System'
        else:
            str = data.columns[2].replace('Date:','').split('/')
            t_window = str[-1]
        serias = []
        for i in range(1,WN+1):
            data = data[data['WN']==i]
            D_FU = data['FU(s)'].values.tolist()
            D_LU = data['LU(s)'].values.tolist()
            D_Date = data[data.columns[2]].values.tolist()
            D_FPS = data[data.columns[3]].values.tolist()
            D_Frames = data['Frames'].tolist()
            D_jank = data['jank'].tolist()
            D_jank_percent = (data['jank']/data['Frames']*100).tolist()
            D_MFS = data['MFS(ms)'].tolist()
            D_OKT = data[data.columns[8]].tolist()
            D_OKT_percent = (data[data.columns[8]]/data['Frames']*100).tolist()
            D_SS = data['SS(%)'].values.tolist()
            if sum(D_Frames) > 0 :
                D_OKTF = sum(D_OKT)*1.00/sum(D_Frames)*100
            else:
                D_OKTF = 0
            for l in range(len(D_FU)):
                D_FU[l] = round(D_FU[l],3)
                D_LU[l] = round(D_LU[l],3)
                D_jank_percent[l] = round(D_jank_percent[l],1)
                D_OKT_percent[l] = round(D_OKT_percent[l],1)
                D_Frames[l] = int(D_Frames[l])
                D_jank[l] = int(D_jank[l])
                D_MFS[l] = int(D_MFS[l])
                D_OKT[l] = int(D_OKT[l])
            serias.append([t_window,i,[D_FU,D_LU,D_Date,D_FPS,D_Frames,D_jank,D_MFS,D_OKT,D_SS,D_OKT_percent,D_jank_percent]])
        log('FPS Finish')
        return serias

    def thermal(self, csvPath):
        log('thermal Start')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 0)
        name = data.columns.tolist()
        del name[0]
        Time = data['uptime'].values.tolist()
        thermalData = []
        for i in range(len(name)):
            D = data[data.columns[i+1]].tolist()
            for j in range(len(D)):
                D[j] = int(D[j])
            thermalData.append(D)
        log('thermal Finish')
        return [Time, name, thermalData]

    def gpufreq(self, csvPath):
        log('gpu Start')
        data = pd.read_csv(r'%s'%csvPath, warn_bad_lines=False, error_bad_lines=False, low_memory=False).fillna(value = 0)
        Time = data['uptime'].values.tolist()
        gpu_freq = data['gpu_freq'].tolist()
        if 'gpu' in data.columns:
            check = 1
            gpu = data['gpu'].astype('Float64').tolist()
        else:
            check = 0
        for i in range(len(gpu_freq)):
            gpu_freq[i] = int(gpu_freq[i])
        log('gpu Finish')
        if check == 0:
            return [Time, gpu_freq]
        else:
            return [Time, gpu_freq, gpu]



if __name__ == '__main__':
    results = findPath('%s'%sys.argv[1], "meminfo.csv")
    DATA_Path = sys.argv[1]
    dataPath = os.path.join(DATA_Path,'data')

    import shutil
    if os.path.exists(dataPath) :
        try:
            shutil.rmtree(dataPath)
        except os.error as err:
            time.sleep(0.5)
            try:
                shutil.rmtree(dataPath)
            except os.error as err:
                log("Delete data Error!!!")
    copyFiles(os.path.join(os.path.dirname(os.path.realpath(sys.argv[0])), 'monitor_HTML'), DATA_Path)
    if not os.path.exists(dataPath) :
        os.mkdir(dataPath)

    outjs = monitor()
    if len(results) > 0 :
        writepath = os.path.join(dataPath,'maxCPU.csv')
        f=open(writepath,'w')
        f.write('Path,Command,CPU')
        f.write("\n")
        f.close()

        writepath = os.path.join(dataPath,'maxPSS.csv')
        f=open(writepath,'w')
        f.write('Path,Command,Pss Difference(M),Pss(M)')
        f.write("\n")
        f.close()

        writepath = os.path.join(dataPath,'maxVSS.csv')
        f=open(writepath,'w')
        f.write('Path,Command,VSS Difference(M),VSS(M)')
        f.write("\n")
        f.close()

        caselist = []
        monitorlist = []
        case = ""

        for Path in results :
            name = os.path.split(Path)
            tmp = os.path.split(name[-2])
            if case == "" :
                case = tmp[-1]
                monitorlist = [name[-1]]
            else:
                if case == tmp[-1] :
                    monitorlist.append(name[-1])
                else:
                    c = 0
                    for i in range(len(caselist)) :
                        if caselist[i][0] == case :
                            caselist[i][1].extend(monitorlist)
                            caselist[i][1].sort(reverse = True)
                            c = 1
                            break
                    if c == 0 :
                        monitorlist.sort(reverse = True)
                        caselist.append([case, monitorlist])
                    case = tmp[-1]
                    monitorlist = [name[-1]]
            log('Start outjs: %s_%s.js'%(tmp[-1], name[-1]))
            writepath = os.path.join(dataPath, '%s_%s.js'%(tmp[-1], name[-1]))
            outjs.main(Path, writepath)
        c = 0
        for i in range(len(caselist)) :
            if caselist[i][0] == case :
                caselist[i][1].extend(monitorlist)
                caselist[i][1].sort(reverse = True)
                c = 1
                break
        if c == 0 :
            monitorlist.sort(reverse = True)
            caselist.append([case, monitorlist])
        caselist.sort(key = lambda a_tuple:a_tuple[0],reverse = False)
        js="var caselist=%s"%caselist
        writepath = os.path.join(dataPath,'list.js')
        f = codecs.open(writepath, "w", "utf-8")
        f.write('%s'%js)
        f.close()
        log('Finish: list.js')
    else:
        log ('Not Found monitor csv files.')


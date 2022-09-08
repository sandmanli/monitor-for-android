#!/system/bin/sh
if [ -f /data/local/tmp/busybox ];then
	export bb="/data/local/tmp/busybox"
else
	echo "No /data/local/tmp/busybox"
	exit
fi
#root
root=`id|$bb grep -c root`

getwindow(){
	dumpsys input|$bb grep " name="|$bb awk -v OFS="," -v loop=$loop -v time=$uptime -v date="$date_time" -v csv="$monitor/windows.csv" '{ \
		if($1~/displayId/){ \
			if($2~/ActivityRecord/)A[substr($1,11,length($1)-11)]=$4 \
		}else{ \
			if($2~"SurfaceView")W="SurfaceView-"substr($4,1,length($4)-2);else W=substr($4,1,length($4)-3); \
			if($10=="visible=true,"){ \
				D=substr($5,11,length($5)-11); \
				for(i=12;i<=NF;i++){ \
					if($i~"flags")F=substr($i,7,length($i)-7); \
					if($i~"type")T=substr($i,6,length($i)-6); \
					if($i~"frame"){ \
						S=substr($i,7,length($i)-7); \
						gsub("\]","",S); \
						gsub("\\[",",",S) \
					}; \
					if($i~"ownerPid")P=substr($i,10,length($i)-10); \
					if($i~"ownerUid")U=substr($i,10,length($i)-10) \
				}; \
				if($8=="hasFocus=true,")print loop,time,date,D,W,A[D],F,T,P,U,"\""S"\"" >>csv \
			} \
		} \
	}'
}

get_package(){
if [ ! -z "$packages" ];then
	local grep_str="`echo $packages|$bb sed 's/\./\\\\./g;s/\[/\\\[/g;s/\]/\\\]/g'`"
	local tmp="`$bb ps -o pid,args`"
	local check="`echo "$tmp"|$bb sed 's/{.*.} //g'|$bb grep -E "$grep_str"`"
	if [ ! -z "$check" ];then
		local tmp="`$bb ps -T`"
		local check1="`echo "$tmp"|$bb grep -E -c "$grep_str"`"
		if [ $threads -lt $check1 ];then
			threads=$check1
			echo "$tmp"|$bb grep -E "$grep_str" >$monitor/threads/$loop"_"$check1.log
		fi
		local i=0
		echo "$packages"|$bb sed 's/|/\n/g'|while read p;do
			local Ts="`$bb ps -T|$bb awk -v package="$p" '$NF==package{r+=1}END{print r+0}'`"
			local FD=-1
			echo "$check"|$bb awk -v package="$p" '{if($2==package){t+=1;D[$1" "$2]=t}}END{for(i in D)print i" "D[i]}'|while read l;do
				local pid="`echo $l|$bb awk '{print $1}'`"
				if [ -f /proc/$pid/cmdline ];then
					if [ $root -eq 1 ];then
						local FD="`ls -l /proc/$pid/fd/ 2>/dev/null|$bb awk 'END{print NR}'`"
						if [ $i -eq 0 ];then
							local i=1
							if [ -f $monitor/FDs/maxFDS.log ];then
								local FDs="`$bb awk -F, -v p="$p" '$1==p{r=$2}END{printf r+0}' $monitor/FDs/maxFDS.log`"
							else
								local FDs=0
							fi
							if [ $FDs -lt $FD ];then
								if [ $FDs -eq 0 ];then
									echo "$p,$FD,$pid" >>$monitor/FDs/maxFDS.log
								else
									local check="`cat $monitor/FDs/maxFDS.log`"
									echo "$check"|$bb awk -F, -v p="$p" -v r="$p,$FD,$pid" '{if($1==p)print r;else print $0}' >$monitor/FDs/maxFDS.log
								fi
								ls -l /proc/$pid/fd/ 1>$monitor/FDs/$pid"_"$loop"_"$FD.log 2>/dev/null
							fi
						fi
					fi
					local arg="`$bb awk 'BEGIN{r="null"}{if(NR>1){if(NR==2)r=$0;else r=r" "$0}}END{print r}' /proc/$pid/cmdline`"
					if [ -z "`echo $arg|$bb tr -d " "`" ];then
						local arg="null"
					fi
					command="`echo $l|$bb awk '{print $2}'`"
					if [ -d /proc/$pid ];then
						local pss="`dumpsys meminfo $pid|$bb awk -v pid=$pid -v comm=$command -v time=$uptime '{if($1=="**")comm=substr($6,2,length($6)-2);if($1=="Native"&&$2=="Heap"){n=$(NF-2);o=$(NF-1);p=$NF};if($1=="Dalvik"&&$2=="Heap"){d=$(NF-2);e=$(NF-1);f=$NF};if($1=="Dalvik"&&$2=="Other")g=$3;if($1=="TOTAL"&&NF==9)s=$2;if($1=="Views:"){v=$2;print time","comm","s","pid","n+0","o+0","p+0","d+0","e+0","f+0","g+0","v+0}}'`"
						if [ ! -z "$pss" -a $Ts -gt 0 ];then
							if [ $root -eq 1 ];then
								echo "$pss,$Ts,$FD,\"$arg\""
							else
								echo "$pss,$Ts,\"$arg\""
							fi
						fi
					fi
				fi
			done
		done
	fi
fi
}

get_meminfo(){
if [ ! -f $monitor/mem2.csv ];then
	echo uptime,$mem2 >$monitor/mem2.csv
fi
if [ -z $packages ];then
	local check="busybox"
else
	local check="busybox|$packages"
fi
dumpsys meminfo |$bb awk -v time=$uptime -v packages="$check" -v mem="$mem2" -v OFS=, -v csv=$monitor/mem2.csv -v csv1=$monitor/meminfo.csv 'BEGIN{ \
	l=split(mem,O,","); \
	state=0; \
	mem="" \
} \
{ \
	if($0=="")state=0; \
	gsub(/\(|\)|Total PSS by |,/,"",$0); \
	if(state!=0||$2=="RAM:"||$1=="ZRAM:"){ \
		gsub(/K: /," kB: ",$0); \
	}; \
	if(state==1){ \
		gsub(/ Services/,"_Services",$0); \
		if($3!~packages&&$1+0!=0&&$5+0!=0)print time","$3","$1","$5",,,,,,,,,,," >>csv1 \
	}else{ \
		if(state==2){ \
			C=$3; \
			if(NF>3)for(i=4;i<=NF;i++)C=C"_"$i; \
			D[C]=$1 \
		} \
	}; \
	if($2=="RAM:"){ \
		if($1=="Total"){ \
			D["Total_RAM"]=substr($3,1,length($3)-1) \
		}else{ \
			if($1=="Free"){ \
				D["Free_RAM"]=substr($3,1,length($3)-1); \
				D["Free_cached_pss"]=substr($4,1,length($4)-1); \
				D["Free_cached_kernel"]=substr($8,1,length($8)-1); \
				D["free"]=substr($12,1,length($12)-1) \
			}else{ \
				if($1=="Used"){ \
					D["Used_RAM"]=substr($3,1,length($3)-1); \
					D["used_pss"]=substr($4,1,length($4)-1); \
					D["used_kernel"]=substr($8,1,length($8)-1) \
				}else{ \
					if($1=="Lost")D["Lost_RAM"]=substr($3,1,length($3)-1) \
				} \
			} \
		} \
	}; \
	if($1=="ZRAM:"){ \
		D["swap_physical_used"]=substr($2,1,length($2)-1); \
		D["swap_for"]=substr($6,1,length($6)-1); \
		D["swap_total"]=substr($9,1,length($9)-1) \
	}; \
	if($1=="ION:")D["ION"]=substr($2,1,length($2)-1); \
	if($1=="process:"){state=1}else{ \
		if($1=="category:")state=2 \
	} \
}END{ \
	R=D[O[1]]; \
	for(i=2;i<=l;i++)R=R","D[O[i]]; \
	print time,R >>csv \
}' 2>/dev/null
}

getmem(){
local info="`$bb awk -v OFS=","  'BEGIN{ \
	r=0 \
}{ \
	if($1=="MemFree:")a=$2; \
	if($1=="Buffers:")b=$2; \
	if($1=="Cached:")c=$2; \
	if($1=="MemAvailable:")d=$2; \
	if($1=="Active:")e=$2; \
	if($1=="Inactive:")f=$2; \
	if($1=="Active(anon):")g=$2; \
	if($1=="Inactive(anon):")h=$2; \
	if($1=="Active(file):")i=$2; \
	if($1=="Inactive(file):")j=$2; \
	if($1=="Dirty:")k=$2; \
	if($1=="Writeback:")l=$2; \
	if($1=="Mapped:")m=$2; \
	if($1=="Slab:")n=$2 \
}END{ \
	print a,b,c,d,e,f,g,h,i,j,k,l,m,n \
}' /proc/meminfo`"
if [ ! -z "$info" ];then
	echo "$uptime,$info" >>$monitor/mem.csv
fi
}

getvss(){
$bb ps -o pid,ppid,vsz,rss,args|$bb sed 's/{.*.} //g'|$bb awk -v OFS="," -v time=$uptime -v csv="$monitor/meminfo2.csv" 'NR>1&&$5!="/data/local/tmp/busybox"{gsub(/\{.*.\} /,"",$0);if(substr($3,length($3),1)=="m"){V=substr($3,1,length($3)-1)}else{if(substr($3,length($3),1)=="g")V=substr($3,1,length($3)-1)*1024;else V=sprintf("%.3f",$3/1024)+0};if(substr($4,length($4),1)=="m"){R=substr($4,1,length($4)-1)}else{if(substr($4,length($4),1)=="g")R=substr($4,1,length($4)-1)*1024;else R=sprintf("%.3f",$4/1024)+0};C=$5;A="";if(NF>=6)A=$6;if(NF>6){for(i=7;i<=NF;i++)A=A" "$i};if(A=="")A="null";if(V>0)print time,$1,$2,V,R,C,"\""A"\"">>csv}'
}

getcpu(){
$bb top -b -n 1|$bb grep -E -v "busybox|Shutdown thread"|$bb awk -v time="$uptime" -v csv="$monitor/cpu.csv" -v csv2="$monitor/cpuinfo.csv" '{ \
	gsub("%","",$0); \
	gsub("\.0 "," ",$0); \
	if(NR==2) print time","$2","$4","$6","$8","$10","$12","$14 >>csv; \
	if(NR>4){ \
		c=""; \
		a=""; \
		t=""; \
		if($8+0==0)exit; \
		if(NF==9)c=$9; \
		if(NF>9){ \
			if(substr($9,1,1)=="\{"){ \
				t=$9; \
				c=$10; \
				if(NF>10)for(i=11;i<=NF;i++)a=a" "$i \
			}else{ \
				c=$9; \
				if(NF>9)for(i=10;i<=NF;i++)a=a" "$i \
			} \
		}; \
		print time","$1","$8+0","c",\""a"\","t >>csv2 \
	}}'
}

getCPU(){
if [ "${cpuTime}a" != "a" ];then
	cpuTime="`$bb awk '$1~"cpu"{printf $2" "$3" "$4" "$5" "$6" "$7" "$8" "}' /proc/stat`"
	$bb sleep 1
fi
$bb awk -v time="$uptime" -v csv="$monitor/cpus.csv" -v cpu="$cpuTime" 'BEGIN{split(cpu,D," ")}{if($1~"cpu"){if(i=="")i=0;else i+=1;sum=$2-D[1+7*i]+$3-D[2+7*i]+$4-D[3+7*i]+$5-D[4+7*i]+$6-D[5+7*i]+$7-D[6+7*i]+$8-D[7+7*i];R=R","sprintf("%.2f",100-($5-D[4+7*i])*100/sum)+0}}END{print time R>>csv}' /proc/stat
cpuTime="`$bb awk '$1~"cpu"{printf $2" "$3" "$4" "$5" "$6" "$7" "$8" "}' /proc/stat`"
}

getFPS(){
local KPI=100
echo "FU(s),LU(s),Date:$1,FPS:$2,Frames,jank,jank2,MFS(ms),OKT:$KPI,SS(%),WN" >$monitor/fps_window.csv
echo "FU(s),LU(s),Date:$1,FPS:$2,Frames,jank,jank2,MFS(ms),OKT:$KPI,SS(%),WN" >$monitor/fps_system.csv
while true;do
	dumpsys SurfaceFlinger --latency-clear
	if [ -f /data/local/tmp/stop ];then
		break
	fi
	$bb usleep 1600000
	local uptime="`echo $EPOCHREALTIME|$bb awk -F. '{print strftime("%F %T",$1+8*3600)"."substr($2,1,3)}'`"
	dumpsys SurfaceFlinger --latency "$1"|$bb awk -v T="$uptime" -v target=$2 -v kpi=$KPI '{if(NR==1){r=$1/1000000;if(r<0)r=$1/1000;b=0;n=0;w=1}else{if(n>0&&$0=="")O=1;if(NF==3&&$2!=0&&$2!=9223372036854775807){x=($3-$1)/1000000/r;if(b==0){b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}else{c=($2-b)/1000000;if(c>500){O=1}else{n+=1;if(c>=r){C+=c;if(c>kpi)o+=1;if(c>=m)m=c;if(x>1)d+=1;if(x>2)D+=1;b=$2}else{C+=r;b=sprintf("%.0f",b+r*1000000)}}};if(n==1)s=sprintf("%.3f",$2/1000000000)};if(n>0&&O==1){O=0;if(n==1)t=sprintf("%.3f",s+C/1000);else t=sprintf("%.3f",b/1000000000);f=sprintf("%.2f",n*1000/C);m=sprintf("%.0f",m);g=f/target;if(g>1)g=1;h=kpi/m;if(h>1)h=1;e=sprintf("%.2f",g*60+h*20+(1-o/n)*20);print s","t","T","f+0","n","d","D","m","o","e","w;n=0;if($0==""){b=0;w+=1}else{b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}}}}' >>$monitor/fps_window.csv
	dumpsys SurfaceFlinger --latency |$bb awk -v T="$uptime" -v target=$2 -v kpi=$KPI '{if(NR==1){r=$1/1000000;if(r<0)r=$1/1000;b=0;n=0;w=1}else{if(n>0&&$0=="")O=1;if(NF==3&&$2!=0&&$2!=9223372036854775807){x=($3-$1)/1000000/r;if(b==0){b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}else{c=($2-b)/1000000;if(c>500){O=1}else{n+=1;if(c>=r){C+=c;if(c>kpi)o+=1;if(c>=m)m=c;if(x>1)d+=1;if(x>2)D+=1;b=$2}else{C+=r;b=sprintf("%.0f",b+r*1000000)}}};if(n==1)s=sprintf("%.3f",$2/1000000000)};if(n>0&&O==1){O=0;if(n==1)t=sprintf("%.3f",s+C/1000);else t=sprintf("%.3f",b/1000000000);f=sprintf("%.2f",n*1000/C);m=sprintf("%.0f",m);g=f/target;if(g>1)g=1;h=kpi/m;if(h>1)h=1;e=sprintf("%.2f",g*60+h*20+(1-o/n)*20);print s","t","T","f+0","n","d","D","m","o","e","w;n=0;if($0==""){b=0;w+=1}else{b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}}}}' >>$monitor/fps_system.csv
done
}

#main
${testresult="/data/local/tmp/"} 2>/dev/null
monitor="$testresult/$1"
if [ -d $monitor ];then
	$bb rm -r $monitor
fi
mkdir -p $monitor/threads
threads=0
if [ -f /data/local/tmp/stop ];then
	$bb rm /data/local/tmp/stop
fi
packages=$3
loop=0
#info
$bb cat /proc/cpuinfo >$monitor/cpuinfo.txt
echo PID=$$ >$monitor/info.log
echo sleep=$4 >>$monitor/info.log
echo build="`getprop ro.build.fingerprint`" >>$monitor/info.log
echo time="`echo $EPOCHREALTIME|$bb awk -F. '{print strftime("%F %T",$1+8*3600)"."$2}'`" >>$monitor/info.log
echo uptime="`$bb awk -F. '{print $1}' /proc/uptime`" >>$monitor/info.log

#csv
echo "uptime,usr,sys,nic,idle,io,irq,sirq" >$monitor/cpu.csv
echo "uptime,PID,%CPU,Command,args,Thread" >$monitor/cpuinfo.csv
echo "uptime:$4,MemFree,Buffers,Cached,MemAvailable,Active,Inactive,Active(anon),Inactive(anon),Active(file),Inactive(file),Dirty,Writeback,Mapped,Slab" >$monitor/mem.csv

if [ $root -eq 1 ];then
	mkdir -p $monitor/FDs
	echo "uptime,Process_Name,Pss,PID,Native_Heap(Size),Native_Heap(Alloc),Native_Heap(Free),Dalvik_Heap(Size),Dalvik_Heap(Alloc),Dalvik_Heap(Free),Dalvik_Other,Views,Threads,FD,Args" >$monitor/meminfo.csv
else
	echo "uptime,Process_Name,Pss,PID,Native_Heap(Size),Native_Heap(Alloc),Native_Heap(Free),Dalvik_Heap(Size),Dalvik_Heap(Alloc),Dalvik_Heap(Free),Dalvik_Other,Views,Threads,Args" >$monitor/meminfo.csv
fi
echo "uptime,PID,PPID,VSZ,RSS,COMMAND,Args" >$monitor/meminfo2.csv
echo "Loop:$4,uptime,Date_Time,DisplayID,FocusedWindow,FocusedActivity,Flags,Type,Pid,uid,frame" >$monitor/windows.csv

CPUS="`$bb awk -v csv="$monitor/cur_freq.csv" -v csv1="$monitor/cpus.csv" '{if(FNR==1)cpu+=1}END{R="uptime,0:"cpu;R1="uptime,cpu,0";for(i=1;i<cpu;i++){R=R","i;R1=R1","i};print R>csv;print R1>>csv1;print cpu}' /sys/devices/system/cpu/cpu*/uevent`"
if [ $5 -ge 1 ];then
	mem2="`dumpsys meminfo |$bb awk '{if($0=="")state=0;gsub(/K: /," kB: ",$0);if(state==2){C=$3;if(NF>3){for(i=4;i<=NF;i++)C=C"_"$i;if(R=="")R=C;else R=R","C}};if($2=="RAM:"){if($1=="Total")R=R",Total_RAM";else {if($1=="Free")R=R",Free_RAM,Free_cached_pss,Free_cached_kernel,free";else {if($1=="Used")R=R",Used_RAM,used_pss,used_kernel";else {if($1=="Lost")R=R",Lost_RAM"}}}};if($1=="ZRAM:"){R=R",swap_physical_used,swap_for,swap_total"};if($1=="ION:")R=R",ION";if($NF=="category:")state=2}END{print R}'`"
fi


#FPS
if [ ! -z "$2" ];then
	getFPS "$2" 60 &
fi

uptime="`$bb awk '{print $1}' /proc/uptime`"
getCPU
while true;do
	date_time="`echo $EPOCHREALTIME|$bb awk -F. '{print strftime("%F %T",$1+8*3600)"."substr($2,1,3)}'`"
	uptime="`$bb awk '{print $1}' /proc/uptime`"
	#windows.csv
	getwindow
	#cpu
	getCPU
	getcpu
	getmem
	getvss
	if [ $5 -ge 1 ];then
		get_meminfo
	fi
	get_package >>$monitor/meminfo.csv
	#stop
	loop=$((loop+1))
	if [ -f /data/local/tmp/stop ];then
		echo "Found stop file!!!"
		wait
		break
	fi
	if [ $4 -gt 0 ];then
		$bb sleep $4
	fi
done
 
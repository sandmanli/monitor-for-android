#!/system/bin/sh
if [ -f /data/local/tmp/busybox ];then
	export bb="/data/local/tmp/busybox"
else
	echo "No /data/local/tmp/busybox"
	exit
fi
#root
root=`id|$bb grep -c root`

get_package(){
if [ ! -z "$packages" ];then
	local grep_str=`echo $packages|$bb sed 's/\./\\\\./g;s/\[/\\\[/g;s/\]/\\\]/g'`
	local tmp=`$bb ps -o pid,args`
	local check=`echo "$tmp"|$bb sed 's/{.*.} //g'|$bb grep -E "$grep_str"`
	if [ ! -z "$check" ];then
		local tmp=`$bb ps -T`
		local check1=`echo "$tmp"|$bb grep -E -c "$grep_str"`
		if [ $threads -lt $check1 ];then
			threads=$check1
			echo "$tmp"|$bb grep -E "$grep_str" >$monitor/threads/$loop"_"$check1.log
		fi
		local i=0
		echo "$packages"|$bb sed 's/|/\n/g'|while read p;do
			local Ts=`$bb ps -T|$bb awk -v package="$p" '$NF==package{r+=1}END{print r}'`
			local FD=-1
			echo "$check"|$bb awk -v package="$p" '{if($2==package){t+=1;D[$1" "$2]=t}}END{for(i in D)print i" "D[i]}'|while read l;do
				local pid=`echo $l|$bb awk '{print $1}'`
				if [ -f /proc/$pid/cmdline ];then
					if [ $root -eq 1 -a ! -z "$pid" ];then
						local FD=`ls -l /proc/$pid/exe /proc/$pid/root /proc/$pid/fd/ 2>/dev/null|$bb awk 'END{print NR}'`
						if [ $i -eq 0 ];then
							local i=1
							if [ -f $monitor/FDs/maxFDS.log ];then
								local FDs=`$bb awk -F, -v p="$p" '$1==p{r=$2}END{printf r+0}' $monitor/FDs/maxFDS.log`
							else
								local FDs=0
							fi
							if [ $FDs -lt $FD ];then
								if [ $FDs -eq 0 ];then
									echo "$p,$FD,$pid" >>$monitor/FDs/maxFDS.log
								else
									local check=`cat $monitor/FDs/maxFDS.log`
									echo "$check"|$bb awk -F, -v p="$p" -v r="$p,$FD,$pid" '{if($1==p)print r;else print $0}' >$monitor/FDs/maxFDS.log
								fi
								ls -l /proc/$pid/fd/ 1>$monitor/FDs/$pid"_"$loop"_"$FD.log 2>/dev/null
							fi
						fi
						#showmap
						if [ $1 -eq 2 ];then
							if [ $((loop%showmap)) -eq 0 ];then
								if [ -f /system/bin/showmap -o -f /system/xbin/showmap ];then
									showmap $pid |$bb awk -v OFS=, -v p="$pid" -v time=$uptime -v csv="$monitor/showmap.csv" '{if(NR==2){if($0~/swap/){o=10;s=78}else{o=9;s=69}};if($0!~/virtual|size|--------/){C=$o;if(NF>o)C=substr($0,s);print time,p,$1,$2,$3,$4,$5,$6,$7,$(o-1),C>>csv}}'
								else
									$bb awk -v OFS=, -v p="$pid" -v time=$uptime -v csv="$monitor/showmap.csv" '{if(NF==3){o+=1;if(o<=7){if(o==1)Size[C]+=$2;else{if(o==2)Rss[C]+=$2;else{if(o==3)Pss[C]+=$2;else{if(o==4)SC[C]+=$2;else{if(o==5)SD[C]+=$2;else{if(o==6)PC[C]+=$2;else{if(o==7)PD[C]+=$2;}}}}}}}}else{o=0;if(n==1||NR==1){n=0;if(NF==5){C="[anon]"}else{C=$6;if(NF>6)C=substr($0,39+length($1)+length($2)+length($3)+length($4)+length($5))};N[C]+=1};if($1=="VmFlags:")n=1}}END{for(i in N){print time,p,Size[i],Rss[i],Pss[i],SC[i],SD[i],PC[i],PD[i],N[i],i >>csv;T1+=Size[i];T2+=Rss[i];T3+=Pss[i];T4+=SC[i];T5+=SD[i];T6+=PC[i];T7+=PD[i];T8+=N[i]};if(T1+0>0)print time,p,T1,T2,T3,T4,T5,T6,T7,T8,"TOTAL" >>csv}' /proc/2062/smaps
								fi
							fi
						fi
					fi
					local arg=`$bb awk 'BEGIN{r="null"}{if(NR>1){if(NR==2)r=$0;else r=r" "$0}}END{print r}' /proc/$pid/cmdline`
					if [ -z "`echo $arg|$bb tr -d " "`" ];then
						local arg="null"
					fi
					command=`echo $l|$bb awk '{print $2}'`
					if [ -d /proc/$pid ];then
						local pss=`dumpsys meminfo $pid|$bb awk -v pid=$pid -v comm=$command -v time=$uptime '{if($1=="**")comm=substr($6,2,length($6)-2);if($1=="Native"){n=n+$(NF-2);o=o+$(NF-1);p=p+$NF}else{if($1=="Dalvik"&&NF>6){d=d+$(NF-2);e=e+$(NF-1);f=f+$NF;if($2=="Heap"){g=g+$(NF-6)}else{g=g+$2}}else{if($1=="TOTAL"){s=$2+0}else{if($1=="Views:"){print time","comm","s","pid","n+0","o+0","p+0","d+0","e+0","f+0","g+0","$2+0}else{if($3=="Views:"){print time","comm","s","pid","n+0","o+0","p+0","d+0","e+0","f+0","g+0","$4+0}}}}}}'`
						if [ ! -z "$pss" -a ! -z $Ts ];then
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
if [ -f /data/local/tmp/mem2.tmp ];then
	$bb rm /data/local/tmp/mem2.tmp
fi
local tmp=`dumpsys meminfo|$bb sed 's/(//g;s/)//g;s/Total PSS by //g;s/ Services/_Services/g;s/K: / kB: /g;s/,//g'|$bb awk -v tmp="/data/local/tmp/mem2.tmp" -v time=$uptime '{if(NF==0)S+=1;if(NR!=2){if(S==2){if(NF==3)g=$3;if(NF>=5)print time","$3","$1" "$5" "g}else{if(S==3){if(NF>2){C=$3;if(NF>3){for(i=4;i<=NF;i++)C=C"_"$i};print C" "$1 >>tmp}}else{if(S==4){if($1=="Free"){if(substr($3,length($3),1)!="K"){R=0;r=sprintf("Free_RAM "$3"\ncached_pss "$5"\ncached_kernel "$9"\nfree "$(NF-1))}else{R=1;r=sprintf("Free_RAM "substr($3,1,length($3)-1)"\ncached_pss "substr($4,1,length($4)-1)"\ncached_kernel "substr($8,1,length($8)-1)"\nfree "substr($(NF-1),1,length($(NF-1))-1))};print r >>tmp};if($1=="Used"){if(R==0){r=sprintf("Used_RAM "$3"\nused_pss "$5"\nkernel "$9)}else{r=sprintf("Used_RAM "substr($3,1,length($3)-1)"\nused_pss "substr($4,1,length($4)-1)"\nkernel "substr($8,1,length($8)-1))};print r >>tmp};if($1=="Lost"){if(R==0){r=sprintf("Lost_RAM "$3)}else{r=sprintf("Lost_RAM "substr($3,1,length($3)-1))};print r >>tmp}}}}}}'`

if [ ! -z "$tmp" -a "$Time" != "0" ];then
	if [ ! -f $monitor/mem2.csv ];then
		$bb sort /data/local/tmp/mem2.tmp|$bb awk -v csv="$monitor/mem2.csv" -v Time="$uptime" '{if(T==""){T=$1;r=$2}else{T=T","$1;r=r","$2}}END{print "uptime,"T>csv;if(r!="")print Time","r>>csv;print NR}' >/data/local/tmp/mem2.check
	else
		local check=`cat /data/local/tmp/mem2.check`
		$bb sort /data/local/tmp/mem2.tmp|$bb awk -v csv="$monitor/mem2.csv" -v Time="$uptime" -v C=$check '{if(r=="")r=$2;else r=r","$2}END{if(NR==C&&r!="")print Time","r>>csv}'
	fi
	local grep_str="busybox|DUMP"
	if [ ! -z "$packages" ];then
		local grep_str="$grep_str|"`echo $packages|$bb sed 's/\./\\\\./g;s/\[/\\\[/g;s/\]/\\\]/g'`
		local tmp=`echo "$tmp"|$bb grep -E -v "$grep_str"`
	fi
	echo "$tmp"|while read l;do
		local data=`echo "$l"|$bb awk '{print $1}'`
		local pid=`echo "$l"|$bb awk '{print $2}'`
		local type=`echo "$l"|$bb awk '{print $3}'`
		if [ -f /proc/$pid/cmdline ];then
			local arg=`$bb awk 'BEGIN{r="null"}{if(NR>1){if(NR==2)r=$0;else r=r" "$0}}END{print r}' /proc/$pid/cmdline`
			if [ -z "`echo $arg|$bb tr -d " "`" ];then
				local arg="null"
			fi
		else
			local arg="died"
		fi
		if [ ! -z $pid -a ! -z "$data" ];then
			if [ $root -eq 1 ];then
				echo "$data,$pid,,,,,,,,,,,\"$arg\""
			else
				echo "$data,$pid,,,,,,,,,,\"$arg\""
			fi
		fi
	done
fi
}

getmem(){
local info=`$bb awk 'BEGIN{r=0}{if($1=="MemFree:"){a=$2};if($1=="Buffers:"){b=$2};if($1=="Cached:"){c=$2};if($1=="Active:"){e=$2};if($1=="Inactive:"){f=$2};if($1=="Active(anon):"){g=$2};if($1=="Inactive(anon):"){h=$2};if($1=="Active(file):"){i=$2};if($1=="Inactive(file):"){j=$2};if($1=="Dirty:"){k=$2};if($1=="Writeback:"){l=$2};if($1=="Mapped:"){m=$2};if($1=="Slab:"){n=$2};if($1=="CMA"&&$2=="Free:"){r=1;a=a-$3;o=$3}}END{if(r==0) print a","b","c","e","f","g","h","i","j","k","l","m","n;else print a","b","c","e","f","g","h","i","j","k","l","m","n","o}' /proc/meminfo`
if [ ! -z "$info" ];then
	echo "$uptime,$info" >>$monitor/mem.csv
fi
}

getvss(){
$bb ps -o pid,ppid,vsz,rss,args|$bb sed 's/{.*.} //g'|$bb awk -v OFS="," -v time=$uptime -v csv="$monitor/meminfo2.csv" 'NR>1&&$5!="/data/local/tmp/busybox"{if(substr($3,length($3),1)=="m"){V=substr($3,1,length($3)-1)}else{if(substr($3,length($3),1)=="g")V=substr($3,1,length($3)-1)*1024;else V=sprintf("%.3f",$3/1024)+0};if(substr($4,length($4),1)=="m"){R=substr($4,1,length($4)-1)}else{if(substr($4,length($4),1)=="g")R=substr($4,1,length($4)-1)*1024;else R=sprintf("%.3f",$4/1024)+0};C=$5;A="";if(NF>=6)A=$6;if(NF>6){for(i=7;i<=NF;i++)A=A" "$i};if(A=="")A="null";if(V>0)print time,$1,$2,V,R,C,"\""A"\"">>csv}'
}

getcpu(){
local tmp=`$bb top -b -n 1|$bb grep -E -v "busybox|Shutdown thread"|$bb sed '2s/%//g;s/\\.0 / /g;s/ S N / SN /g;s/ R N / RN /g;s/ D N / DN /g;s/ Z N / ZN /g;s/ T N / TN /g;s/S </S</g;s/D </D</g;s/R </R</g;s/Z </Z</g;s/T </T</g;s/t </t</g;s/[0-9]m[0-9]/m /g;s/}/{/g;s/ th\\]/_th\\]/g;s/\\[mtk /\\[mtk_/g;s/Net Work Manage/Net-Work-Manage/g' 2>/dev/null|$bb awk -v time="$uptime" -v csv="$monitor/cpu.csv" -v csv2="$monitor/check.log" -v cpu=$1 -v T="{" -v T2="\"" '{if(NR==2) print time","$2","$4","$6","$8","$10","$12","$14 >>csv;if(NR>4){r="";if($cpu=="0") exit;if($cpu+0==0){if($(cpu-1)/1000>0){a=sprintf("%.0f",$(cpu-1)/1000)}else{a=sprintf("%.1f",$(cpu-1))}c=substr($(cpu-1),length(a)+1);r=$cpu;if(NF>cpu);r=r T$(cpu+1)}else{if($(cpu+1)+0!=0){print $0 >>csv2}else{c=$cpu;r=$(cpu+1)}};if($(cpu+1)+0==0){if(NF>cpu+1){r=r T$(cpu+2);if(NF>cpu+2)r=r T$(cpu+3);if(NF>cpu+3)for(i=(cpu+4);i<=NF;i++)r=r" "$i};print time","$1","c","r}}}'`
echo "$tmp"|$bb awk -F"{" -v S="}" -v T="\"" '{if(NF==1)print $0",,";if(NF==2)print $1","T$2T",";if(NF==3)print $1","T$2" "$3T",";if(NF==4&&$3=="")print $1$4",,"T$2T;if(NF==4&&$3!="")print $1","T$2" "$3S$4T",";if(NF>4&&$3==""){a=$5;if(NF>5)for(i=6;i<=NF;i++)a=a S $i;print $1$4","T a T","T$2T};if(NF>4&&$3!=""){a=$4;if(NF>4)for(i=5;i<=NF;i++)a=a S $i;print $1","T$2" "$3" "a T","}}' >>$monitor/cpuinfo.csv
}

getFPS(){
local KPI=100
echo "FU(s),LU(s),Date:$1,FPS:$2,Frames,jank,jank2,MFS(ms),OKT:$KPI,SS(%),WN" >$monitor/fps_window.csv
echo "FU(s),LU(s),Date:$1,FPS:$2,Frames,jank,jank2,MFS(ms),OKT:$KPI,SS(%),WN" >$monitor/fps_system.csv
local uptime=`$bb awk -v T="$EPOCHREALTIME" 'NR==3{printf("%.6f",T-$3/1000000000+8*3600)}' /proc/timer_list`
while true;do
	dumpsys SurfaceFlinger --latency-clear
	if [ -f /data/local/tmp/stop ];then
		break
	fi
	$bb usleep 1600000
	dumpsys SurfaceFlinger --latency "$1"|$bb awk -v time=$uptime -v target=$2 -v kpi=$KPI '{if(NR==1){r=$1/1000000;if(r<0)r=$1/1000;b=0;n=0;w=1}else{if(n>0&&$0=="")O=1;if(NF==3&&$2!=0&&$2!=9223372036854775807){x=($3-$1)/1000000/r;if(b==0){b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}else{c=($2-b)/1000000;if(c>500){O=1}else{n+=1;if(c>=r){C+=c;if(c>kpi)o+=1;if(c>=m)m=c;if(x>1)d+=1;if(x>2)D+=1;b=$2}else{C+=r;b=sprintf("%.0f",b+r*1000000)}}};if(n==1)s=sprintf("%.3f",$2/1000000000)};if(n>0&&O==1){O=0;if(n==1)t=sprintf("%.3f",s+C/1000);else t=sprintf("%.3f",b/1000000000);T=strftime("%F %T",time+t);f=sprintf("%.2f",n*1000/C);m=sprintf("%.0f",m);g=f/target;if(g>1)g=1;h=kpi/m;if(h>1)h=1;e=sprintf("%.2f",g*60+h*20+(1-o/n)*20);print s","t","T","f+0","n","d","D","m","o","e","w;n=0;if($0==""){b=0;w+=1}else{b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}}}}' >>$monitor/fps_window.csv
	dumpsys SurfaceFlinger --latency |$bb awk -v time=$uptime -v target=$2 -v kpi=$KPI '{if(NR==1){r=$1/1000000;if(r<0)r=$1/1000;b=0;n=0;w=1}else{if(n>0&&$0=="")O=1;if(NF==3&&$2!=0&&$2!=9223372036854775807){x=($3-$1)/1000000/r;if(b==0){b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}else{c=($2-b)/1000000;if(c>500){O=1}else{n+=1;if(c>=r){C+=c;if(c>kpi)o+=1;if(c>=m)m=c;if(x>1)d+=1;if(x>2)D+=1;b=$2}else{C+=r;b=sprintf("%.0f",b+r*1000000)}}};if(n==1)s=sprintf("%.3f",$2/1000000000)};if(n>0&&O==1){O=0;if(n==1)t=sprintf("%.3f",s+C/1000);else t=sprintf("%.3f",b/1000000000);T=strftime("%F %T",time+t);f=sprintf("%.2f",n*1000/C);m=sprintf("%.0f",m);g=f/target;if(g>1)g=1;h=kpi/m;if(h>1)h=1;e=sprintf("%.2f",g*60+h*20+(1-o/n)*20);print s","t","T","f+0","n","d","D","m","o","e","w;n=0;if($0==""){b=0;w+=1}else{b=$2;n=1;d=0;D=0;if(x<=1)C=r;if(x>1){d+=1;C=int(x)*r;if(x%1>0)C+=r};if(x>2)D+=1;m=r;o=0}}}}' >>$monitor/fps_system.csv
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
cpu_p=`$bb top -b -n 1|$bb awk 'NR==4{print NF-1}'`
loop=0
if [ -f /sys/class/kgsl/kgsl-3d0/devfreq/cur_freq -a -f /sys/class/power_supply/battery/current_now ];then
	cpu_type=0
	echo "uptime,gpu_freq,charge_current" >$monitor/others.csv
else
	cpu_type=1
fi
#info
$bb cat /proc/cpuinfo >$monitor/cpuinfo.txt
HW=`$bb awk -F":" 'substr($1,1,8)=="Hardware"{print substr($2,2)}' /proc/cpuinfo|$bb tr -d ,`
echo PID=$$ >$monitor/info.log
echo cpu_type=$cpu_type >>$monitor/info.log
echo sleep=$4 >>$monitor/info.log
echo Hardware=$HW >>$monitor/info.log
echo build=`getprop ro.build.fingerprint` >>$monitor/info.log
echo time=`echo $EPOCHREALTIME|$bb awk -F. '{print strftime("%F %T",$1+8*3600)"."$2}'` >>$monitor/info.log
echo uptime=`$bb awk -F. '{print $1}' /proc/uptime` >>$monitor/info.log
if [ $cpu_type -eq 0 ];then
	echo charge_full=`$bb awk '{print $0/1000}' /sys/class/power_supply/bms/charge_full` >>$monitor/info.log
fi

#csv
echo "uptime,usr,sys,nic,idle,io,irq,sirq" >$monitor/cpu.csv
echo "uptime,PID,%CPU,Command,args,Thread" >$monitor/cpuinfo.csv
if [ `$bb grep -c "CMA Free" /proc/meminfo` -eq 0 ];then
	echo "uptime:$4,MemFree,Buffers,Cached,Active,Inactive,Active(anon),Inactive(anon),Active(file),Inactive(file),Dirty,Writeback,Mapped,Slab" >$monitor/mem.csv
else
	echo "uptime:$4,MemFree,Buffers,Cached,Active,Inactive,Active(anon),Inactive(anon),Active(file),Inactive(file),Dirty,Writeback,Mapped,Slab,CMA Free" >$monitor/mem.csv
fi
echo "uptime,BatteryLevel,PlugType" >$monitor/btm.csv
if [ $root -eq 1 ];then
	mkdir -p $monitor/FDs
	echo "uptime,Process_Name,Pss,PID,Native_Heap(Size),Native_Heap(Alloc),Native_Heap(Free),Dalvik_Heap(Size),Dalvik_Heap(Alloc),Dalvik_Heap(Free),Dalvik_Pss,Views,Threads,FD,Args" >$monitor/meminfo.csv
	if [ $5 -eq 2 ];then
		echo "uptime,PID,Process_Name,VSS,RSS,Pss,shared_clean,shared_dirty,private_clean,private_dirty,#,object" >$monitor/showmap.csv
		showmap=$((60/$5))
	fi
else
	echo "uptime,Process_Name,Pss,PID,Native_Heap(Size),Native_Heap(Alloc),Native_Heap(Free),Dalvik_Heap(Size),Dalvik_Heap(Alloc),Dalvik_Heap(Free),Dalvik_Pss,Views,Threads,Args" >$monitor/meminfo.csv
fi
echo "uptime,PID,PPID,VSZ,RSS,COMMAND,Args" >$monitor/meminfo2.csv
echo "Loop:$4,uptime,Date_Time,DisplayID,FocusedWindow,FocusedApplication,Flags,Type,Pid,uid,frame" >$monitor/windows.csv

CPUS=`$bb awk -v csv="$monitor/cur_freq.csv" 'END{R="uptime,0:"NR;for(i=1;i<NR;i++)R=R","i;print R>csv;print NR}' /sys/devices/system/cpu/cpu*/online`

thermal_path=""
for i in `ls /sys/devices/virtual/thermal/thermal_zone*/type`;do
	zone=`echo $i|$bb awk '{split($0,N,"/");print N[6]}'`
	check=`cat $i 2>/dev/null`
	if [ ! -z "$check" ];then
		title=$zone"("$check")"
	else
		title=$zone"(unknown)"
	fi
	check=`cat /sys/devices/virtual/thermal/$zone/temp 2>/dev/null`
	if [ ! -z "$check" ];then
		if [ -z "$thermal_path" ];then
			thermal_path=/sys/devices/virtual/thermal/$zone/temp
			thermal_type="uptime,"$title
			thermal_zones=$zone
		else
			thermal_path=$thermal_path" "/sys/devices/virtual/thermal/$zone/temp
			thermal_type=$thermal_type","$title
			thermal_zones=$thermal_zones" "$zone
		fi
	fi
done
thermal_type=`echo $thermal_type|$bb sed 's/thermal_zone//g'`
echo $thermal_type >$monitor/thermal.csv
unset zone
unset check
unset title
unset thermal_type

#FPS
if [ ! -z "$2" ];then
	getFPS "$2" 60 &
fi

while true;do
	date_time="`echo $EPOCHREALTIME|$bb awk -F. '{print strftime("%F %T",$1+8*3600)"."substr($2,1,3)}'`"
	uptime=`$bb awk '{print $1}' /proc/uptime`
	#cpu freq
	$bb awk -v cpus=$CPUS -v time=$uptime -v csv="$monitor/cur_freq.csv" '{split(FILENAME,N,"/");r[substr(N[6],4)]=$0/1000}END{R=r[0];for(i=1;i<cpus;i++)R=R","r[i];print time","R >>csv}' /sys/devices/system/cpu/cpu*/cpufreq/scaling_cur_freq
	#thermal_zone
	$bb awk -v time=$uptime -v TZs="$thermal_zones" -v csv="$monitor/thermal.csv" 'BEGIN{split(TZs,tmp," ")}{split(FILENAME,N,"/");r[N[6]]=$0}END{for(i in tmp){if(R=="")R=r[tmp[i]]+0;else R=R","r[tmp[i]]+0};print time","R >>csv}'  $thermal_path
	#windows.csv
	dumpsys input|$bb grep " name="|$bb awk -v OFS="," -v loop=$loop -v time=$uptime -v date="$date_time" -v csv="$monitor/windows.csv" '{if($1=="FocusedApplication:"){A=$6}else{W=substr($4,1,length($4)-3);if($9=="visible=true,"){D=substr($5,11,length($5)-11);if(D>0)D=1;for(i=11;i<=NF;i++){if(substr($i,1,5)=="flags")F=substr($i,7,length($i)-7);if(substr($i,1,4)=="type")T=substr($i,6,length($12)-6);if(substr($i,1,5)=="frame"){S=substr($i,7,length($i)-7);gsub("\]","",S);gsub("\\[",",",S)};if(substr($i,1,8)=="ownerPid")P=substr($i,10,length($i)-10);if(substr($i,1,8)=="ownerUid")U=substr($i,10,length($i)-10)};if($7=="hasFocus=true,"){if(match(W,"/")){split(W,A,"/");gsub(A[1],"",A[2]);A=A[1]"/"A[2]};print loop,time,date,D,W,A,F,T,P,U,"\""S"\"" >>csv}}}}'
	#btm.csv
	dumpsys power|$bb grep -E "mBatteryLevel=|mPlugType"|$bb awk -F "=" -v OFS="," -v time=$uptime -v csv="$monitor/btm.csv" '{if(NR==1)a=$2;else{print time,$2,a >>csv;exit}}'
	#others
	if [ $cpu_type -eq 0 ];then
		$bb awk -v time=$uptime -v csv="$monitor/others.csv" '{if(R=="")R=$0/1000000;else R=R","$0}END{print time","R >>csv}' /sys/class/kgsl/kgsl-3d0/devfreq/cur_freq /sys/class/power_supply/battery/current_now
	fi
	#cpu
	getcpu $cpu_p
	getmem
	getvss
	if [ $5 -ge 1 ];then
		get_meminfo >>$monitor/meminfo.csv
	fi
	get_package $5 >>$monitor/meminfo.csv
	#stop
	loop=$((loop+1))
	if [ -f /data/local/tmp/stop ];then
		echo "Found stop file!!!"
		wait
		touch /data/local/tmp/finish
		break
	elif [ `$bb df /data|$bb awk '{r=substr($(NF-1),1,length($(NF-1))-1)}END{print r+0}'` -ge 90 ];then
		echo "The free space of data less 10%,stop!!!"
		wait
		touch /data/local/tmp/finish
		break
	fi
	if [ $4 -gt 0 ];then
		$bb sleep $4
	fi
done

function getMemData(a){
	var data=TotalData.memData
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

function getMem2Data(a){
	var data=TotalData.mem2Data
	switch (a){
		case 'mmap':
			return [data[0], data[1], data[2]];
			break;
		case 'other':
			return [data[0], data[3], data[4]];
			break;
	}
}

function getbtm(){
	var btm=TotalData.btm
	var level=[];
	var PlugType=[];
	for (var i=0; i < btm[0].length; i++){
		level.push([btm[0][i],btm[1][i]]);
		PlugType.push([btm[0][i],btm[2][i]])
	}
	var series=[];
	series.push({name:'BatteryLevel',data:level});
	series.push({name:'PlugType',data:PlugType,yAxis: 1});
	return [btm[0][0],series]
}

function getcpus(){
	var cpusData=TotalData.cpusData;
	var tmp=[];
	for (var j=0; j < cpusData[1].length; j++){
		tmp.push([])
	};
	var min_x;
	if(cpusData[0][0]>0){
		min_x=cpusData[0][0]
	}else{
		min_x=cpusData[0][1]
	};
	var max_x=cpusData[0][cpusData[0].length-1]
	for (var i=0; i < cpusData[0].length; i++){
		for (var j=0; j < cpusData[1].length; j++){
			if(cpusData[0][j]>0){
				tmp[j].push([cpusData[0][i],cpusData[1][j][i]])
			}
		}
	}
	var series=[];
	series.push({name:'cpu（均值：' + cpusData[2][0][0] + '，中位值：' + cpusData[2][0][1] + '）',data:tmp[0]});
	for (var j=0; j < cpusData[1].length-1; j++){
		series.push({name:'cpu' + j + '（均值：' + cpusData[2][j+1][0] + '，中位值：' + cpusData[2][j+1][1] + '）',data:tmp[j+1]})
	};
	return [min_x,max_x,series]
}

function getcpu(){
	var usr=[],sys=[],nic=[],idle=[],io=[],irq=[],sirq=[];
	var cpudata=TotalData.cpuData;
	for (var i=0; i < cpudata[0].length; i++){
		usr.push([cpudata[0][i],cpudata[1][0][i]]);
		sys.push([cpudata[0][i],cpudata[2][0][i]]);
		nic.push([cpudata[0][i],cpudata[3][0][i]]);
		idle.push([cpudata[0][i],cpudata[4][0][i]]);
		io.push([cpudata[0][i],cpudata[5][0][i]]);
		irq.push([cpudata[0][i],cpudata[6][0][i]]);
		sirq.push([cpudata[0][i],cpudata[7][0][i]])
	}
	var series=[];
	series.push({name:'usr（均值：' + cpudata[1][1] + '，中位值：' + cpudata[1][2] + '）',data:usr});
	series.push({name:'sys（均值：' + cpudata[2][1] + '，中位值：' + cpudata[2][2] + '）',data:sys});
	series.push({name:'nic（均值：' + cpudata[3][1] + '，中位值：' + cpudata[3][2] + '）',data:nic});
	series.push({name:'idle（均值：' + cpudata[4][1] + '，中位值：' + cpudata[4][2] + '）',data:idle});
	series.push({name:'io（均值：' + cpudata[5][1] + '，中位值：' + cpudata[5][2] + '）',data:io});
	series.push({name:'irq（均值：' + cpudata[6][1] + '，中位值：' + cpudata[6][2] + '）',data:irq});
	series.push({name:'sirq（均值：' + cpudata[7][1] + '，中位值：' + cpudata[7][2] + '）',data:sirq})
	return [cpudata[0][0],series]
}

function getcpuinfo(list){
	var tat=[],series=[],pids=[];
	for (var i = 0; i < list.length; i++){
		var cpu=[];
		var p=list[i][1];
		var cpuinfo=TotalData.cpuInfo[p-1];
		for (var j=0; j < cpuinfo[0].length; j++){
			if(isArray(cpuinfo[1][j]) == false){
				cpu.push({x:cpuinfo[0][j],y:cpuinfo[1][j]});
				pids.push("")
			}else{
				if(cpuinfo[1][j].length == 2){
					if(j!=0){cpu.push(null)};
					cpu.push({x:cpuinfo[0][j],y:cpuinfo[1][j][0],marker:{enabled:true,fillColor:'#FF0000'}})
					if(j!=cpuinfo[0].length-1){cpu.push(null)};
					pids.push("")
				};
				if(cpuinfo[1][j].length == 3){
					if(j!=0){cpu.push(null)};
					cpu.push({x:cpuinfo[0][j],y:cpuinfo[1][j][0],marker:{enabled:true,fillColor:'#FF00FF'}});
					if(j!=cpuinfo[0].length-1){cpu.push(null)};
					pids.push(cpuinfo[1][j][2])
				}
			}
		};
		tat.push([cpuinfo[0],cpuinfo[2],cpuinfo[3],pids]);
		var textStr=list[i][0];
		if(textStr.length >35)textStr=textStr.substr(0,25) + ".." + textStr.substr(-10,10);
		series.push({name:textStr,data:cpu});
		cpu=[];
	}
	return [tat,series]
}

function getmem(a){
	var data=getMemData(a);
	var series=[];
	switch (a){
		case 'free':
			var free=[],memfree=[],buffers=[],cached=[];
			for (var i=0; i < data[0].length; i++){
				free.push({x:data[0][i],y:data[1][i]});
				memfree.push({x:data[0][i],y:data[2][0][i]});
				buffers.push({x:data[0][i],y:data[2][1][i]});
				cached.push({x:data[0][i],y:data[2][2][i]});
			}
			series.push({name:'MemAvailable',data:free});
			series.push({name:'MemFree',data:memfree});
			series.push({name:'Buffers',data:buffers});
			series.push({name:'Cached',data:cached});
			break;
		case 'all':
			var free=[],active=[],inactive=[],io=[],mapped=[],slab=[];
			for (var i=0; i < data[0].length; i++){
				free.push({x:data[0][i],y:data[1][i]});
				active.push({x:data[0][i],y:data[2][i]});
				inactive.push({x:data[0][i],y:data[3][i]});
				io.push({x:data[0][i],y:data[4][i]});
				mapped.push({x:data[0][i],y:data[5][i]});
				slab.push({x:data[0][i],y:data[6][i]})
			}
			series.push({name:'MemAvailable',data:free});
			series.push({name:'Active',data:active});
			series.push({name:'Inactive',data:inactive});
			series.push({name:'io',data:io});
			series.push({name:'Mapped',data:mapped});
			series.push({name:'Slab',data:slab});
			break;
		case 'io':
			var io=[],dirty=[],writeback=[];
			for (var i=0; i < data[0].length; i++){
				io.push({x:data[0][i],y:data[1][i]});
				dirty.push({x:data[0][i],y:data[2][i]});
				writeback.push({x:data[0][i],y:data[3][i]});
			}
			series.push({name:'IO',data:io});
			series.push({name:'Dirty',data:dirty});
			series.push({name:'Writeback',data:writeback});
			break;
		case 'AI':
		var active=[],inactive=[],active_a=[],inactive_a=[],active_f=[],inactive_f=[];
			for (var i=0; i < data[0].length; i++){
				active.push({x:data[0][i],y:data[1][i]});
				inactive.push({x:data[0][i],y:data[2][i]});
				active_a.push({x:data[0][i],y:data[3][i]});
				inactive_a.push({x:data[0][i],y:data[4][i]});
				active_f.push({x:data[0][i],y:data[5][i]});
				inactive_f.push({x:data[0][i],y:data[6][i]});
			}
			series.push({name:'Active',data:active});
			series.push({name:'Inactive',data:inactive});
			series.push({name:'Active(anon)',data:active_a});
			series.push({name:'Inactive(anon)',data:inactive_a});
			series.push({name:'Active(file)',data:active_f});
			series.push({name:'Inactive(file)',data:inactive_f});
			break;
		case 'MS':
		var mapped=[],slab=[];
		for (var i=0; i < data[0].length; i++){
				mapped.push({x:data[0][i],y:data[1][i]});
				slab.push({x:data[0][i],y:data[2][i]});
			}
			series.push({name:'Mapped',data:mapped});
			series.push({name:'Slab',data:slab});
			break;}
	return [data[0][0],series]
}

function getmem2(a){
	var data=getMem2Data(a);
	var series=[];
	for (var l=0; l < data[1].length; l++){
		var tmp=[];
		for (var i=0; i < data[0].length; i++){
			tmp.push({x:data[0][i],y:data[2][l][i]});
		}
		series.push({name:data[1][l],data:tmp});
	}
	return [data[0][0],series];
}

function getmeminfo(a){
	var data=TotalData.memInfo[a],pids=[];
	var ta=[],series=[],pss=[],NHS=[],NHA=[],NHF=[],DHP=[],DHS=[],DHA=[],DHF=[],Views=[],Threads=[],type=1,FD=[];
	if(data[data.length-1].length == 0){
		type=0
	}
	ta.push(data[1]);
	ta.push(data[2]);
	for (var i=0; i < data[1].length; i++){
		if(isArray(data[3][i]) == false){
			pss.push({x:data[1][i],y:data[3][i]});
			if(data[0] == 1){
				NHS.push({x:data[1][i],y:data[6][i]});
				NHA.push({x:data[1][i],y:data[7][i]});
				NHF.push({x:data[1][i],y:data[8][i]});
				DHP.push({x:data[1][i],y:data[9][i]});
				DHS.push({x:data[1][i],y:data[10][i]});
				DHA.push({x:data[1][i],y:data[11][i]});
				DHF.push({x:data[1][i],y:data[12][i]});
				Views.push({x:data[1][i],y:data[4][i]});
				Threads.push({x:data[1][i],y:data[5][i]});
			}
			if(type == 1){
				FD.push({x:data[1][i],y:data[data.length-1][i]});
			}
		}else{
			if(data[3][i].length == 2){
				if(i!=0){
					pss.push(null);
					if(data[0] == 1){
						NHS.push(null);
						NHA.push(null);
						NHF.push(null);
						DHP.push(null);
						DHS.push(null);
						DHA.push(null);
						DHF.push(null);
						Views.push(null);
						Threads.push(null);
					}
					if(type == 1){
						FD.push(null);
					}
				};
				pss.push({x:data[1][i],y:data[3][i][0],marker:{enabled:true,fillColor:'#FF0000'}});
				if(data[0] == 1){
					NHS.push({x:data[1][i],y:data[6][i],marker:{enabled:true,fillColor:'#FF0000'}});
					NHA.push({x:data[1][i],y:data[7][i],marker:{enabled:true,fillColor:'#FF0000'}});
					NHF.push({x:data[1][i],y:data[8][i],marker:{enabled:true,fillColor:'#FF0000'}});
					DHP.push({x:data[1][i],y:data[9][i],marker:{enabled:true,fillColor:'#FF0000'}});
					DHS.push({x:data[1][i],y:data[10][i],marker:{enabled:true,fillColor:'#FF0000'}});
					DHA.push({x:data[1][i],y:data[11][i],marker:{enabled:true,fillColor:'#FF0000'}});
					DHF.push({x:data[1][i],y:data[12][i],marker:{enabled:true,fillColor:'#FF0000'}});
					Views.push({x:data[1][i],y:data[4][i],marker:{enabled:true,fillColor:'#FF0000'}});
					Threads.push({x:data[1][i],y:data[5][i],marker:{enabled:true,fillColor:'#FF0000'}});
				};
				if(type == 1){
					FD.push({x:data[1][i],y:data[data.length-1][i],marker:{enabled:true,fillColor:'#FF0000'}});
				};
				pids.push("");
			}else{
				if(data[3][i].length == 3){
					pss.push({x:data[1][i],y:data[3][i][0],marker:{enabled:true,fillColor:'#FF00FF'}});
					if(data[0] == 1){
						NHS.push({x:data[1][i],y:data[6][i],marker:{enabled:true,fillColor:'#FF00FF'}});
						NHA.push({x:data[1][i],y:data[7][i],marker:{enabled:true,fillColor:'#FF00FF'}});
						NHF.push({x:data[1][i],y:data[8][i],marker:{enabled:true,fillColor:'#FF00FF'}});
						DHP.push({x:data[1][i],y:data[9][i],marker:{enabled:true,fillColor:'#FF00FF'}});
						DHS.push({x:data[1][i],y:data[10][i],marker:{enabled:true,fillColor:'#FF00FF'}});
						DHA.push({x:data[1][i],y:data[11][i],marker:{enabled:true,fillColor:'#FF00FF'}});
						DHF.push({x:data[1][i],y:data[12][i],marker:{enabled:true,fillColor:'#FF00FF'}});
						Views.push({x:data[1][i],y:data[4][i],marker:{enabled:true,fillColor:'#FF00FF'}});
						Threads.push({x:data[1][i],y:data[5][i],marker:{enabled:true,fillColor:'#FF00FF'}});
					};
					if(type == 1){
						FD.push({x:data[1][i],y:data[data.length-1][i],marker:{enabled:true,fillColor:'#FF00FF'}});
					};
					pids.push(data[3][i][2]);
				}else{
					pids.push("");
				}
			}
		}
	}
	ta.push(pids);
	series.push({name:'Pss',data:pss})
	if(data[0] == 1){
		series.push({name:'Native_Heap(Size)',data:NHS});
		series.push({name:'Native_Heap(Alloc)',data:NHA});
		series.push({name:'Native_Heap(Free)',data:NHF});
		series.push({name:'Dalvik_Other',data:DHP});
		series.push({name:'Dalvik_Heap(Size)',data:DHS});
		series.push({name:'Dalvik_Heap(Alloc)',data:DHA});
		series.push({name:'Dalvik_Heap(Free)',data:DHF});
		series.push({name:'Views',data:Views,yAxis: 1});
		series.push({name:'Threads',data:Threads,yAxis: 1});
	}
	if(type == 1){
		series.push({name:'FD',data:FD,yAxis: 1});
	}
	NHS=[];NHA=[];NHF=[];DHP=[];DHS=[];DHA=[];DHF=[];Views=[];Threads=[];FD=[];
	return [ta,series];
}

function getmeminfo2(a){
	var data=TotalData.psMeminfo[a];
	var ta=[],series=[],vsz=[],rss=[],pids=[];
	ta.push(data[0]);
	ta.push(data[1]);
	for (var i=0; i < data[0].length; i++){
		if(isArray(data[2][i]) == false){
			vsz.push({x:data[0][i],y:data[2][i]});
			rss.push({x:data[0][i],y:data[3][i]});
			pids.push("");
		}else{
			if(data[2][i].length == 2){
				if(i!=0){
					vsz.push(null);
					rss.push(null);
				}
				vsz.push({x:data[0][i],y:data[2][i][0],marker:{enabled:true,fillColor:'#FF0000'}});
				rss.push({x:data[0][i],y:data[3][i],marker:{enabled:true,fillColor:'#FF0000'}});
				pids.push("");
			}else{
				if(data[2][i].length == 3){
					vsz.push({x:data[0][i],y:data[2][i][0],marker:{enabled:true,fillColor:'#FF00FF'}});
					rss.push({x:data[0][i],y:data[3][i],marker:{enabled:true,fillColor:'#FF00FF'}});
					pids.push(data[2][i][2]);
				}else{
					pids.push("");
				}
			}
		}
	};
	ta.push(pids);
	series.push({name:'VSZ',data:vsz})
	series.push({name:'RSS',data:rss})
	return [ta,series];
}

function getFPS(a){
	var fpsdata=TotalData.fpsData
	var fps=[], OKTF=[], jank_percent=[], SS=[], args=[];
	args.push(fpsdata[a][1]);
	args.push(fpsdata[a][2]);
	args.push(fpsdata[a][4]);
	args.push(fpsdata[a][5]);
	args.push(fpsdata[a][6]);
	args.push(fpsdata[a][7]);
	for (var i=0; i < fpsdata[a][0].length; i++){
		fps.push({x:fpsdata[a][0][i],y:fpsdata[a][3][i]});
		fps.push({x:fpsdata[a][1][i],y:fpsdata[a][3][i]});
		SS.push({x:fpsdata[a][1][i],y:fpsdata[a][8][i]});
		OKTF.push({x:fpsdata[a][1][i],y:fpsdata[a][9][i]});
		jank_percent.push({x:fpsdata[a][1][i],y:fpsdata[a][10][i]});
		if(i+1 < fpsdata[a][0].length){
			if(fpsdata[a][0][i+1].sub(fpsdata[a][1][i]) >= 0.5){
				fps.push(null);
				SS.push(null);
				OKTF.push(null);
				jank_percent.push(null)
			}
		}
	}
	var series=[];
	series.push({name:'FPS',data:fps});
	series.push({name: '得分(%)',data: SS,yAxis: 1});
	series.push({name: '单帧超100ms(%)',data: OKTF,yAxis: 1});
	series.push({name: '硬件绘制掉帧(%)',data: jank_percent,yAxis: 1});
	return [[fpsdata[a][0][0], fpsdata[a][1][fpsdata[a][1].length-1]], series, args]
}

function getcurfreq(){
	var series=[];
	var curFreqData=TotalData.curFreqData
	for (var j=0; j < curFreqData[1].length; j++){
		var tmp=[];
		for (var i=0; i < curFreqData[0].length; i++){
			tmp.push({x:curFreqData[0][i],y:curFreqData[1][j][i]});
		}
		series.push({name:'cpufreq' + j,data:tmp});
	}
	if(csvData.cpus==1){
		var cpusData=TotalData.cpusData
		for (var j=0; j < cpusData[1].length; j++){
			var tmp=[];
			for (var i=0; i < cpusData[0].length; i++){
				tmp.push({x:cpusData[0][i],y:cpusData[1][j][i]});
			}
			if(j==0){
				series.push({name:'cpu（均值：' + cpusData[2][j][0] + '，中位值：' + cpusData[2][j][1] + '）',data:tmp,yAxis: 1});
			}else{
				series.push({name:'cpu' + (j-1) + '（均值：' + cpusData[2][j][0] + '，中位值：' + cpusData[2][j][1] + '）',data:tmp,yAxis: 1});
			}
		}
	}
	return [curFreqData[0][0], series]
}

function getthermal(a){
	var tmp=[];
	var thermalData=TotalData.thermalData
	for (var i=0; i < thermalData[0].length; i++){
		tmp.push({x:thermalData[0][i],y:thermalData[2][a][i]});
	}
	return [thermalData[0][0], [{name:thermalData[1][a],data:tmp}]]
}

function getgpufreq(){
	var tmp=[],series=[];
	var gpuFreqData = TotalData.gpuFreqData
	if(gpuFreqData.length == 3){
		var gpu=[];
	}
	for (var i=0; i < gpuFreqData[0].length; i++){
		tmp.push({x:gpuFreqData[0][i],y:gpuFreqData[1][i]});
		if(gpuFreqData.length == 3){
			gpu.push({x:gpuFreqData[0][i],y:gpuFreqData[2][i]});
		}
	}
	series.push({name:'gpu_freq',data:tmp})
	if(gpuFreqData.length == 3){
		series.push({name:'gpu',data:gpu,yAxis: 1})
	}
	return [gpuFreqData[0][0], series]
}
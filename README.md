设计思路：
------
* 设备端离线后台shell脚本监控  
* 用busybox的awk做数据提取存为csv  
* 结果获取到PC端用python脚本生成html报告  

依赖文件：
------
* 设备端需存在/data/local/tmp/busybox `（busybox可到官网对应cpu架构下载）` ，命令：  
`adb push busybox /data/local/tmp`  
`adb shell chmod 755 /data/local/tmp/busybox`  

脚本文件：
------
* 监控脚本monitor.sh  
`adb shell`  
`sh /data/local/tmp/monitor.sh "$monitor_folder" "$monitorWindow" "$monitorPackages" 5 $meminfo_type &`  
参数说明：  
1、monitor_folder = 监控结果文件夹名`（/data/local/tmp/$monitor_folder）`  
2、monitorWindow = fps监控窗口，不抓取为空""
  `adb shell dumpsys SurfaceFlinger`Allocated buffers信息中获取，安卓8.0之后有标号如#0、SurfaceView后有“ - ”传参注意需要""  
3、monitorPackages = 额外抓取heap、views、threads、FD信息的进程，多个用|间隔，不抓取为空""  
4、5 = 5秒间隔  
5、meminfo_type = 1，取所有进程PSS，额外取指定进程详细信息，0则只取配置进程内存信息  
预期监控时长结束后，停止监控：  
`adb shell touch /data/local/tmp/stop`  
获取结果  
`adb pull /data/local/tmp/$monitor_folder`  

* 监控脚本monitor.py  
生成报告：`(需安装python环境和pandas库)`
`python monitor.py 文件夹路径`
说明：
1、脚本会先遍历路径下meminfo.csv所在路径，并使用其上一级目录作为case名  
2、monitor_HTML是报告的模板文件，数据采用的是生成js动态加载的形式，脚本会将其复制到传参目录下  
3、依次处理csv数据存为`data/case名_csv结果文件夹名`，list.js为case选择列表数据，cpu和pss存储了最大值和极值差的csv  
4、查看报告数据需要浏览器有本地读写权限：  
chrome: `start chrome.exe --allow-file-access-from-files`  
firefox: `about:config 中 privacy.file_unique_origin属性false`  
5、报告数据刷新会在点击监控结果文件夹名称后刷新  

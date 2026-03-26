import os
import platform
import socket
import time

import psutil

from module_admin.entity.vo.server_vo import CpuInfo, MemoryInfo, PyInfo, ServerMonitorModel, SysFiles, SysInfo
from utils.common_util import bytes2human


class ServerService:
    """
    服务监控模块服务层
    """

    @staticmethod
    async def get_server_monitor_info():
        # CPU信息
        # 获取CPU总核心数
        cpu_num = psutil.cpu_count(logical=True)
        cpu_usage_percent = psutil.cpu_times_percent()
        cpu_used = cpu_usage_percent.user
        cpu_sys = cpu_usage_percent.system
        cpu_free = cpu_usage_percent.idle
        cpu = CpuInfo(cpuNum=cpu_num, used=cpu_used, sys=cpu_sys, free=cpu_free)

        # 内存信息
        memory_info = psutil.virtual_memory()
        memory_total = bytes2human(memory_info.total)
        memory_used = bytes2human(memory_info.used)
        memory_free = bytes2human(memory_info.available)
        memory_usage = memory_info.percent
        mem = MemoryInfo(total=memory_total, used=memory_used, free=memory_free, usage=memory_usage)

        # 主机信息
        # 获取主机名
        hostname = socket.gethostname()
        # 获取IP (注意: 可能会获取到 127.0.0.1 或内网IP)
        try:
            computer_ip = socket.gethostbyname(hostname)
        except Exception:
            computer_ip = "127.0.0.1"
        os_name = platform.platform()
        computer_name = platform.node()
        os_arch = platform.machine()
        user_dir = os.path.abspath(os.getcwd())
        sys = SysInfo(
            computerIp=computer_ip, computerName=computer_name, osArch=os_arch, osName=os_name, userDir=user_dir
        )

        # python解释器信息
        current_pid = os.getpid()
        current_process = psutil.Process(current_pid)
        python_name = current_process.name()
        python_version = platform.python_version()
        try:
            python_home = current_process.exe()
        except Exception:
            python_home = "Unknown"
        start_time_stamp = current_process.create_time()
        start_time = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(start_time_stamp))
        current_time_stamp = time.time()
        difference = current_time_stamp - start_time_stamp

        days = int(difference // (24 * 60 * 60))
        hours = int((difference % (24 * 60 * 60)) // (60 * 60))
        minutes = int((difference % (60 * 60)) // 60)
        run_time = f"{days}天{hours}小时{minutes}分钟"

        # 获取该进程的内存信息
        current_process_memory_info = current_process.memory_info()
        py = PyInfo(
            name=python_name,
            version=python_version,
            startTime=start_time,
            runTime=run_time,
            home=python_home,
            total=bytes2human(memory_info.available),
            used=bytes2human(current_process_memory_info.rss),
            free=bytes2human(memory_info.available - current_process_memory_info.rss),
            usage=round((current_process_memory_info.rss / memory_info.available) * 100, 2),
        )

        # 磁盘信息
        io = psutil.disk_partitions()
        sys_files = []
        for i in io:
            if "cdrom" in i.opts or i.fstype == "":
                continue
            try:
                o = psutil.disk_usage(i.mountpoint)
                disk_data = SysFiles(
                    dirName=i.device,
                    sysTypeName=i.fstype,
                    typeName="本地固定磁盘（" + i.mountpoint.replace("\\", "") + "）",
                    total=bytes2human(o.total),
                    used=bytes2human(o.used),
                    free=bytes2human(o.free),
                    usage=f"{o.percent}%",
                )
                sys_files.append(disk_data)
            except Exception:
                continue

        result = ServerMonitorModel(cpu=cpu, mem=mem, sys=sys, py=py, sysFiles=sys_files)

        return result

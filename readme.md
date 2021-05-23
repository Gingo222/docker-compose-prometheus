简介：
项目共有5个服务   
prometheus 数据监控服务
alertmanager 监控报警，通过配置一系列的规则进行报警    
grafana 以prometheus 为数据源进行多维度的数据报表展示    
node-exporter  系统信息收集并暴露给prometheus进行采集    
cadvisor 容器信息收集并暴露给prometheus进行采集    
dcgm-exporter gpu信息收集并暴露给prometheus进行采集    

部署步骤：    
1 下载docker-compose-prometheus后, 进入项目

2 本地机器(可略过，目前已注释)
  在本地mysql运行创建granafa的数据库，进行报表监控数据的持久化 
  运行 create database grafana; 

3 修改prometheus.yml,将数据获取地址改为服务器的ip地址

4 运行 docker-compose up -d
  查看各服务是否正常运行

5 服务都起来，打开grafana地址，
地址为IP:3000
用户，密码 admin，admin
创建数database ，datashource 为prometheus`, 
import 导入 grafana 里面的json




部署中出现的一些问题：
cAdvisor 部署可能出现的问题解决方案：
sudo mount -o remount,rw '/sys/fs/cgroup'
sudo ln -s /sys/fs/cgroup/cpu,cpuacct /sys/fs/cgroup/cpuacct,cpu

grafana可以数据不持久化
只需要把docker-compose.yaml 里面的volume注释即可
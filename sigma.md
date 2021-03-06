# **阿里巴巴调度与集群管理系统Sigma**


## 一、概要
>>Sigma集群管理系统是阿里巴巴集团云化战略的关键系统。Sigma通过和离线任务的伏羲调度系统深度集成，突破了若干CPU、内存和网络资源隔离的关键技术，实现了在线和离线任务的混合部署。

## 二、调度系统业界现状

开源领域：Kubernetes，Docker Swarm，Mesos，Yarn等
闭源，基于开源的改造或者开源兼容系统：Borg，Fuxi，Sigma等
在线和离线任务混部：已知主要是Borg
资源利用率状况：Brog领先

## 三、阿里巴巴遇到的问题：
双十一资源利用率非常不充分，部分CPU满负载运行，相当多的CPU闲置。

目标：通过批量优化，达到比顺序调度更优化的效率

## 四、Sigma的改变
* 云化架构，混合云
* 规模： 统一大资源池模式
* 调度：大资源池下，Sigma调度对核心应用的各种策略保障，得以更充分地发挥价值。
* 资源分配：双十一充分使用了所有资源，没有闲置
* 资源利用率：资源充分均衡使用
* 离线和在线任务开始混部
  
## 五、Sigma特点
* 业务架构特点：业务多样化，业务场景复杂
* 灵活可配置的调度策略
* 复杂约束下的批量调度优化
* 精确高水平排布
* 大规模快速建站
* 混合云+弹性
* 支持多样化的应用场景
* 调度优选建模的建立
* 业务团队开发出新的策略，可立即配置生效，不需要代码发布
* 所有调度策略可配置
* 支持的策略：
    * 的应用部署：亲和、互斥、独占、POM0（最重要优先级应用）
    * 其他策略：资源需要，容器创建的特殊需要，IP隔离需要
    * CPU精细调节：CPUSet独占、均衡、SameCore等策略

  #### 统一调度体系
  Sigma 有 Alikenel、SigmaSlave、SigmaMaster 三层大脑联动协作，Alikenel 部署在每一台物理机上，对内核进行增强，在资源分配、时间片分配上进行灵活的按优先级和策略调整，对任务的时延，任务时间片的抢占、不合理抢占的驱逐都能通过上层的规则配置自行决策。SigmaSlave 可以在本机进行容器 CPU 分配、应急场景处理等。通过本机 Slave 对时延敏感任务的干扰快速做出决策和响应，避免因全局决策处理时间长带来的业务损失。SigmaMaster 是一个最强的中心大脑，可以统揽全局，为大量物理机的容器部署进行资源调度分配和算法优化决策。整个架构是面向终态的设计理念，收到请求后把数据存储到持久化存储层，调度器识别调度需求分配资源位置，Slave识别状态变化推进本地分配部署。系统整体的协调性和最终一致性非常好。

  #### 混部架构
  阿里巴巴在 2014 年开始推动混部架构，目前已在阿里巴巴内部大规模部署。在线服务属于长生命周期、规则策略复杂性高、时延敏感类任务。而计算任务生命周期短、调度要求大并发高吞吐、任务有不同的优先级、对时延不敏感。基于这两种调度的本质诉求的不同，我们在混合部署的架构上把两种调度并行处理，即一台物理机上可以既有 Sigma 调度又有 Fuxi 调度，实现基础环境统一。Sigma 调度是通过 SigmaAgent 启动 PouchContainer 容器。Fuxi 也在这台物理机上抢占资源，启动自己的计算任务。所有在线任务都在 PouchContainer 容器上，它负责把服务器资源进行分配并运行在线任务，离线任务填入其空白区，保证物理机资源利用达到饱和，这样就完成了两种任务的混合部署。

  #### 云化架构
  将集群分为在线任务集群、计算任务集群和 ECS 集群。资源管理，单机运维、状况管理，命令通道、监控报警这类基础运维体系已经打通。在双 11 场景中，我们会在云上划出一个独立的区域与其他场景互通。在互通区域，Sigma 调度可以到计算集群服务器里申请资源，生产 Pouch 容器，也可以到 cloud open API 去申请 ECS，生产出容器的资源。在日常的场景中 Fuxi 可以到 sigma 里申请资源，创建需要的容器。
  在双 11 场景中，利用规模化运维系统在容器上构建大量在线服务，包括业务层的混合部署，每个集群都有 online service 和有状态服务及大数据分析。阿里云的独占集群也部署了在线服务和有状态的数据服务，做到了 datacenter as a computer，多个数据中心像一台计算机一样来管理，实现跨多个不同的平台来调度业务的发展所需要的资源。构建了混合云用极低的成本拿到服务器，解决有没有的问题。
  先有服务器规模，再通过分时复用和混合部署来大幅度提升资源利用率。真正实现了弹性资源平滑复用任务灵活混合部署，用最少的服务器最短的时间和用最优效率完成业务容量目标









## 六、参考文献：
阿里巴巴调度与集群管理系统Sigma演讲  - 张瓅玶
http://www.infoq.com/cn/presentations/alibaba-scheduling-and-cluster-management-system-sigma

阿里巴巴 Sigma 调度和集群管理系统架构详解
-阿里系统软件技术 
https://juejin.im/post/5ad867b06fb9a045fc665ca4
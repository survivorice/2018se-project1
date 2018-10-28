 # Ceph #
 ##  Ceph基础介绍 ##
Ceph是一个可靠地、自动重均衡、自动恢复的分布式存储系统，根据场景划分可以将Ceph分为三大块，分别是对象存储、块设备存储和文件系统服务。  
在虚拟化领域里，比较常用到的是Ceph的块设备存储，比如在OpenStack项目里，Ceph的块设备存储可以对接OpenStack的cinder后端存储、Glance的镜像存储和虚拟机的数据存储，比较直观的是Ceph集群可以提供一个raw格式的块存储来作为虚拟机实例的硬盘。  
  
对于对象存储、块设备存储和文件系统服务这3种功能介绍，分别如下：  
1.对象存储，也就是通常意义的键值存储，其接口就是简单的GET、PUT、DEL 和其他扩展，代表主要有 Swift 、S3 以及 Gluster 等；  
2.块存储，这种接口通常以 QEMU Driver 或者 Kernel Module 的方式存在，这种接口需要实现 Linux 的 Block Device 的接口或者 QEMU 提供的 Block Driver 接口，如 Sheepdog，AWS 的 EBS，青云的云硬盘和阿里云的盘古系统，还有 Ceph 的 RBD（RBD是Ceph面向块存储的接口）。在常见的存储中 DAS、SAN 提供的也是块存储；  
3.文件存储，通常意义是支持 POSIX 接口，它跟传统的文件系统如 Ext4 是一个类型的，但区别在于分布式存储提供了并行化的能力，如 Ceph 的 CephFS (CephFS是Ceph面向文件存储的接口)，但是有时候又会把 GlusterFS ，HDFS 这种非POSIX接口的类文件存储接口归入此类。当然 NFS、NAS也是属于文件系统存储；  

## Ceph组件 ##
Ceph的核心组件包括Ceph OSD、Ceph Monitor和Ceph MDS。  
从下面这张图来简单学习下，Ceph 的架构组件。
![image](https://images2017.cnblogs.com/blog/1109179/201711/1109179-20171106211611450-2111366494.png)  
  
Monitor， 负责监视整个集群的运行状况，信息由维护集群成员的守护程序来提供，各节点之间的状态、集群配置信息。Ceph monitor map主要包括OSD map、PG map、MDS map 和 CRUSH 等，这些 map 被统称为集群 Map。ceph monitor 不存储任何数据。下面分别开始介绍这些map的功能：

Monitor map：包括有关monitor 节点端到端的信息，其中包括 Ceph 集群ID，监控主机名和IP以及端口。并且存储当前版本信息以及最新更改信息，通过 "ceph mon dump" 查看 monitor map。  

OSD map：包括一些常用的信息，如集群ID、创建OSD map的 版本信息和最后修改信息，以及pool相关信息，主要包括pool 名字、pool的ID、类型，副本数目以及PGP等，还包括数量、状态、权重、最新的清洁间隔和OSD主机信息。通过命令 "ceph osd dump" 查看。  

PG map：包括当前PG版本、时间戳、最新的OSD Map的版本信息、空间使用比例，以及接近占满比例信息，同事，也包括每个PG ID、对象数目、状态、OSD 的状态以及深度清理的详细信息。通过命令 "ceph pg dump" 可以查看相关状态。  

CRUSH map： CRUSH map 包括集群存储设备信息，故障域层次结构和存储数据时定义失败域规则信息。通过 命令 "ceph osd crush map" 查看。  

MDS map：MDS Map 包括存储当前 MDS map 的版本信息、创建当前的Map的信息、修改时间、数据和元数据POOL ID、集群MDS数目和MDS状态，可通过"ceph mds dump"查看。  

OSD，Ceph OSD 是由物理磁盘驱动器、在其之上的 Linux 文件系统以及 Ceph OSD 服务组成。Ceph OSD 将数据以对象的形式存储到集群中的每个节点的物理磁盘上，完成存储数据的工作绝大多数是由 OSD daemon 进程实现。在构建 Ceph OSD的时候，建议采用SSD 磁盘以及xfs文件系统来格式化分区。BTRFS 虽然有较好的性能，但是目前不建议使用到生产中，目前建议还是处于围观状态。  

Ceph 元数据，MDS。ceph 块设备和RDB并不需要MDS，MDS只为 CephFS服务。  

RADOS，Reliable Autonomic Distributed Object Store。RADOS是ceph存储集群的基础。在ceph中，所有数据都以对象的形式存储，并且无论什么数据类型，RADOS对象存储都将负责保存这些对象。RADOS层可以确保数据始终保持一致。  

librados，librados库，为应用程度提供访问接口。同时也为块存储、对象存储、文件系统提供原生的接口。  

ADOS块设备，它能够自动精简配置并可调整大小，而且将数据分散存储在多个OSD上。  
RADOSGW，网关接口，提供对象存储服务。它使用librgw和librados来实现允许应用程序与Ceph对象存储建立连接。并且提供S3 和 Swift 兼容的RESTful API接口。
CephFS，Ceph文件系统，与POSIX兼容的文件系统，基于librados封装原生接口。  

简单说下CRUSH，Controlled Replication Under Scalable Hashing，它表示数据存储的分布式选择算法， ceph 的高性能/高可用就是采用这种算法实现。CRUSH 算法取代了在元数据表中为每个客户端请求进行查找，它通过计算系统中数据应该被写入或读出的位置。CRUSH能够感知基础架构，能够理解基础设施各个部件之间的关系。并且CRUSH保存数据的多个副本，这样即使一个故障域的几个组件都出现故障，数据依然可用。CRUSH 算是使得 ceph 实现了自我管理和自我修复。

RADOS 分布式存储相较于传统分布式存储的优势在于:  

　　1. 将文件映射到object后，利用Cluster Map 通过CRUSH 计算而不是查找表方式定位文件数据存储到存储设备的具体位置。优化了传统文件到块的映射和Block MAp的管理。  
　　2. RADOS充分利用OSD的智能特点，将部分任务授权给OSD，最大程度地实现可扩展。  
## Ceph数据分布算法 ##

在分布式存储系统中比较关注的一点是如何使得数据能够分布得更加均衡，常见的数据分布算法有一致性Hash和Ceph的Crush算法。Crush是一种伪随机的控制数据分布、复制的算法，Ceph是为大规模分布式存储而设计的，数据分布算法必须能够满足在大规模的集群下数据依然能够快速的准确的计算存放位置，同时能够在硬件故障或扩展硬件设备时做到尽可能小的数据迁移，Ceph的CRUSH算法就是精心为这些特性设计的，可以说CRUSH算法也是Ceph的核心之一。  
首先下图展示了ceph内部各单位之间的关系：
![img](https://images2017.cnblogs.com/blog/1302233/201712/1302233-20171224011812365-1637840216.png)  
ceph开发了 CRUSH（Controoled Replication Under Scalable Hashing），一种伪随机数据分布算法，它能够在层级结构的存储集群中有效的分布对象的副本。CRUSH实现了一种伪随机(确定性)的函数，它的参数 是object id或object group id，并返回一组存储设备(用于保存object副本OSD)。CRUSH需要cluster map(描述存储集群的层级结构)、和副本分布策略(rule)。  
CRUSH有两个关键优点：  
任何组件都可以独立计算出每个object所在的位置(去中心化)。  
只需要很少的元数据(cluster map)，只要当删除添加设备时，这些元数据才需要改变。  

CRUSH的目的是利用可用资源优化分配数据,当存储设备添加或删除时高效地重组数据,以及灵活地约束对象副本放置,当数据同步或者相关硬件故障的时候最 大化保证数据安全。支持各种各样的数据安全机制,包括多方复制(镜像),RAID奇偶校验方案或者其他形式的校验码,以及混合方法(比如RAID- 10)。这些特性使得CRUSH适合管理对象分布非常大的(PB级别)、要求可伸缩性,性能和可靠性非常高的存储系统。简而言之就是PG到OSD的映射过程。  

## Ceph的容错处理 ##
对于Ceph文件系统，错误分两类：一类是磁盘错误或者数据损坏（ disk error or  corruptted data）， 这类错误OSD会自己报告和处理。（self report ）； 第二类是OSD失去网络连接导致该OSD不可达（unreachable on the network）这种情况下需要主动检测（active monitor），在同一个PG组中的其它OSD会发心跳信息互相检测。 这种检测的一个优化的方法就是，当replication复制操作时，就可以顺带检测，不用发单独的消息来检测，只有一段时间没有replication 操作时，才发ping消息里检测。  

OSD的失效状态有两种：一种是down状态，这种状态下，被认为是临时错误。 在这种情况下，如果是primay，其任务由下一个replicate接手。如果该OSD没有迅速恢复（quickly recovery），那么就被标记为out状态，在这种状态下，将有新的osd加入这个PG中。  

如何标记一个OSD 从down状态 标记为out状态？由于网络分区的问题，需要通过 Ceph Monitor 来裁定。  

## Ceph 的写流程 ##
 客户端先写主副本，然后同步到两个从副本。主副本等待从副本的ack消息和apply消息。当主副本收到ack消息，说明写操作已经写在内存中完成，收到apply 消息，说明已经apply到磁盘上了。  

如果在写的过程中，主副本失效，按顺序下一个从副本接管主副本的工作，这个时候是否返回给客户端写正确？在这种情况下，客户端只是判断正常工作的 （acting）的 OSD的返回结果，只要所有正常工作的OSD返回即认为成功，虽然这时候可能只有两副本成功。同时该临时primay必须保存所有操作的recovey队 列里，如果原primay恢复，可以replay所有recovery队列里的操作，如果主副本从down到out状态，也即是永久失效，临时 primay转正，由临时primay为正式primay，只是需要加入一个新的OSD到该PG中。  

如果是从副本失效，就比较简单。临时失效，主replay所有写操作，如过永久失效，新加入一个OSD到PG中就可以了。

## 恢复 ##
当有OSD失效，恢复或者增加一个新的OSD时，导致OSD cluster map的变换。Ceph处理以上三种情况的策略是一致的。为了恢复，ceph保存了两类数据，一个是每个OSD的一个version，另一个是PG修改的 log，这个log包括PG修改的object 的名称和version。  

当一个OSD接收到cluster map的更新时：  

1）检查该OSD的所属的PG，对每个PG，通过CRUSH算法，计算出主副本的三个OSD  

2）如何该PG里的OSD发生了改变，这时候，所有的replicate向主副本发送log，也就是每个对象最后的version，当primay 决定了最后各个对象的正确的状态，并同步到所有副本上。  

3）每个OSD独立的决定，是从其它副本中恢复丢失或者过时的（missing or outdated）对象。 (如何恢复? 好像是整个对象全部拷贝，或者基于整个对象拷贝，但是用了一些类似于rsync的算法？目前还不清楚）  

4）当OSD在恢复过程中，delay所有的请求，直到恢复成功。  

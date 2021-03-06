# Google Omega #

## 背景 ##
Google的論文《Omega flexible, scalable schedulers for large compute clusters》中把調度分為3代，
第一代是獨立的集群，第二代是兩層調度（mesos,YARN）第三帶是共享狀態調度（即omega）。

## 架构 ##
>為了克服雙層調度器的以上兩個缺點，Google開發了下一代資源管理系統Omega，Omega是一種基於共享狀態的調度器,
該調度器將雙層調度器中的集中式資源調度模塊簡化成了一些持久化的共享數據（狀態）和針對這些數據的驗證代碼，
而這裡的“共享數據”實際上就是整個集群的實時資源使用信息。一旦引入共享數據後，共享數據的並發訪問方式就成為
該系統設計的核心，而Omega則採用了傳統數據庫中基於多版本的並發訪問控制方式（也稱為“樂觀鎖”, MVCC, Multi-Version Concurrency Control），
這大大提升了Omega的並發性。  
![三种系统比较](http://dongxicheng.org/wp-content/uploads/2013/04/three-types-of-schedulers.jpg "资源管理系统")

>由於Omega不再有集中式的調度模塊，因此，不能像Mesos或者YARN那樣，在一個統一模塊中完成以下功能：對整個集群中的所有資源分組，
限制每類應用程序的資源使用量，限制每個用戶的資源使用量等，這些全部由各個應用程序調度器自我管理和控制.  

>根據論文所述，Omega只是將優先級這一限制放到了共享數據的驗證代碼中，即當同時由多個應用程序申請同一份資源時，
優先級最高的那個應用程序將獲得該資源，其他資源限制全部下放到各個子調度器。 
引入多版本並發控制後，限制該機制性能的一個因素是資源訪問衝突的次數，
衝突次數越多，系統性能下降的越快，而google通過實際負載測試證明，這種方式的衝突次數是完全可以接受的。

## 优缺点 ##
优点：共享资源狀態，支持更大的集群和更高的並发。  

缺點：只有论文，无具体实现，在小集群下，沒有优势。

## 参考文章 ##
https://www.xuebuyuan.com/zh-hant/2102324.html  
http://dongxicheng.org/mapreduce-nextgen/google-omega

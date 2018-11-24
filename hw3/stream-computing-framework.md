# Stream Computing Framework

## 离线和批量、实时和流式

![批量计算和流式计算](https://upload-images.jianshu.io/upload_images/6468203-ffdc767f7d634050.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)


### 批量计算和流式计算：

图中显示了一个计算的基本流程，receiver处负责从数据源接收数据，并发送给下游的task，数据由task处理后由sink端输出。

以图为例，批量和流式处理数据粒度不一样，批量每次处理一定大小的数据块（输入一般采用文件系统），一个task处理完一个数据块之后，才将处理好的中间数据发送给下游。流式计算则是以record为单位，task在处理完一条记录之后，立马发送给下游。

假如对一些固定大小的数据做统计，那么采用批量和流式效果基本相同，但是流式有一个好处就是可以实时得到计算中的结果，这对某些应用很有帮助，比如每1分钟统计一下请求server的request次数。




## 批量和流式的区别：

+ 数据处理单位：

批量计算按数据块来处理数据，每一个task接收一定大小的数据块，比如MR，map任务在处理完一个完整的数据块后（比如128M），然后将中间数据发送给reduce任务。

流式计算的上游算子处理完一条数据后，会立马发送给下游算子，所以一条数据从进入流式系统到输出结果的时间间隔较短（当然有的流式系统为了保证吞吐，也会对数据做buffer）。

### 结论
批量计算往往得等任务全部跑完之后才能得到结果，而流式计算则可以实时获取最新的计算结果。

+ 数据源：

批量计算通常处理的是有限数据（bound data），数据源一般采用文件系统，而流式计算通常处理无限数据（unbound data），一般采用消息队列作为数据源。

+ 任务类型：

批量计算中的每个任务都是短任务，任务在处理完其负责的数据后关闭，而流式计算往往是长任务，每个work一直运行，持续接受数据源传过来的数据。


## 离线=批量？实时=流式？
习惯上认为离线和批量等价；实时和流式等价，但其实这种观点并不完全正确。

假设一种情况：如果拥有一个非常强大的硬件系统，可以毫秒级的处理Gb级别的数据，那么批量计算也可以毫秒级得到统计结果（当然这种情况非常极端，目前不可能），那它还是离线计算吗？

所以说离线和实时应该指的是：数据处理的延迟；批量和流式指的是：数据处理的方式。两者并没有必然的关系。


--------------------
## Storm
Storm做为最早的一个实时计算框架，早期应用于各大互联网公司，这里我们依然使用work count举例：
![work count](https://upload-images.jianshu.io/upload_images/6468203-6a39d56ea96ba09e.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)

spout：负责从数据源接收数据

bolt：负责数据处理，最下游的bolt负责数据输出

spout不断从数据源接收数据，然后按一定规则发送给下游的bolt进行计算，最下游的bolt将最终结果输出到外部系统中（这里假设输出到DB），这样我们在DB中就可以看到最新的数据统计结果。Storm每一层的算子都可以配置多个，这样保证的水平扩展性。因为往往处理的是unbound data，所以storm中的算子都是长任务。

+ 容灾

容灾是所有系统都需要考虑的一个问题，考虑一下：假如运行过程中，一个算子（bolt）因某种原因挂了，Storm如何恢复这个任务呢？

![容灾](https://upload-images.jianshu.io/upload_images/6468203-2dd35f5b2cc9b86c.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)

批处理解决方案就比较简单，拿MR举例，假如一个运行中map或reduce失败，那么任务重新提交一遍就ok（只不过重头计算又要花费大量时间），下面我们看看Storm是如何解决的：

> storm的spout有一个buffer，会缓存接收到的record，并且Storm还有一个acker（可以认为是一个特殊的bolt任务），每条record和该record所产生的所有tuple在处理完成后都会向对应的acker发送ack消息，当acker接收到该record所有的ack消息之后，便认为该record处理成功，并通知spout从buffer中将该record移除，若receiver没有在规定的时间内接收到ack，acker则通知spout重放数据。acker个数可以由用户指定，因为数据量比较大时，一个acker可能处理不过来所有的ack信息，成为系统瓶颈。

Storm采用ack机制实现了数据的重放，尽管做了很多优化，但是毕竟每条record和它产生的tuple都需要ack，对吞吐还是有较大的影响，关闭ack的话，对于某些不允许丢数据的业务来说又是不可接受的。

Storm的这种特点会导致大家认为：<strong>流式计算的吞吐不如批量计算</strong>。（这点其实是不对的，只能说Storm的设计导致了它的吞吐不如批量计算，一个设计优秀的流式系统是有可能拥有和批处理系统一样的吞吐）

### 数据不重不丢
早期的流式系统无法提供精准的计算服务:

![crash](https://upload-images.jianshu.io/upload_images/6468203-2f7d0236954ffb48.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)


sink处的重复输出：假如运行过程中，boltA数据入库后，boltB因为某种原因crash了，这时候会导致该record重放，boltA中已经处理过的数据会再次入库，导致部分数据重复输出。

不仅sink处存在重复输出的问题，receiver处也同样存在这种问题。

Storm没有提供exactly once的功能，并且开启ack功能后又会严重影响吞吐，所以会给大家一种印象：<strong>流式系统只适合吞吐相对较小的、低延迟不精确的计算；而精确的计算则需要由批处理系统来完成</strong>，所以出现了Lambda架构，该架构由Storm的创始人提出，简单的理解就是同时运行两个系统：一个流式，一个批量，用批量计算的精确性来弥补流式计算的不足，但是这个架构存在一个问题就是需要同时维护两套系统，代价比较大。

-------------------

## Spark streaming
### 吞吐
Spark streaming采用小批量的方式，提高了吞吐性能：

![Spark Streaming](https://upload-images.jianshu.io/upload_images/6468203-74cb9bf4435bfce2.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)


简单展示Spark streaming的运行机制，主要是与Storm做下对比。Spark streaming批量读取数据源中的数据，然后把每个batch转化成内部的RDD。Spark streaming以batch为单位进行计算，而不是以record为单位，大大减少了ack所需的开销，显著提高了吞吐。

但也因为处理数据的粒度变大，导致Spark streaming的数据延时不如Storm，Spark streaming是秒级返回结果，Storm则是毫秒级。

### 不重不丢（exactly once）
Spark streaming通过batch的方式提高了吞吐，但是同样存在上面所说的数据丢失和重复的问题。

大部分流式系统都提供了at most once和at least once功能，但不是所有系统都能提供exactly once。

我们先看看Spark streaming的at least once是如何实现的，Spark streaming的每个batch可以看做是一个Spark任务，receiver会先将数据写入WAL，保证receiver宕机时，从数据源获取的数据能够从日志中恢复，并且依赖RDD实现内部的exactly once。

>RDD：Resilient Distributed Dataset弹性分布式数据集，Spark保存着RDD之间的依赖关系，保证RDD计算失败时，可以通过上游RDD进行重新计算。

上面简单解释了Spark streaming依赖源数据写WAL和自身RDD机制提供了容灾功能，保证at least once，但是依然无法保证exactly once，在回答这个问题前，我们再来看一下，什么情况Spark streaming的数据会重复计算。

![Spark Streaming 2](https://upload-images.jianshu.io/upload_images/6468203-5b67d743b29939f9.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)


关注图中的3个红框：

Spark streaming的RDD机制只能保证内部计算exactly once，但这是不够的，回想一下刚才Storm的例子，假如某个batch中，sink处一部分数据已经入库，这时候某个sink节点宕机，导致该节点处理的数据重复输出。还有另一种情况就是receiver处重复接收数据.

![Spark Streaming 3](https://upload-images.jianshu.io/upload_images/6468203-2b5a7a13b5944610.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)

假如receiverA目前从kafka读到pos=100的记录，并且已经持久化到HDFS，但是由于网络延迟没有及时更新pos，此时receiverA宕机了，receiverB接管A的数据，并且后续的任务还会从pos=100处重新读取，导致重复消费。造成这种情况的主要原因就是：<strong>receiver处数据消费和Kafka中position的更新没有做到原子性。</strong>

根据上面的讨论，可以得出：一个流式系统如果要做到exactly once，必须满足3点：
+ receiver处保证exactly once

+ 流式系统自身保证exactly once

+ sink处保证exactly once

------

## Flink
Flink在数据处理的方式上和Storm类似，并没有采用小批量，是一个真正的流式系统。它不仅拥有了不弱于Spark streaming的吞吐，并且提供了exactly once语义。

简单来说，Flink采用轻量级分布式快照实现容错，大致流程是：Flink不断的对整个系统做snapshot，snapshot数据可以放在master上或外部系统（如HDFS），假如发生故障时，Flink停止整个数据流，并选出最近完成的snapshot，将整个数据流恢复到该snapshot那个时间点，snapshot本身比较轻量，而且用户可以自行配置snapshot的间隔，snapshot的性能开销对系统的影响很小。

![Flink 1](https://upload-images.jianshu.io/upload_images/6468203-70d043320d3461f8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)


barrier是分布式snapshot实现中一个非常核心的元素，barrier和records一起在流式系统中传输，barrier是当前snapshot和下一个snapshot的分界点，它携带了当前snapshot的id，假设目前在做snapshot N，算子在发送barrier N之前，都会对当前的状态做checkpoint，checkpoint只包含了barrier N之前的数据状态，不会涉及barrier N之后的数据。

![Flink 2](https://upload-images.jianshu.io/upload_images/6468203-886dccd9bbc56aec.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)


因为算子很多情况下需要接收多个算子的数据（shuffle操作），所以只有当所有上游的发送的barrier N都到达之后，算子才会将barrier N发送给下游（所有的下游）。当所有的sink算子都接收到barrier N之后，才会认为该snapshot N成功完成。

为了保证一致性，需要遵守以下几个原则：

1.一旦算子接收到某一个上游算子的barrier之后，它不能再处理该上游后面的数据，只有当它所有上游算子的barrier都到达，并将barrier发送给下游之后，才能继续处理数据，否则的话会造成snapshot N和N+1的数据重叠。

2.某个上游算子的barrier到达之后，该上游算子后续的数据将会被缓存在input buffer中。

3.一旦所有上游的算子的barrier都到达之后，该算子将数据和barrier发送给下游。

4.发送成功之后，该算子继续处理input buffer中的数据，并继续接收处理上游算子发送过来的数据。

![snapshot 流程](https://upload-images.jianshu.io/upload_images/6468203-38edec56a93276f8.png?imageMogr2/auto-orient/strip%7CimageView2/2/w/1000/format/webp)


图中的Master保存了snapshot的状态，假设数据还是从Kafka中获取，首先receiver算子会先将当前的position发送给master，记录在snapshot中，并同时向下游发送barrier，下游的算子接收到barrier后，发起checkpoint操作，将当前的状态记录在外部系统中，并更新Master中snapshot状态，最后当所有的sink算子都接收到barrier之后，更新snapshot中的状态，此时认为该snapshot完成。

通过这种轻量级的分布式snapshot方式，Flink实现了exactly once，同时Flink也支持at least once，也就是算子不阻塞barrier已经到达的上游算子的数据，这样可以降低延迟，但是不保证exactly once。

----

## 总结
Storm提供了低延迟的计算，但是吞吐较低，并且无法保证exactly once，Spark streaming通过小批量的方式保证了吞吐的情况下，同时提供了exactly once语义，但是实时性不如Storm。Flink采用分布式快照的方式实现了一个高吞吐、低延迟、支持exactly once的流式系统。


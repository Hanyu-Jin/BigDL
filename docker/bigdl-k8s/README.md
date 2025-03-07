BigDL bigdl-k8s image has been built to easily run applications on Kubernetes cluster. The details of pre-installed packages and usage of the image will be introduced in this page.

- [Launch pre-built bigdl-k8s image](#launch-pre-built-bigdl-k8s-image)
- [Run BigDL examples on k8s](#Run-bigdl-examples-on-k8s)

## Launch pre-built bigdl-k8s image

#### Prerequisites

1. Runnable docker environment has been set up.
2. A running Kubernetes cluster is prepared. Also make sure the permission of  `kubectl`  to create, list and delete pod.

#### Launch pre-built bigdl-k8s image

1. Pull an BigDL bigdl-k8s image from [dockerhub](https://hub.docker.com/r/intelanalytics/bigdl-k8s/tags):

```bash
sudo docker pull intelanalytics/bigdl-k8s:latest
```

- Speed up pulling image by adding mirrors

To speed up pulling the image from dockerhub in China, add a registry's mirror. For Linux OS (CentOS, Ubuntu etc), if the docker version is higher than 1.12, config the docker daemon. Edit `/etc/docker/daemon.json` and add the registry-mirrors key and value:

```bash
{
  "registry-mirrors": ["https://<my-docker-mirror-host>"]
}
```

For example, add the ustc mirror in China. 

```bash
{
  "registry-mirrors": ["https://docker.mirrors.ustc.edu.cn"]
}
```

Flush changes and restart docker：

```bash
sudo systemctl daemon-reload
sudo systemctl restart docker
```

If your docker version is between 1.8 and 1.11, find the docker configuration which location depends on the operation system. Edit and add `DOCKER_OPTS="--registry-mirror=https://<my-docker-mirror-host>"`. Restart docker `sudo service docker restart`.

If you would like to speed up pulling this image on MacOS or Windows, find the docker setting and config registry-mirrors section by specifying mirror host. Restart docker.

Then pull the image. It will be faster.

```bash
sudo docker pull intelanalytics/bigdl-k8s:latest
```

2.K8s configuration

Get k8s master as spark master :

```bash
kubectl cluster-info
```

After running this commend, it shows "Kubernetes master is running at https://127.0.0.1:12345 "

this means :

```bash
master="k8s://https://127.0.0.1:12345"
```

The namespace is default or spark.kubernetes.namespace

RBAC : 

```bash
kubectl create serviceaccount spark
kubectl create clusterrolebinding spark-role --clusterrole=edit --serviceaccount=default:spark --namespace=default
```

View k8s configuration file : 

```
.kube/config
```

or

```bash
kubectl config view --flatten --minify > kuberconfig
```

The k8s data can stored in nfs or ceph, take nfs as an example

In NFS server, run :

```bash
yum install nfs-utils
systemctl enable rpcbind
systemctl enable nfs
systemctl start rpcbind
firewall-cmd --zone=public --permanent --add-service={rpc-bind,mountd,nfs}
firewall-cmd --reload
mkdir /disk1/nfsdata
chmod 755 /disk1/nfsdata
nano /etc/exports "/disk1/nfsdata *(rw,sync,no_root_squash,no_all_squash)"
systemctl restart nfs
```

In NFS client, run :

```bash
yum install -y nfs-utils && systemctl start rpcbind && showmount -e <nfs-master-ip-address>
```

k8s conf :

```bash
git clone https://github.com/kubernetes-incubator/external-storage.git
cd /XXX/external-storage/nfs-client
nano deploy/deployment.yaml
nano deploy/rbac.yaml
kubectl create -f deploy/rbac.yaml
kubectl create -f deploy/deployment.yaml
kubectl create -f deploy/class.yaml
```

test :

```bash
kubectl create -f deploy/test-claim.yaml
kubectl create -f deploy/test-pod.yaml
kubectl get pvc
kubectl delete -f deploy/test-pod.yaml
kubectl delete -f deploy/test-claim.yaml
```

if the test is success, then run:

```bash
kubectl create -f deploy/nfs-volume-claim.yaml
```

3.Launch a k8s client container:

Please note the two different containers: **client container** is for user to submit bigdl jobs from here, since it contains all the required env and libs except hadoop/k8s configs; executor container is not need to create manually, which is scheduled by k8s at runtime.

```bash
sudo docker run -itd --net=host \
    -v /etc/kubernetes:/etc/kubernetes \
    -v /root/.kube:/root/.kube \
    intelanalytics/bigdl-k8s:latest bash
```

Note. To launch the client container, `-v /etc/kubernetes:/etc/kubernetes:` and `-v /root/.kube:/root/.kube` are required to specify the path of kube config and installation.

To specify more argument, use:

```bash
sudo docker run -itd --net=host \
    -v /etc/kubernetes:/etc/kubernetes \
    -v /root/.kube:/root/.kube \
    -e NOTEBOOK_PORT=12345 \
    -e NOTEBOOK_TOKEN="your-token" \
    -e http_proxy=http://your-proxy-host:your-proxy-port \
    -e https_proxy=https://your-proxy-host:your-proxy-port \
    -e RUNTIME_SPARK_MASTER=k8s://https://<k8s-apiserver-host>:<k8s-apiserver-port> \
    -e RUNTIME_K8S_SERVICE_ACCOUNT=account \
    -e RUNTIME_K8S_SPARK_IMAGE=intelanalytics/bigdl-k8s:latest \
    -e RUNTIME_PERSISTENT_VOLUME_CLAIM=myvolumeclaim \
    -e RUNTIME_DRIVER_HOST=x.x.x.x \
    -e RUNTIME_DRIVER_PORT=54321 \
    -e RUNTIME_EXECUTOR_INSTANCES=1 \
    -e RUNTIME_EXECUTOR_CORES=4 \
    -e RUNTIME_EXECUTOR_MEMORY=20g \
    -e RUNTIME_TOTAL_EXECUTOR_CORES=4 \
    -e RUNTIME_DRIVER_CORES=4 \
    -e RUNTIME_DRIVER_MEMORY=10g \
    intelanalytics/bigdl-k8s:latest bash 
```

- NOTEBOOK_PORT value 12345 is a user specified port number.
- NOTEBOOK_TOKEN value "your-token" is a user specified string.
- http_proxy is to specify http proxy.
- https_proxy is to specify https proxy.
- RUNTIME_SPARK_MASTER is to specify spark master, which should be `k8s://https://<k8s-apiserver-host>:<k8s-apiserver-port>` or `spark://<spark-master-host>:<spark-master-port>`. 
- RUNTIME_K8S_SERVICE_ACCOUNT is service account for driver pod. Please refer to k8s [RBAC](https://spark.apache.org/docs/latest/running-on-kubernetes.html#rbac).
- RUNTIME_K8S_SPARK_IMAGE is the k8s image.
- RUNTIME_PERSISTENT_VOLUME_CLAIM is to specify volume mount. We are supposed to use volume mount to store or receive data. Get ready with [Kubernetes Volumes](https://spark.apache.org/docs/latest/running-on-kubernetes.html#volume-mounts).
- RUNTIME_DRIVER_HOST is to specify driver localhost (only required when submit jobs as kubernetes client mode). 
- RUNTIME_DRIVER_PORT is to specify port number (only required when submit jobs as kubernetes client mode).
- Other environment variables are for spark configuration setting. The default values in this image are listed above. Replace the values as you need.

Once the container is created, launch the container by:

```bash
sudo docker exec -it <containerID> bash
```

Then you may see it shows:

```
root@[hostname]:/opt/spark/work-dir# 
```

`/opt/spark/work-dir` is the spark work path. 

Note: The `/opt` directory contains:

- download-bigdl.sh is used for downloading Analytics-Zoo distributions.
- jdk is the jdk home.
- spark is the spark home.

## Run BigDL examples on k8s

#### Launch an BigDL python example on k8s

Here is a sample for submitting the python [anomalydetection] example on cluster mode.

```bash
${SPARK_HOME}/bin/spark-submit \
  --master ${RUNTIME_SPARK_MASTER} \
  --deploy-mode cluster \
  --conf spark.kubernetes.authenticate.driver.serviceAccountName=${RUNTIME_K8S_SERVICE_ACCOUNT} \
  --name bigdl-app-k8s \
  --conf spark.kubernetes.container.image=${RUNTIME_K8S_SPARK_IMAGE} \
  --conf spark.executor.instances=${RUNTIME_EXECUTOR_INSTANCES} \
  --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.${RUNTIME_PERSISTENT_VOLUME_CLAIM}.options.claimName=${RUNTIME_PERSISTENT_VOLUME_CLAIM} \
  --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.${RUNTIME_PERSISTENT_VOLUME_CLAIM}.mount.path=/bigdl/data \
  --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.${RUNTIME_PERSISTENT_VOLUME_CLAIM}.options.claimName=${RUNTIME_PERSISTENT_VOLUME_CLAIM} \
  --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.${RUNTIME_PERSISTENT_VOLUME_CLAIM}.mount.path=/bigdl/data \
  --conf spark.kubernetes.driver.label.<your-label>=true \
  --conf spark.kubernetes.executor.label.<your-label>=true \
  --executor-cores ${RUNTIME_EXECUTOR_CORES} \
  --executor-memory ${RUNTIME_EXECUTOR_MEMORY} \
  --total-executor-cores ${RUNTIME_TOTAL_EXECUTOR_CORES} \
  --driver-cores ${RUNTIME_DRIVER_CORES} \
  --driver-memory ${RUNTIME_DRIVER_MEMORY} \
  --properties-file ${ANALYTICS_ZOO_HOME}/conf/spark-analytics-zoo.conf \
  --py-files ${ANALYTICS_ZOO_HOME}/lib/analytics-zoo-bigdl_${BIGDL_VERSION}-spark_${SPARK_VERSION}-${ANALYTICS_ZOO_VERSION}-python-api.zip,/opt/analytics-zoo-examples/python/anomalydetection/anomaly_detection.py \
  --conf spark.driver.extraJavaOptions=-Dderby.stream.error.file=/tmp \
  --conf spark.sql.catalogImplementation='in-memory' \
  --conf spark.driver.extraClassPath=${ANALYTICS_ZOO_HOME}/lib/analytics-zoo-bigdl_${BIGDL_VERSION}-spark_${SPARK_VERSION}-${ANALYTICS_ZOO_VERSION}-jar-with-dependencies.jar \
  --conf spark.executor.extraClassPath=${ANALYTICS_ZOO_HOME}/lib/analytics-zoo-bigdl_${BIGDL_VERSION}-spark_${SPARK_VERSION}-${ANALYTICS_ZOO_VERSION}-jar-with-dependencies.jar \
  file:///opt/analytics-zoo-examples/python/anomalydetection/anomaly_detection.py \
  --input_dir /bigdl/data/nyc_taxi.csv
```

Options:

- --master: the spark mater, must be a URL with the format `k8s://https://<k8s-apiserver-host>:<k8s-apiserver-port>`. 
- --deploy-mode: submit application in cluster mode.
- --name: the Spark application name.
- --conf: require to specify k8s service account, container image to use for the Spark application, driver volumes name and path, label of pods, spark driver and executor configuration, etc.
  check the argument settings in your environment and refer to the [spark configuration page](https://spark.apache.org/docs/latest/configuration.html) and [spark on k8s configuration page](https://spark.apache.org/docs/latest/running-on-kubernetes.html#configuration) for more details.
- --properties-file: the customized conf properties.
- --py-files: the extra python packages is needed.
- file://: local file path of the python example file in the client container.
- --input_dir: input data path of the anomaly detection example. The data path is the mounted filesystem of the host. Refer to more details by [Kubernetes Volumes](https://spark.apache.org/docs/latest/running-on-kubernetes.html#using-kubernetes-volumes).

See more [python examples](submit-examples-on-k8s.md) running on k8s.

#### Launch an BigDL scala example on k8s

Here is a sample for submitting the scala [anomalydetection](https://github.com/intel-analytics/analytics-zoo/tree/master/zoo/src/main/scala/com/intel/analytics/zoo/examples/anomalydetection) example on cluster mode

```bash
${SPARK_HOME}/bin/spark-submit \
  --master ${RUNTIME_SPARK_MASTER} \
  --deploy-mode cluster \
  --conf spark.kubernetes.authenticate.driver.serviceAccountName=${RUNTIME_K8S_SERVICE_ACCOUNT} \
  --name analytics-zoo \
  --conf spark.kubernetes.container.image=${RUNTIME_K8S_SPARK_IMAGE} \
  --conf spark.executor.instances=${RUNTIME_EXECUTOR_INSTANCES} \
  --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.${RUNTIME_PERSISTENT_VOLUME_CLAIM}.options.claimName=${RUNTIME_PERSISTENT_VOLUME_CLAIM} \
  --conf spark.kubernetes.driver.volumes.persistentVolumeClaim.${RUNTIME_PERSISTENT_VOLUME_CLAIM}.mount.path=/zoo \
  --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.${RUNTIME_PERSISTENT_VOLUME_CLAIM}.options.claimName=${RUNTIME_PERSISTENT_VOLUME_CLAIM} \
  --conf spark.kubernetes.executor.volumes.persistentVolumeClaim.${RUNTIME_PERSISTENT_VOLUME_CLAIM}.mount.path=/zoo \
  --conf spark.kubernetes.driver.label.<your-label>=true \
  --conf spark.kubernetes.executor.label.<your-label>=true \
  --executor-cores ${RUNTIME_EXECUTOR_CORES} \
  --executor-memory ${RUNTIME_EXECUTOR_MEMORY} \
  --total-executor-cores ${RUNTIME_TOTAL_EXECUTOR_CORES} \
  --driver-cores ${RUNTIME_DRIVER_CORES} \
  --driver-memory ${RUNTIME_DRIVER_MEMORY} \
  --properties-file ${ANALYTICS_ZOO_HOME}/conf/spark-analytics-zoo.conf \
  --py-files ${ANALYTICS_ZOO_HOME}/lib/analytics-zoo-bigdl_${BIGDL_VERSION}-spark_${SPARK_VERSION}-${ANALYTICS_ZOO_VERSION}-python-api.zip \
  --conf spark.driver.extraJavaOptions=-Dderby.stream.error.file=/tmp \
  --conf spark.sql.catalogImplementation='in-memory' \
  --conf spark.driver.extraClassPath=${ANALYTICS_ZOO_HOME}/lib/analytics-zoo-bigdl_${BIGDL_VERSION}-spark_${SPARK_VERSION}-${ANALYTICS_ZOO_VERSION}-jar-with-dependencies.jar \
  --conf spark.executor.extraClassPath=${ANALYTICS_ZOO_HOME}/lib/analytics-zoo-bigdl_${BIGDL_VERSION}-spark_${SPARK_VERSION}-${ANALYTICS_ZOO_VERSION}-jar-with-dependencies.jar \
  --class com.intel.analytics.zoo.examples.anomalydetection.AnomalyDetection \
  ${ANALYTICS_ZOO_HOME}/lib/analytics-zoo-bigdl_${BIGDL_VERSION}-spark_${SPARK_VERSION}-${ANALYTICS_ZOO_VERSION}-python-api.zip \
  --inputDir /zoo/data
```

Options:

- --master: the spark mater, must be a URL with the format `k8s://https://<k8s-apiserver-host>:<k8s-apiserver-port>`. 
- --deploy-mode: submit application in cluster mode.
- --name: the Spark application name.
- --conf: require to specify k8s service account, container image to use for the Spark application, driver volumes name and path, label of pods, spark driver and executor configuration, etc.
  check the argument settings in your environment and refer to the [spark configuration page](https://spark.apache.org/docs/latest/configuration.html) and [spark on k8s configuration page](https://spark.apache.org/docs/latest/running-on-kubernetes.html#configuration) for more details.
- --properties-file: the customized conf properties.
- --py-files: the extra python packages is needed.
- --class: scala example class name.
- --input_dir: input data path of the anomaly detection example. The data path is the mounted filesystem of the host. Refer to more details by [Kubernetes Volumes](https://spark.apache.org/docs/latest/running-on-kubernetes.html#using-kubernetes-volumes).

See more [scala examples](submit-examples-on-k8s.md) running on k8s.

#### Access logs to check result and clear pods 

When application is running, it’s possible to stream logs on the driver pod:

```bash
$ kubectl logs <spark-driver-pod>
```

To check pod status or to get some basic information around pod using:

```bash
$ kubectl describe pod <spark-driver-pod>
```

You can also check other pods using the similar way.

After finishing running the application, deleting the driver pod:

```bash
$ kubectl delete <spark-driver-pod>
```

Or clean up the entire spark application by pod label:

```bash
$ kubectl delete pod -l <pod label>
```


/*
 * Copyright 2016 The BigDL Authors.
 *
 * Licensed under the Apache License, Version 2.0 (the "License");
 * you may not use this file except in compliance with the License.
 * You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package com.intel.analytics.bigdl.ppml.fl;

public class FLHelper {
    int clientNum = 1;
    // Server property
    int serverPort = 8980;

    // Client property
    String clientTarget = "localhost:8980";
    String taskID = "taskID";
    String certChainFilePath = null;
    String privateKeyFilePath = null;

    String fgBoostServerModelPath = null;

    public void setClientNum(int clientNum) {
        this.clientNum = clientNum;
    }

    public void setServerPort(int serverPort) {
        this.serverPort = serverPort;
    }

    public void setClientTarget(String clientTarget) {
        this.clientTarget = clientTarget;
    }

    public void setTaskID(String taskID) {
        this.taskID = taskID;
    }

    public void setCertChainFilePath(String certChainFilePath) {
       this.certChainFilePath = certChainFilePath;
    }
    
    public void setPrivateKeyFilePath(String privateKeyFilePath) {
       this.privateKeyFilePath = privateKeyFilePath;
    }

    public void setFgBoostServerModelPath(String fgBoostServerModelPath) {
        this.fgBoostServerModelPath = fgBoostServerModelPath;
    }
}

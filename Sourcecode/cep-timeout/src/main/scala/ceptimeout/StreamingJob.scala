/*
 * Licensed to the Apache Software Foundation (ASF) under one
 * or more contributor license agreements.  See the NOTICE file
 * distributed with this work for additional information
 * regarding copyright ownership.  The ASF licenses this file
 * to you under the Apache License, Version 2.0 (the
 * "License"); you may not use this file except in compliance
 * with the License.  You may obtain a copy of the License at
 *
 *     http://www.apache.org/licenses/LICENSE-2.0
 *
 * Unless required by applicable law or agreed to in writing, software
 * distributed under the License is distributed on an "AS IS" BASIS,
 * WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
 * See the License for the specific language governing permissions and
 * limitations under the License.
 */

package ceptimeout

import org.apache.flink.core.fs.FileSystem
import org.apache.flink.streaming.api.scala._
import org.fiware.cosmos.orion.flink.connector.OrionSource


object StreamingJob {

  var timerMap: Map[String,Long] = Map()
  var hadNoTimeOutBefore: Map[String, Boolean] = Map()

  def timeoutWriter(sensor: String, sensorTimer: Long, currentTime: Long): String = {
    if (currentTime - sensorTimer > 10 && hadNoTimeOutBefore.getOrElse(sensor, true)){
      hadNoTimeOutBefore += (sensor -> false)
      sensor + ": timeout! please check if the sensor is still working!" + "\n"
    } else if (currentTime - sensorTimer <= 10 && !hadNoTimeOutBefore.getOrElse(sensor, true)) {
      hadNoTimeOutBefore += (sensor -> true)
      sensor + ": Sensor is working again!" + "\n"
    } else {
      ""
    }
  }
  def getTimeouts(map: Map[String, Long], time: Long): String = {
    var text: String = ""
    map foreach (x => text += timeoutWriter(x._1, x._2, time))
    text
  }

  def checkTime(sensor: String): String = {
    val currentTime: Long = System.currentTimeMillis() / 1000
    timerMap += (sensor -> currentTime)
    var message: String = getTimeouts(timerMap, currentTime)
    message = message.stripLineEnd
    message
  }

  def main(args: Array[String]) {
    // set up the streaming execution environment
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    val eventStream = env.addSource(new OrionSource(9004))

    val processedDataStream = eventStream.flatMap(event => event.entities)
      .map(entity => entity.id)
      .map(checkTime(_))

    val filteredWarningStream = processedDataStream.filter(_ != "")
    filteredWarningStream.writeAsText("/tmp/logtimeout.txt", FileSystem.WriteMode.OVERWRITE)


    // execute program
    env.execute("Socket Window NgsiEvent")
  }
}

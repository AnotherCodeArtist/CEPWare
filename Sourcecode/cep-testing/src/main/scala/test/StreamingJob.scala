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

package test

import org.apache.flink.core.fs.FileSystem
import org.apache.flink.streaming.api.scala._
import org.fiware.cosmos.orion.flink.connector.OrionSource


object StreamingJob {

  def checkTemp(tuple: (String, String)): String = {
    val time: Long = System.currentTimeMillis() / 1000
    val message: String = tuple._1 + ": " + tuple._2 + "°C at " + time.toString
    message
  }

  def main(args: Array[String]) {
    // set up the streaming execution environment
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    val eventStream = env.addSource(new OrionSource(9001))

    val processedDataStream = eventStream.flatMap(event => event.entities)
      .map(entity => (entity.id, entity.attrs("temperature").value.asInstanceOf[String]))
      .map(checkTemp(_))

    val filteredWarningStream = processedDataStream.filter(_ != "")
    filteredWarningStream.writeAsText("/tmp/logtest.txt", FileSystem.WriteMode.OVERWRITE)


    // execute program
    env.execute("Socket Window NgsiEvent")
  }
}

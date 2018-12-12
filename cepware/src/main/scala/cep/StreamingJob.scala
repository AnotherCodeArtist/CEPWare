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

package cep

import org.apache.flink.streaming.api.scala._

import org.apache.flink.streaming.api.scala.function.ProcessWindowFunction
import org.apache.flink.streaming.api.windowing.time.Time
import org.fiware.cosmos.orion.flink.connector.OrionSource
import org.apache.flink.streaming.api.windowing.windows.TimeWindow
import org.apache.flink.streaming.api.windowing.assigners.TumblingProcessingTimeWindows
import org.apache.flink.util.Collector


/**
  * When Importing the Task in Apache Flink
  * EntryClass:
  * org.apache.flink.StreamingJob
  */


object StreamingJob {

  var timerList: List[(String, Long)] = List()
  var currentTime: Long = 0
  var timeChecker: Long = 0
  var timeOuts: String = ""

  def timeoutWriter(sensor: String, sensorTimer: Long, currentTime: Long): String = {
    if (currentTime - sensorTimer > 5){
      sensor + ": timeout! please check if the sensor is still working!" + "\n"
    } else {
      ""
    }
  }
  def getTimeouts(list: List[(String, Long)], messages: String) : String = {
    list match {
      case Nil => messages
      case x :: xs => getTimeouts(xs, messages + timeoutWriter(x._1, x._2, currentTime))
    }
  }

  def main(args: Array[String]) {

    currentTime = System.currentTimeMillis() / 1000
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    val eventStream = env.addSource(new OrionSource(9001))

    if (currentTime - timeChecker > 5) {
      timeOuts = getTimeouts(timerList, "")
      timeChecker = System.currentTimeMillis() / 1000
    } else {
      timeOuts = ""
    }

    val processedDataStream = eventStream.flatMap(event => event.entities)
      .map(entity => (entity.id, entity.attrs("temperature").value.asInstanceOf[String]))
      .keyBy(_._1)
      .window(TumblingProcessingTimeWindows.of(Time.seconds(1)))
      .process(new MyProcessWindowFunction)
      .writeAsText("/tmp/log.txt")


    //processedDataStream.writeAsText("/tmp/log.txt")

    env.execute("Socket Window NgsiEvent")
  }



  class MyProcessWindowFunction extends ProcessWindowFunction[(String, String), String, String, TimeWindow] {

    override def process(key: String, context: Context, elements: Iterable[(String, String)], out: Collector[String]): Unit = {
      var message: String = ""
      val values: Iterable[Float] = elements.map(_._2.toFloat)
      val max: Float = values.max
      val min: Float = values.min

      timerList = timerList.filterNot(_._1 == key)
      timerList = (key, System.currentTimeMillis() / 1000) :: timerList

      if (max >= 60){
        message = message + message + key + ": room on fire!" + " temperature: " + max.toString + "°C" + "\n"
      }
      if (min <= 15) {
        message = message + key + ": do not forget to close the windows!" + " temperature: " + min.toString + "°C" + "\n"
      }
      if (max - min >= 3) {
        message = message + key + ": room on fire!" + " temperature is rising too fast" + "\n"
      }
      timerList = timerList

      message = message + timeOuts

      out.collect(message)
    }
  }
}
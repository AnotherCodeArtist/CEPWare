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

package org.apache.flink

import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.api.scala.{StreamExecutionEnvironment, _}
import org.apache.flink.streaming.api.windowing.time.Time
import org.fiware.cosmos.orion.flink.connector.{NgsiEvent, OrionSource}
import java.io._
import java.lang
import java.util.Calendar
import java.util.stream.Collectors._

import scala.io.Source
import org.apache.flink.api.common.functions.AggregateFunction
import org.apache.flink.api.java.tuple.Tuple
import org.apache.flink.streaming.api.functions.windowing.ProcessWindowFunction
import org.apache.flink.streaming.api.windowing.windows.TimeWindow
import org.apache.flink.util.Collector
import org.apache.flink.api.common.state.ValueState
import org.apache.flink.api.common.state.ValueStateDescriptor
import org.apache.flink.streaming.api.datastream.DataStream
import org.apache.flink.streaming.api.functions.ProcessFunction
import org.apache.flink.util.Collector

import scala.collection.TraversableOnce


/**
  * When Importing the Task in Apache Flink
  * EntryClass:
  * org.apache.flink.StreamingJob
  */

object StreamingJob {

  var timerR1: Long = 0
  var timerR2: Long = 0
  var timerR3: Long = 0
  var timerR4: Long = 0
  var timerR5: Long = 0

  def main(args: Array[String]) {

    // function to check if temperature is too hot or too cold
    def checkTemp(tuple: roomTemp): String = {
      var message: String = ""
      val currentTime = System.currentTimeMillis() / 1000

      tuple.id match {
        case "R1" => timerR1 = System.currentTimeMillis() / 1000
        case "R2" => timerR2 = System.currentTimeMillis() / 1000
        case "R3" => timerR3 = System.currentTimeMillis() / 1000
        case "R4" => timerR4 = System.currentTimeMillis() / 1000
        case "R5" => timerR5 = System.currentTimeMillis() / 1000
      }

      if (timerR1 != 0 && currentTime - timerR1 > 5){
        message = message + "R1: timeout! please check if the sensor is working!" + "\n"
      }
      if (timerR2 != 0 && currentTime - timerR2 > 5){
        message = message + "R2: timeout! please check if the sensor is working!" + "\n"
      }
      if (timerR3 != 0 && currentTime - timerR3 > 5){
        message = message + "R3: timeout! please check if the sensor is working!" + "\n"
      }
      if (timerR4 != 0 && currentTime - timerR4 > 5){
        message = message + "R4: timeout! please check if the sensor is working!" + "\n"
      }
      if (timerR5 != 0 && currentTime - timerR5 > 5){
        message = message + "R5: timeout! please check if the sensor is working!" + "\n"
      }

      if (tuple.temp.toFloat > 60f) {
        message = message + tuple.id + ": room on fire!" + " temperature: " + tuple.temp + "°C" + "\n"
      }
      if (tuple.temp.toFloat < 15f) {
        message = message + tuple.id + ": do not forget to close the windows!" + " temperature: " + tuple.temp + "°C" + "\n"
      }
      message
    }

    // set up the streaming execution environment
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    val eventStream = env.addSource(new OrionSource(9001))

    val processedDataStream = eventStream.flatMap(event => event.entities)
      .map(entity => new roomTemp(entity.id, entity.attrs("temperature").value.asInstanceOf[String]))

    val warningStream = processedDataStream.map(checkTemp(_))
    val filteredWarningStream = warningStream.filter(_ != "")


    // Writing the Results in a log.txt File
    // Attention: log.txt must not exist before the task is executed
    filteredWarningStream.writeAsText("/tmp/log.txt")

    // execute program
    env.execute("Socket Window NgsiEvent")
  }

  class roomTemp(var id: String, var temp: String) {
  }

}



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

  var timerList : List[(String,Long)] = List()
  var tempList1 : List[(String,Float)] = List()
  var tempList2 : List[(String,Float)] = List()
  var wipeTimer: Long = System.currentTimeMillis() / 1000
  var currentTime: Long = 0
  var decideList: Boolean = true

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

  def checkTemp(tuple: roomTemp): String = {
    var message: String = ""
    currentTime = System.currentTimeMillis() / 1000

    // add the current temperature to the templist
    tempList1 = (tuple.id, tuple.temp.toFloat) :: tempList1
    tempList2 = (tuple.id, tuple.temp.toFloat) :: tempList2

    // if there is already an element for the current sensor in the list, remove it
    // then add the current time for the sensor to the timerlist
    timerList = timerList.filterNot(_._1 == tuple.id)
    timerList = (tuple.id, System.currentTimeMillis() / 1000) :: timerList

    // sensor timeout if a sensor didn't send any data in 5 seconds
    message = getTimeouts(timerList, message)

    // the room is on fire if the temperature is higher than 60°C
    if (tuple.temp.toFloat > 60f) {
      message = message + tuple.id + ": room on fire!" + " temperature: " + tuple.temp + "°C" + "\n"
    }

    // close the windows if the temperature is lower than 15°C
    if (tuple.temp.toFloat < 15f) {
      message = message + tuple.id + ": do not forget to close the windows!" + " temperature: " + tuple.temp + "°C" + "\n"
    }

    // first, remove all elements that are not relevant (data of other sensors)
    // then compare the current temperature with the minimum temperature of a specific time period
    // if the current temperature is more than 3°C higher, then the temperature rose too fast and the room is on fire
    val filteredTempList1: List[Float] = tempList1.filter(_._1 == tuple.id).map(_._2)
    val filteredTempList2: List[Float] = tempList2.filter(_._1 == tuple.id).map(_._2)
    if (tuple.temp.toFloat - filteredTempList1.min > 3 || tuple.temp.toFloat - filteredTempList2.min > 3) {
      message = message + tuple.id + ": room on fire!" + " temperature is rising too fast" + "\n"
    }

    // 2 lists with temperatures that are getting cleared in rotations
    // lists:
    // |--------------|--------------|--------------|--------------|
    // |-------|--------------|--------------|--------------|-------
    // clear:
    // |-------|------|-------|------|-------|-------|------|------|
    // if every 12 seconds one list is cleared, then the minimum covered time range is 12 seconds and the maximum 24 seconds
    if (currentTime - wipeTimer > 12) {
      if (decideList) {
        tempList1 = List()
        decideList = false
      } else {
        tempList2 = List()
        decideList = true
      }
      wipeTimer = System.currentTimeMillis() / 1000
    }

    // return all warnings
    message
  }

  def main(args: Array[String]) {

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
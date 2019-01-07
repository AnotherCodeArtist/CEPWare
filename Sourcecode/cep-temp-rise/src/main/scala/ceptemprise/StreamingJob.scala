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

package ceptemprise

import org.apache.flink.core.fs.FileSystem
import org.apache.flink.streaming.api.scala._
import org.apache.flink.streaming.api.scala.function.ProcessWindowFunction
import org.apache.flink.streaming.api.windowing.assigners.SlidingProcessingTimeWindows
import org.apache.flink.streaming.api.windowing.time.Time
import org.apache.flink.streaming.api.windowing.windows.TimeWindow
import org.apache.flink.util.Collector
import org.fiware.cosmos.orion.flink.connector.OrionSource


object StreamingJob {

  var wasNotOnFireBefore: Map[String, Boolean] = Map()

  def main(args: Array[String]) {
    // set up the streaming execution environment
    val env = StreamExecutionEnvironment.getExecutionEnvironment
    val eventStream = env.addSource(new OrionSource(9003))

    val processedDataStream = eventStream.flatMap(event => event.entities)
      .map(entity => (entity.id, entity.attrs("temperature").value.asInstanceOf[String]))
      .keyBy(_._1)
      .window(SlidingProcessingTimeWindows.of(Time.seconds(20), Time.seconds(10)))
      .process(new MyProcessWindowFunction)

    val filteredWarningStream = processedDataStream.filter(_ != "")
    filteredWarningStream.writeAsText("/tmp/logtemprise.txt", FileSystem.WriteMode.OVERWRITE)

    // execute program
    env.execute("Socket Window NgsiEvent")
  }

  class MyProcessWindowFunction extends ProcessWindowFunction[(String, String), String, String, TimeWindow] {

    override def process(key: String, context: Context, elements: Iterable[(String, String)], out: Collector[String]): Unit = {
      var message: String = ""
      val temperatures: Iterable[Float] = elements.map(_._2.toFloat)

      if (temperatures.head - temperatures.last <= -3 && wasNotOnFireBefore.getOrElse(key, true)) {
        message = key + ": Room on fire! Temperature is rising too fast!"
        wasNotOnFireBefore += (key -> false)
      }
      if (temperatures.head - temperatures.last > -3 && !wasNotOnFireBefore.getOrElse(key, true)) {
        message = key + ": Room no longer on fire! Temperature is no longer rising too fast!"
        wasNotOnFireBefore += (key -> true)
      }

      if (message != "") {
        // in urlString replace INSERT_BOT_KEY with your actual bot key from Botfather and CHANNEL with your channel id
        val urlString: String = "https://api.telegram.org/botINSERT_BOT_KEY/sendMessage?chat_id=@CHANNEL&text=" + message
        scala.io.Source.fromURL(urlString)
      }

      out.collect(message)
    }
  }

}



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

package cepminmax

import org.apache.flink.core.fs.FileSystem
import org.apache.flink.streaming.api.scala._
import org.fiware.cosmos.orion.flink.connector.OrionSource


object StreamingJob {

  var temperatures: Map[String, Float] = Map();

  def checkTemp(tuple: (String, String)): String = {
    var message: String = ""
    val currTemp: Float = tuple._2.toFloat

    if ((temperatures.getOrElse(tuple._1, 0f) < 60f) && currTemp >= 60f){
      message = tuple._1 + ": Room on fire! Temperature: " + tuple._2 + "°C"
    }
    if ((temperatures.getOrElse(tuple._1, 0f) >= 60f) && currTemp < 60f && currTemp > 15){
      message = tuple._1 + ": Room no longer on fire! Temperature: " + tuple._2 + "°C"
    }

    if ((temperatures.getOrElse(tuple._1, 16f) > 15f) && currTemp <= 15f){
      message = tuple._1 + ": Room is too cold! Temperature: " + tuple._2 + "°C"
    }
    if ((temperatures.getOrElse(tuple._1, 16f) <= 15f) && currTemp > 15f && currTemp < 60){
      message = tuple._1 + ": Room is no longer too cold! Temperature: " + tuple._2 + "°C"
    }
    temperatures += (tuple._1 -> currTemp)
    message = message.stripLineEnd

    if (message != "") {
      // in urlString replace INSERT_BOT_KEY with your actual bot key from Botfather and CHANNEL with your channel id
      val urlString: String = "https://api.telegram.org/botINSERT_BOT_KEY/sendMessage?chat_id=@CHANNEL&text=" + message
      scala.io.Source.fromURL(urlString)
    }

    message
  }

  def main(args: Array[String]) {
    // set up the streaming execution environment
    val env = StreamExecutionEnvironment.getExecutionEnvironment

    val eventStream = env.addSource(new OrionSource(9002))

    val processedDataStream = eventStream.flatMap(event => event.entities)
      .map(entity => (entity.id, entity.attrs("temperature").value.asInstanceOf[String]))
      .map(checkTemp(_))

    val filteredWarningStream = processedDataStream.filter(_ != "")
    filteredWarningStream.writeAsText("/tmp/logminmax.txt", FileSystem.WriteMode.OVERWRITE)


    // execute program
    env.execute("Socket Window NgsiEvent")
  }
}

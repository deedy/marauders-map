package dom.chatserver

/*
	main chat application.
*/

import org.mashupbots.socko.events.HttpResponseStatus
import org.mashupbots.socko.events.WebSocketHandshakeEvent
import org.mashupbots.socko.infrastructure.Logger
import org.mashupbots.socko.routes._
import org.mashupbots.socko.webserver.WebServer
import org.mashupbots.socko.webserver.WebServerConfig

import akka.actor._
import akka.event.Logging
import akka.contrib.pattern._
import akka.cluster.Cluster
import akka.cluster.ClusterEvent._

object ChatApp extends Logger {

	def main(args: Array[String]) {
		// optionally set cluster address
		if (args.nonEmpty) {
			System.setProperty("akka.remote.netty.tcp.port", args(0))
		}

		// start an actor system
		val actorSystem = ActorSystem("ClusterSystem")

		// start cluster monitoring
		val clusterListener = actorSystem.actorOf(Props[ClusterListener])
		Cluster(actorSystem).subscribe(clusterListener, classOf[ClusterDomainEvent])

		// set up app routing
		val routes = Routes({
			case HttpRequest(httpRequest) => httpRequest match {
				case GET(Path("/html")) => {
					actorSystem.actorOf(Props[ChatHandler]) ! httpRequest
				}
				case Path("/favicon.ico") => {
					httpRequest.response.write(HttpResponseStatus.NOT_FOUND)
				}
			}
			case WebSocketHandshake(wsHandshake) => wsHandshake match {
				case Path("/websocket/") => {
					wsHandshake.authorize(
					onComplete = Some(onWebSocketHandshakeComplete),
					onClose = Some(onWebSocketClose))
				}
			}
			case WebSocketFrame(wsFrame) => {
				actorSystem.actorOf(Props[ChatHandler]) ! wsFrame
			}
		})

		// create a web server with our routes
		val webServer = new WebServer(WebServerConfig(), routes, actorSystem)

		// create a server actor from the webserver
		actorSystem.actorOf(Props(classOf[ClusterServer], webServer))

		Runtime.getRuntime.addShutdownHook(new Thread {
			override def run { webServer.stop() }
		})
		webServer.start()

		System.out.println("Chat server is now online at http://localhost:8888/html")
	}

	def onWebSocketHandshakeComplete(webSocketId: String) {
		System.out.println(s"Web Socket $webSocketId connected")
	}

	def onWebSocketClose(webSocketId: String) {
		System.out.println(s"Web Socket $webSocketId closed")
	}

}

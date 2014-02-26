package dom.chatserver

/*
	pub/sub wrapper for the socko webserver.
	recieves published messages from pub/sub broker
	forwards message to all local clients
*/

import akka.actor._
import akka.event.Logging
import akka.contrib.pattern._
import akka.cluster.Cluster

import org.mashupbots.socko.events.HttpResponseStatus
import org.mashupbots.socko.events.WebSocketHandshakeEvent
import org.mashupbots.socko.infrastructure.Logger
import org.mashupbots.socko.routes._
import org.mashupbots.socko.webserver.WebServer

import akka.contrib.pattern._
import DistributedPubSubMediator.{ Subscribe, SubscribeAck }

class ClusterServer (webServer : WebServer) extends Actor {

	// mediator is the pub/sub broker
	val mediator = DistributedPubSubExtension(context.system).mediator

	// subscribe to the topic named "chats"
	mediator ! Subscribe("chats", self)

	def receive = {
		// confirmation of subscription (noop)
		case SubscribeAck(Subscribe("chats", `self`)) =>

		// got chat message via pub/sub
		case ChatMessage(s) =>
			// write to all local connections
			webServer.webSocketConnections.writeText(s)
  }

}
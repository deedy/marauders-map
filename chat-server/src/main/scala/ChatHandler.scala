package dom.chatserver

/*
	Request handler for distributed chat application
	Can serve an HTML page containing a chatbox,
	Or can recieve websocket events.

	On a websocket event, will inform the pub/sub broker of the message.

	Closes after handing request.
*/

import akka.actor._
import akka.event.Logging
import akka.contrib.pattern._

import java.text.SimpleDateFormat
import java.util.GregorianCalendar

import org.mashupbots.socko.events.HttpRequestEvent
import org.mashupbots.socko.events.WebSocketFrameEvent

class ChatHandler extends Actor {
	val log = Logging(context.system, this)
	def receive = {
		case event: HttpRequestEvent =>
			writeHTML(event)
			context.stop(self)
		case event: WebSocketFrameEvent =>
			writeWebSocketResponse(event)
			context.stop(self)
		case _ => {
			log.info("received unknown message of type: ")
			context.stop(self)
		}
	}

	private def writeHTML(ctx: HttpRequestEvent) {
		// Send 100 continue if required
		if (ctx.request.is100ContinueExpected) {
			ctx.response.write100Continue()
		}
		// read chatbox HTML
		val source = scala.io.Source.fromURL(getClass.getResource("/chatbox.html"))
		val lines = source.mkString
		source.close()
		// repspond with chatbox
		ctx.response.write(lines, "text/html; charset=UTF-8")
	}

	private def writeWebSocketResponse(event: WebSocketFrameEvent) {
		import DistributedPubSubMediator.Publish
		log.info("TextWebSocketFrame: " + event.readText)

		// record time and message
		val dateFormatter = new SimpleDateFormat("HH:mm:ss")
		val time = new GregorianCalendar()
		val ts = dateFormatter.format(time.getTime())
		val retString = ts + " " + event.readText

		// publish message
		val mediator = DistributedPubSubExtension(context.system).mediator
		mediator ! Publish("chats", new ChatMessage(retString))
	}
}
